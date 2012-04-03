'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the <ORGANIZATION> nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created on Feb 8, 2011

@author: ielhelw

'''

from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import urlparse, urllib, cgi, httplib, json, pycurl, os

class HttpError(Exception): pass


class FileUploadField(object):
  def __init__(self, filename, file):
    self.filename = filename
    self.file = file


class HttpRequest(object): pass
class HttpResponse(object): pass


class HttpErrorResponse(HttpResponse):
  def __init__(self, error_message):
    self.message = error_message


class HttpJsonResponse(HttpResponse):
  def __init__(self, obj={}):
    self.obj = obj


class HttpFileDownloadResponse(HttpResponse):
  def __init__(self, filename, file):
    self.filename = filename
    self.file = file


class AbstractRequestHandler(BaseHTTPRequestHandler):
  '''Minimal HTTP request handler that uses reflection to map requested URIs
  to URI handler methods.
  
  Mapping is as follows:
    GET  /foo -> self.foo_GET
    POST /foo -> self.foo_POST
    etc.
  
  URI handler methods should accept 1 parameter; a dict containing key/value
  pairs of GET parameters.
  
  '''
  
  JSON_CONTENT_TYPES = ['application/json-rpc',
                        'application/json',
                        'application/jsonrequest']
  MULTIPART_CONTENT_TYPE = 'multipart/form-data'
  
  def handle_one_request(self):
    '''Handle a single HTTP request.
  
    You normally don't need to override this method; see the class
    __doc__ string for information on how to handle specific HTTP
    commands such as GET and POST.
  
    '''
    self.raw_requestline = self.rfile.readline()
    if not self.raw_requestline:
        self.close_connection = 1
        return
    if not self.parse_request(): # An error code has been sent, just exit
        return
    parsed_url = urlparse.urlparse(self.path)
    # we allow calls to / only
    if parsed_url.path != '/':
      self.send_error(httplib.NOT_FOUND)
      return
    
    ## if whitelist specified
    if self.server.whitelist_addresses \
    and self.client_address[0] not in self.server.whitelist_addresses:
      self.send_custom_response(httplib.FORBIDDEN)
      return
    
    # require content-type header
    if 'content-type' not in self.headers:
      self.send_error(httplib.UNSUPPORTED_MEDIA_TYPE)
      return
    
    if self.command == 'GET':
      self._handle_get(parsed_url)
    elif self.command == 'POST':
      self._handle_post()
    else:
      self.send_error(httplib.METHOD_NOT_ALLOWED)
  
  def _handle_get(self, parsed_url):
    if self.headers['content-type'] in self.JSON_CONTENT_TYPES:
      self._dispatch('GET', self._parse_jsonrpc_get_params(parsed_url))
    else:
      self.send_error(httplib.UNSUPPORTED_MEDIA_TYPE)
  
  def _handle_post(self):
    if self.headers['content-type'] in self.JSON_CONTENT_TYPES:
      self._dispatch('POST', self._parse_jsonrpc_post_params())
    elif self.headers['content-type'].startswith(self.MULTIPART_CONTENT_TYPE):
      self._dispatch('UPLOAD', self._parse_upload_params())
    else:
      self.send_error(httplib.UNSUPPORTED_MEDIA_TYPE)
  
  def _parse_jsonrpc_get_params(self, parsed_url):
    params = urlparse.parse_qs(parsed_url.query)
    # get rid of repeated params, pick the last one
    for k in params:
      if isinstance(params[k], list):
        params[k] = params[k][-1]
    if 'params' in params:
      params['params'] = json.loads(params['params'])
    return params
  
  def _parse_jsonrpc_post_params(self):
    if 'content-length' not in self.headers:
      self.send_error(httplib.LENGTH_REQUIRED)
    if not self.headers['content-length'].isdigit():
      self.send_error(httplib.BAD_REQUEST)
    tp = self.rfile.read(int(self.headers['content-length']))
    params =  json.loads(tp)
    return params
  
  def _parse_upload_params(self):
    post_data =  cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
    params = {}
    # get rid of repeated params, pick the last one
    if post_data.list:
      for k in post_data.keys():
        if isinstance(post_data[k], list): record = post_data[k][-1]
        else: record = post_data[k]
        if record.filename == None:
            params[record.name] = record.value
        else:
          params[record.name] = FileUploadField(record.filename, record.file)
    return params
  
  def _dispatch(self, callback_type, params):
    if 'method' not in params:
      self.send_method_missing(callback_type, params)
    elif params['method'] not in self.server.callback_dict[callback_type]:
      self.send_method_not_found(callback_type, params)
    else:
      callback_name = params.pop('method')
      callback_params = {}
      if callback_type != 'UPLOAD':
        if 'params' in params:
          callback_params = params['params']
        request_id = params['id']
      else:
        callback_params = params
        request_id = 1
      try:
        response = self._do_dispatch(callback_type, callback_name, callback_params)
        if isinstance(response, HttpFileDownloadResponse):
          self.send_file_response(httplib.OK, response.file, {'Content-disposition': 'attachement; filename="%s"' % (response.filename)})
        elif isinstance(response, HttpErrorResponse):
          self.send_custom_response(httplib.OK, json.dumps({'error': response.message, 'id': request_id}))
        elif isinstance(response, HttpJsonResponse):
          self.send_custom_response(httplib.OK, json.dumps({'result': response.obj, 'error': None, 'id': request_id}))
      except Exception as e:
        print e
  
  def _do_dispatch(self, callback_type, callback_name, params):
    return self.server.callback_dict[callback_type][callback_name](params)
  
  def send_custom_response(self, code, body=None):
    '''Convenience method to send a custom HTTP response.
    code: HTTP Response code.
    body: Optional HTTP response content.
    '''
    self.send_response(code)
    self.end_headers()
    if body != None:
      print >>self.wfile, body,
  
  def send_file_response(self, code, filename, headers=None):
    fd = open(filename)
    stat = os.fstat(fd.fileno())
    self.send_response(code)
    for h in headers:
      self.send_header(h, headers[h])
    self.send_header('Content-length', stat.st_size)
    self.end_headers()
    while fd.tell() != stat.st_size:
      print >>self.wfile, fd.read(),
    fd.close()
  
  def send_method_missing(self, method, params):
    self.send_custom_response(httplib.BAD_REQUEST, 'Did not specify method')
  
  def send_method_not_found(self, method, params):
    self.send_custom_response(httplib.NOT_FOUND, 'method not found')
  
  def log_message(self, format, *args):
    '''Override logging to disable it.'''
    pass


def _http_get(host, port, uri, params=None):
  try:
    buffer = StringIO()
    c = pycurl.Curl()
    if params != None:
      c.setopt(c.URL, 'http://%s:%s%s?%s' % (host, str(port), uri, urllib.urlencode(params)))
    else:
      c.setopt(c.URL, 'http://%s:%s%s' % (host, str(port), uri))
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    ret = c.getinfo(c.RESPONSE_CODE), buffer.getvalue()
    c.close()
    return ret
  except pycurl.error as e:
    raise HttpError(*e.args)

def _http_post(host, port, uri, params, files=[]):
  try:
    values = []
    for key in params:
      values.append((key, str(params[key])))
    for key in files:
      values.append((key, (pycurl.FORM_FILE, str(files[key]))))
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://%s:%s%s' % (host, str(port), uri))
    c.setopt(c.HTTPHEADER, ['Expect: '])
    c.setopt(c.HTTPPOST, values)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    ret = c.getinfo(c.RESPONSE_CODE), buffer.getvalue()
    c.close()
    return ret
  except pycurl.error as e:
    raise HttpError(*e.args)

def _jsonrpc_get(host, port, uri, method, params=None):
  try:
    buffer = StringIO()
    c = pycurl.Curl()
    curl_params = {'method': method, 'id': '1'}
    if params:
      curl_params['params'] = json.dumps(params)
    c.setopt(c.URL, 'http://%s:%s%s?%s' % (host, str(port), uri, urllib.urlencode(curl_params)))
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.perform()
    ret = c.getinfo(c.RESPONSE_CODE), buffer.getvalue()
    c.close()
    return ret
  except pycurl.error as e:
    raise HttpError(*e.args)

def _jsonrpc_post(host, port, uri, method, params={}):
  try:
    values = []
    for key in params:
      values.append((key, str(params[key])))
    response_buf = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://%s:%s%s' % (host, str(port), uri))
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, json.dumps({'method': method, 'params': params, 'id': '1'}))
    c.setopt(c.WRITEFUNCTION, response_buf.write)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.perform()
    ret = c.getinfo(c.RESPONSE_CODE), response_buf.getvalue()
    c.close()
    return ret
  except pycurl.error as e:
    raise HttpError(*e.args)


if __name__ == "__main__":
  from BaseHTTPServer import HTTPServer
  s = HTTPServer(('0.0.0.0', 6666), RequestHandlerClass=AbstractRequestHandler)
  s.serve_forever()


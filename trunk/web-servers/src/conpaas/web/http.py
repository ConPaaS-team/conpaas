'''
Created on Feb 8, 2011

@author: ielhelw
'''

from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import urlparse, urllib, cgi, httplib, json, pycurl, os

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
      self.send_error(httplib.BAD_REQUEST)
      return
    
    if self.command not in ['GET', 'POST']:
      # we only respond to GET and POST HTTP methods
      self.send_error(httplib.NOT_IMPLEMENTED)
      return
    if self.command == 'GET':
      params = urlparse.parse_qs(parsed_url.query)
      # get rid of repeated params, pick the last one
      for k in params:
        if isinstance(params[k], list):
          params[k] = params[k][-1]
    elif self.command == 'POST':
      post_data =  cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': self.command})
      params = {}
      # get rid of repeated params, pick the last one
      if post_data.list:
        for k in post_data.keys():
          if isinstance(post_data[k], list): record = post_data[k][-1]
          else: record = post_data[k]
          if record.filename == None:
              params[record.name] = record.value
          else:
            params[record.name] = {'file': record.file, 'filename': record.filename}
    self._dispatch(self.command, params)
  
  def _dispatch(self, method, params):
    if 'action' not in params:
      self.send_custom_response(httplib.BAD_REQUEST, 'Did not specify "action"')
    elif params['action'] not in self.server.callback_dict[method]:
      self.send_custom_response(httplib.NOT_FOUND, 'action not found')
    else:
      callback_name = params['action']
      del params['action']
      response = self.server.callback_dict[method][callback_name](params)
      if 'opState' in response and response['opState'] == 'DOWNLOAD':
        self.send_file_response(httplib.OK, response['file'], {'Content-disposition': 'attachement; filename="%s"' % (response['response_filename'])})
      else:
        self.send_custom_response(httplib.OK, json.dumps(response))
  
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
  
  def log_message(self, format, *args):
    '''Override logging to disable it.'''
    pass

def _http_get(host, port, uri, params=None):
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

def _http_post(host, port, uri, params, files=[]):
  values = []
  for key in params:
    values.append((key, str(params[key])))
  for key in files:
    values.append((key, (pycurl.FORM_FILE, files[key])))
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

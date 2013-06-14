#!/usr/bin/python
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
 3. Neither the name of the Contrail consortium nor the
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

Created on June, 2012

@author: aaasz

'''

"""
   This file implements the HTTPS client side for ConPaaS.
   It is used by both the agent and the manager.

   It uses the python-openssl library and standard python
   classes from httplib.

   It constucts a wrapper over the httplib.HTTPConnection
   to force it to use a SSL connection instead of a standard
   socket.

   It also provides a wrapper over OpenSSL.SSL.Connection to
   implement the missing function 'makefile', which is
   part by the python socket API and thus required to work
   with httplib.

   It implements the following methods:
       - https_get
       - https_post
       - jsonrpc_post
       - jsonrpc_get


   TODO:
   Explain the methods

"""

import socket
import mimetypes
from cStringIO import StringIO
from urllib import urlencode

from OpenSSL import SSL
from httplib import HTTPConnection

from conpaas.core.misc import file_get_contents

import json
import httplib

from . import x509

__client_ctx = None
__uid = None
__sid = None

def conpaas_init_ssl_ctx(dir, role, uid=None, sid=None):
    cert_file = dir + '/cert.pem'
    key_file = dir + '/key.pem'
    ca_cert_file = dir + '/ca_cert.pem'

    if role == 'agent':
        verify_callback = _conpaas_callback_agent
    elif role == 'manager':
        verify_callback = _conpaas_callback_manager
    elif role == 'director':
        verify_callback = _conpaas_callback_director
    elif role == 'user':
        verify_callback = _conpaas_callback_user

	if uid == None:
            # Extract uid from the certificate itself
            uid = x509.get_x509_dn_field(file_get_contents(cert_file), 'UID')

    global __client_ctx, __uid, __sid
    __client_ctx = _init_context(SSL.SSLv23_METHOD, cert_file, key_file,
                        ca_cert_file, verify_callback)
    __uid = uid
    __sid = sid

class HTTPSConnection(HTTPConnection):
    """
        This class allows communication via SSL using 
        an OpenSSL Connection.

        It is a wrapper over the httplib.HTTPConnection
        class.
    """

    def __init__(self, host, port=None, strict=None, **ssl):
        try:
            self.ssl_ctx = ssl['ssl_context']
            assert isinstance(self.ssl_ctx, SSL.Context), self.ssl_ctx
        except KeyError:
            self.ssl_ctx = SSL.Context(SSL.SSLv23_METHOD)
        HTTPConnection.__init__(self, host, port, strict)

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = SSLConnectionWrapper(self.ssl_ctx, sock)
        self.sock.connect((self.host, self.port))


class SSLConnectionWrapper(object):
    """
        Wrapper over the OpenSSL.SSL.Connection class
        to implement the makefile method to make it compatible
        with the python socket API, so we can use with httplib

        OpenSSL.SSL.Connection is not subclassable
    """
    default_buf_size = 8192
    def __init__(self, ssl_ctx, sock):
        self._ssl_conn = SSL.Connection(ssl_ctx, sock)
     
    def __getattr__(self, name):
        """
            Forward everything to underlying socket.
        """
        return getattr(self._ssl_conn, name)
    
    def makefile(self, *args):
        """
            This is the method that is missing from SSL.Connection.
            We need to provide this method, which is specific to python
            socket API as it is required by the httplib.

            This function just reads from the socket and writes to a
            StringIO object.

            @return: file object of type cStringIO.StringIO for data returned
                     from socket
        """
        _buf_size = self.__class__.default_buf_size

        fileobject = StringIO()
        try:
            buf = self._ssl_conn.recv(_buf_size)
            while buf:
                fileobject.write(buf)
                buf = self._ssl_conn.recv(_buf_size)

        except (SSL.ZeroReturnError, SSL.SysCallError):
            # Ignore the exception thrown by httplib
            # when incomplete content received
            pass

        # Start reading buffer from beginning
        fileobject.seek(0)
        return fileobject


def _init_context(protocol, cert_file, key_file, 
                 ca_cert_file, verify_callback, verify_depth=9):
    ctx=SSL.Context(protocol)
    ctx.use_privatekey_file (key_file)
    ctx.use_certificate_file(cert_file)
    ctx.load_verify_locations(ca_cert_file)
    ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_callback)

    return ctx
    
def _conpaas_callback_agent(connection, x509, errnum, errdepth, ok):
    '''
        The custom certificate verification function called on the
        agent's client side. The agent might sends requests only to
        other agents pertaining to the same user and the same
        service.
    '''

    components = x509.get_subject().get_components()
    dict = {}

    '''
        Somehow this function gets called twice: once with the CA's
        certificate and once with the peer's certificate. So first
        we rule out the CA's certificate.
    '''
    for key,value in components:
        dict[key] = value
        if key == 'CN':
            if value == 'CA':
                return ok

    if dict['role'] != 'agent':
       return False

    if dict['UID'] != __uid or dict['serviceLocator'] != __sid:
       return False
        
    return ok 

def _conpaas_callback_manager(connection, x509, errnum, errdepth, ok):
    #TODO: For all callback functions - the user certificate
    '''
        The custom certificate verification function called on the
        manager's client side. The manager might send requests only to
        its agents or the frontend.

	Note: Because of the GIT hook, the manager can be
	a client to itself (uses its own certificate to connect
	to itself).
    '''

    components = x509.get_subject().get_components()
    dict = {}

    '''
        Somehow this function gets called twice: once with the CA's
        certificate and once with the peer's certificate. So first
        we rule out the CA's certificate.
    '''
    for key,value in components:
        dict[key] = value
        if key == 'CN':
            if value == 'CA':
                return ok

    if dict['role'] == 'frontend':
        return ok

    if dict['role'] != 'agent' and dict['role'] != 'manager':
       return False

    if dict['UID'] != __uid or dict['serviceLocator'] != __sid:
       return False

    return ok

def _conpaas_callback_user(connection, x509, errnum, errdepth, ok):
    '''
        The custom certificate verification function called on the
        user's client side. The user might sends requests only to
        its managers.
    '''

    components = x509.get_subject().get_components()
    dict = {}

    '''
        Somehow this function gets called twice: once with the CA's
        certificate and once with the peer's certificate. So first
        we rule out the CA's certificate.
    '''
    for key,value in components:
        dict[key] = value
        if key == 'CN':
            if value == 'CA':
                return ok

    if dict['role'] != 'manager':
       return False

    if dict['UID'] != __uid:
       return False
        
    return ok 

def _conpaas_callback_director(connection, x509, errnum, errdepth, ok):
    '''
        The custom certificate verification function called on the
        director's client side. The director might sends requests only to
        managers.
    '''

    components = x509.get_subject().get_components()
    dict = {}
    for key,value in components:
        dict[key] = value
        if key == 'CN':
            if value == 'CA':
                return ok

    if dict['role'] != 'manager':
       return False

    return ok 

def https_get(host, port, uri, params=None):
    """Creates the VMs associated with the list of nodes. It also tests
       if the agents started correctly.

        @param host The hostname or IP address of HTTPS server

        @param post The port of the HTTPS server

        @param uri The path on the HTTPS server

        @param params (Optional) Parameters to be encoded in the url


        @return A tuple containing the return code
        and the response to the HTTP request
    """
    h = HTTPSConnection(host, port=port, ssl_context=__client_ctx)
    if params:
        h.putrequest('GET', '%s?%s' % (uri, urlencode(params)))
    else:
        h.putrequest('GET', uri)
    h.endheaders()
    r = h.getresponse()
    body = r.read()
    h.close()
    return r.status, body

def https_post(host, port, uri, params={}, files=[]):
    """
        Post params and files to an HTTPS server as multipart/form-data.
        It is received as if sending an HTML form.

        @param params A dictionary containing key:value pairs for regular
                      form fields.
        @param files A sequence of (name, filename, value) tuples for
                     data to be uploaded as files

        @return A tuple containing the return code
        and the response to the HTTP request
    """
    content_type, body = _encode_multipart_formdata(params, files)
    h = HTTPSConnection(host, port=port, ssl_context=__client_ctx)
    h.putrequest('POST', uri)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    r = h.getresponse()
    body = r.read()
    h.close()
    return r.status, body

def _encode_multipart_formdata(params, files):
    """
        @param params A dictionary containing key:value pairs
                      for regular form fields.
      
        @param files A sequence of (name, filename, value) tuples for
                     data to be uploaded as files.

        @return A tuple, (content_type, body), ready for
                httplib.HTTP instance
    """
    '''
        TODO: For some reason we receive the filename in
        unicode and the CRLF.join(L) crashes.
        To solve this, I converted the filename to ascii.
    '''
    BOUNDARY = '----------_BoUnDaRy_StRiNg_$'
    CRLF = '\r\n'
    L = []
    for key in params:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(str(params[key]))
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' \
                % (key, filename.encode('ascii')))
        L.append('Content-Type: %s' % _get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def jsonrpc_get(host, port, uri, method, params=None):
    """
        HTTPS GET request as application/json.

        @param method The name of the function to which this request is
                      mapped on the server side (the method that will be
                      called on the server)
        @param params A dictionary containing key:value pairs for regular
                      form fields.

        @return A tuple containing the return code
        and the response to the HTTP request
    """
    h = HTTPSConnection(host, port=port, ssl_context=__client_ctx)
    all_params = {'method': method, 'id': '1'}
    if params:
        all_params['params'] = json.dumps(params)
    h.putrequest('GET', '%s?%s' % (uri, urlencode(all_params)))
    h.putheader('content-type', 'application/json')
    h.endheaders()
    r = h.getresponse()
    body = r.read()
    h.close()
    return r.status, body 

def jsonrpc_post(host, port, uri, method, params={}):
    """
        Post params to an HTTPS server as application/json.

        @param method The name of the function to which this request is
                      mapped on the server side (the method that will be
                      called on the server)
        @param params A dictionary containing key:value pairs for regular
                      form fields.

        @return A tuple containing the return code
        and the response to the HTTP request
    """
    body = json.dumps({'method': method, 'params': params, 'id': '1'})
    h = HTTPSConnection(host, port=port, ssl_context=__client_ctx)
    h.putrequest('POST', uri)
    h.putheader('content-type', 'application/json')
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    r = h.getresponse()
    body = r.read()
    h.close()
    return r.status, body

def check_response(response):
    """Check the given HTTP response, returning the result if everything went
    fine"""
    code, body = response
    if code != httplib.OK: 
        raise Exception('Received http response code %d' % (code))

    data = json.loads(body)
    if data['error']: 
        raise Exception(data['error'])
    
    return data['result']

if __name__ == "__main__":
    conpaas_init_ssl_ctx('/etc/conpaas-security/certs', 'manager')
    print https_post('testbed2.conpaas.eu', 443, 
            '/security/callback/decrementUserCredit.php', params={'sid': 454, 'decrement': 1})
    #print https_get('testbed2.conpaas.eu', 443, '/')
    #print r.status
    #print r.reason
    #print r.read()
    #r = jsonrpc_get('192.168.122.149', 5555, '/', 'check_agent_process')
    #print r
    #r = jsonrpc_post('testbed2.conpaas.eu', 9999, '/','method')
    #print r

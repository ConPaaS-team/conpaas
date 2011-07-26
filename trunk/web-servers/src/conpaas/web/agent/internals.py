'''
Created on Mar 7, 2011

@author: ielhelw
'''

from os.path import exists, join
from os import remove
from shutil import rmtree
from threading import Lock
import pickle, zipfile, tarfile

from conpaas.log import create_logger
from conpaas.web.agent.role import NginxProxy, PHPProcessManager, NginxPHP,\
                                   NginxTomcat, Tomcat6
from conpaas.web.http import HttpErrorResponse, HttpJsonResponse, FileUploadField

WebServer = NginxPHP
HttpProxy = NginxProxy

logger = create_logger(__name__)
exposed_functions = {}

E_CONFIG_NOT_EXIST = 0
E_CONFIG_EXISTS = 1
E_CONFIG_READ_FAILED = 2
E_CONFIG_CORRUPT = 3
E_CONFIG_COMMIT_FAILED = 4
E_ARGS_INVALID = 5
E_ARGS_UNEXPECTED = 6
E_ARGS_MISSING = 7
E_UNKNOWN = 8

E_STRINGS = [
  'No configuration exists',
  'Configuration already exists',
  'Failed to read configuration state of %s from %s', # 2 params
  'Configuration is corrupted',
  'Failed to commit configuration',
  'Invalid arguments',
  'Unexpected arguments %s', # 1 param (a list)
  'Missing argument "%s"', # 1 param
  'Unknown error',
]


class AgentException(Exception):
  def __init__(self, code, *args, **kwargs):
    self.code = code
    self.args = args
    if 'detail' in kwargs:
      self.message = '%s DETAIL:%s' % ( (E_STRINGS[code] % args), str(kwargs['detail']) )
    else:
      self.message = E_STRINGS[code] % args


def expose(http_method):
  def decorator(func):
    if http_method not in exposed_functions:
      exposed_functions[http_method] = {}
    exposed_functions[http_method][func.__name__] = func
    def wrapped(*args, **kwargs):
      return func(*args, **kwargs)
    return wrapped
  return decorator

#def check_nofiles(kwargs, exceptfor=[]):
#  for key in kwargs:
#    if isinstance(kwargs[key], dict) and key not in exceptfor:
#      raise AgentException(E_ARGS_UNEXPECTED, [key], detail='Not expecting a file in "%s"' % key)

def _get(get_params, class_file, pClass):
  if not exists(class_file):
    return HttpErrorResponse(AgentException(E_CONFIG_NOT_EXIST).message)
  try:
    fd = open(class_file, 'r')
    p = pickle.load(fd)
    fd.close()
  except Exception as e:
    ex = AgentException(E_CONFIG_READ_FAILED, pClass.__name__, class_file, detail=e)
    logger.exception(ex.message)
    return HttpErrorResponse(ex.message)
  else:
    return HttpJsonResponse({'return': p.status()})

def _create(post_params, class_file, pClass):
  if exists(class_file):
    return HttpErrorResponse(AgentException(E_CONFIG_EXISTS).message)
  try:
    if type(post_params) != dict: raise TypeError()
    p = pClass(**post_params)
  except (ValueError, TypeError) as e:
    ex = AgentException(E_ARGS_INVALID, detail=str(e))
    return HttpErrorResponse(ex.message)
  except Exception as e:
    ex = AgentException(E_UNKNOWN, detail=e)
    logger.exception(e)
    return HttpErrorResponse(ex.message)
  else:
    try:
      fd = open(class_file, 'w')
      pickle.dump(p, fd)
      fd.close()
    except Exception as e:
      ex = AgentException(E_CONFIG_COMMIT_FAILED, detail=e)
      logger.exception(ex.message)
      return HttpErrorResponse(ex.message)
    else:
      return HttpJsonResponse()

def _update(post_params, class_file, pClass):
  try:
    if type(post_params) != dict: raise TypeError()
    fd = open(class_file, 'r')
    p = pickle.load(fd)
    fd.close()
    p.configure(**post_params)
    p.restart()
  except (ValueError, TypeError) as e:
    ex = AgentException(E_ARGS_INVALID)
    return HttpErrorResponse(ex.message)
  except Exception as e:
    ex = AgentException(E_UNKNOWN, detail=e)
    logger.exception(e)
    return HttpErrorResponse(ex.message)
  else:
    try:
      fd = open(class_file, 'w')
      pickle.dump(p, fd)
      fd.close()
    except Exception as e:
      ex = AgentException(E_CONFIG_COMMIT_FAILED, detail=e)
      logger.exception(ex.message)
      return HttpErrorResponse(ex.message)
    else:
      return HttpJsonResponse()

def _stop(get_params, class_file, pClass):
  if not exists(class_file):
    return HttpErrorResponse(AgentException(E_CONFIG_NOT_EXIST).message)
  try:
    try:
      fd = open(class_file, 'r')
      p = pickle.load(fd)
      fd.close()
    except Exception as e:
      ex = AgentException(E_CONFIG_READ_FAILED, detail=e)
      logger.exception(ex.message)
      return HttpErrorResponse(ex.message)
    p.stop()
    remove(class_file)
    return HttpJsonResponse()
  except Exception as e:
    ex = AgentException(E_UNKNOWN, detail=e)
    logger.exception(e)
    return HttpErrorResponse(ex.message)


webserver_file = '/tmp/webserverfile'

web_lock = Lock()

def _webserver_get_params(kwargs):
  ret = {}
  
  if 'doc_root' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'doc_root')
  ret['doc_root'] = kwargs.pop('doc_root')
  
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not isinstance(kwargs['port'], int):
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  
  if 'codeVersion' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  ret['codeVersion'] = kwargs.pop('codeVersion')
  
  if 'prevCodeVersion' in kwargs:
    ret['prevCodeVersion'] = kwargs.pop('prevCodeVersion')
  if 'backends' in kwargs:
    ret['php'] = kwargs.pop('backends')
  
  if len(kwargs) != 0:
    raise AgentException(E_ARGS_UNEXPECTED, kwargs.keys())
  return ret

@expose('GET')
def getWebServerState(kwargs):
  """GET state of WebServer"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with web_lock:
    return _get(kwargs, webserver_file, WebServer)

@expose('POST')
def createWebServer(kwargs):
  """Create the WebServer"""
  try: kwargs = _webserver_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with web_lock:
      return _create(kwargs, webserver_file, WebServer)

@expose('POST')
def updateWebServer(kwargs):
  """UPDATE the WebServer"""
  try: kwargs = _webserver_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with web_lock:
      return _update(kwargs, webserver_file, WebServer)

@expose('POST')
def stopWebServer(kwargs):
  """KILL the WebServer"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with web_lock:
    return _stop(kwargs, webserver_file, WebServer)


webservertomcat_file = '/tmp/webservertomcatfile'

webservertomcat_lock = Lock()

def _tomcatwebserver_get_params(kwargs):
  ret = {}
  
  if 'doc_root' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'doc_root')
  ret['doc_root'] = kwargs.pop('doc_root')
  
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not isinstance(kwargs['port'], int):
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  
  if 'backends' in kwargs:
    ret['php'] = kwargs.pop('backends')
  
  if 'codeCurrent' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'codeCurrent')
  ret['codeCurrent'] = kwargs.pop('codeCurrent')
  ret['servletsCurrent'] = kwargs.pop('servletsCurrent')
  
  if 'codeOld' in kwargs:
    ret['codeOld'] = kwargs.pop('codeOld')
    ret['servletsOld'] = kwargs.pop('servletsOld')
  
  if len(kwargs) != 0:
    raise AgentException(E_ARGS_UNEXPECTED, kwargs.keys())
  return ret

@expose('GET')
def getTomcatWebServerState(kwargs):
  """GET state of NginxTomcat"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with webservertomcat_lock:
    return _get(kwargs, webservertomcat_file, NginxTomcat)

@expose('POST')
def createTomcatWebServer(kwargs):
  """Create the NginxTomcat"""
  try: kwargs = _tomcatwebserver_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with webservertomcat_lock:
      return _create(kwargs, webservertomcat_file, NginxTomcat)

@expose('POST')
def updateTomcatWebServer(kwargs):
  """UPDATE the NginxTomcat"""
  try: kwargs = _tomcatwebserver_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with webservertomcat_lock:
      return _update(kwargs, webservertomcat_file, NginxTomcat)

@expose('POST')
def stopTomcatWebServer(kwargs):
  """KILL the NginxTomcat"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with webservertomcat_lock:
    return _stop(kwargs, webservertomcat_file, NginxTomcat)


httpproxy_file = '/tmp/httpproxyfile'

httpproxy_lock = Lock()

def _httpproxy_get_params(kwargs):
  ret = {}
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not isinstance(kwargs['port'], int):
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  
  if 'backends' in kwargs:
    backends = kwargs.pop('backends')
  else:
    backends = []
  if len(backends) == 0:
    raise AgentException(E_ARGS_INVALID, detail='At least one backend is required')
  ret['backends'] = backends
  
  if 'codeversion' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'codeversion')
  ret['codeversion'] = kwargs.pop('codeversion')
  
  if len(kwargs) != 0:
    raise AgentException(E_ARGS_UNEXPECTED, kwargs.keys())
  return ret

@expose('GET')
def getHttpProxyState(kwargs):
  """GET state of HttpProxy"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with httpproxy_lock:
    return _get(kwargs, httpproxy_file, HttpProxy)

@expose('POST')
def createHttpProxy(kwargs):
  """Create the HttpProxy"""
  try: kwargs = _httpproxy_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with httpproxy_lock:
      return _create(kwargs, httpproxy_file, HttpProxy)

@expose('POST')
def updateHttpProxy(kwargs):
  """UPDATE the HttpProxy"""
  try: kwargs = _httpproxy_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with httpproxy_lock:
      return _update(kwargs, httpproxy_file, HttpProxy)

@expose('POST')
def stopHttpProxy(kwargs):
  """KILL the HttpProxy"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with httpproxy_lock:
    return _stop(kwargs, httpproxy_file, HttpProxy)

php_file = '/tmp/phpfile'

php_lock = Lock()

def _php_get_params(kwargs):
  ret = {}
  
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not isinstance(kwargs['port'], int):
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  if 'scalaris' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'scalaris')
  ret['scalaris'] = kwargs.pop('scalaris')
  ret['configuration'] = kwargs.pop('configuration')
  
  if len(kwargs) != 0:
    raise AgentException(E_ARGS_UNEXPECTED, kwargs.keys())
  return ret

@expose('GET')
def getPHPState(kwargs):
  """GET state of PHPProcessManager"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with php_lock:
    return _get(kwargs, php_file, PHPProcessManager)

@expose('POST')
def createPHP(kwargs):
  """Create the PHPProcessManager"""
  try: kwargs = _php_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with php_lock:
      return _create(kwargs, php_file, PHPProcessManager)

@expose('POST')
def updatePHP(kwargs):
  """UPDATE the PHPProcessManager"""
  try: kwargs = _php_get_params(kwargs)
  except AgentException as e:
    return HttpErrorResponse(e.message)
  else:
    with php_lock:
      return _update(kwargs, php_file, PHPProcessManager)

@expose('POST')
def stopPHP(kwargs):
  """KILL the PHPProcessManager"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with php_lock:
    return _stop(kwargs, php_file, PHPProcessManager)

@expose('UPLOAD')
def updatePHPCode(kwargs):
  if 'file' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  file = kwargs.pop('file')
  
  if 'filetype' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  filetype = kwargs.pop('filetype')
  
  if 'codeVersionId' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  codeVersionId = kwargs.pop('codeVersionId')
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  if not isinstance(file, FileUploadField):
    return HttpErrorResponse(AgentException(E_ARGS_INVALID, detail='"file" should be a file').message)
  
  if filetype == 'zip': source = zipfile.ZipFile(file.file, 'r')
  elif filetype == 'tar': source = tarfile.open(fileobj=file.file)
  else: return HttpErrorResponse('Unknown archive type ' + str(filetype))
  
  target_dir = join('/var/www/', codeVersionId)
  if exists(target_dir):
    rmtree(target_dir)
  source.extractall(target_dir)
  return HttpJsonResponse()

tomcat_file = '/tmp/tomcat'
tomcat_lock = Lock()

@expose('GET')
def getTomcatState(kwargs):
  """GET state of Tomcat6"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with tomcat_lock:
    return _get(kwargs, tomcat_file, Tomcat6)

@expose('POST')
def createTomcat(kwargs):
  """Create Tomcat6"""
  ret = {}
  if 'tomcat_port' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_MISSING, 'tomcat_port').message)
  ret['tomcat_port'] = kwargs.pop('tomcat_port')
  
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  
  with tomcat_lock:
    return _create(ret, tomcat_file, Tomcat6)

@expose('POST')
def stopTomcat(kwargs):
  """KILL Tomcat6"""
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  with tomcat_lock:
    return _stop(kwargs, tomcat_file, Tomcat6)

@expose('UPLOAD')
def updateTomcatCode(kwargs):
  if 'file' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  file = kwargs.pop('file')
  
  if 'filetype' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  filetype = kwargs.pop('filetype')
  
  if 'codeVersionId' not in kwargs:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  codeVersionId = kwargs.pop('codeVersionId')
  if len(kwargs) != 0:
    return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message)
  if not isinstance(file, FileUploadField):
    return HttpErrorResponse(AgentException(E_ARGS_INVALID, detail='"file" should be a file').message)
  
  if filetype == 'zip': source = zipfile.ZipFile(file.file, 'r')
  elif filetype == 'tar': source = tarfile.open(fileobj=file.file)
  else: return HttpErrorResponse('Unsupported archive type ' + str(filetype))
  
  target_dir = join('/conpaas/tomcat-6/webapps/', codeVersionId)
  if exists(target_dir):
    rmtree(target_dir)
  source.extractall(target_dir)
  return HttpJsonResponse()

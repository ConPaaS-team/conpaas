'''
Created on Mar 7, 2011

@author: ielhelw
'''

from os.path import exists, join
from os import remove
from shutil import rmtree
from threading import Lock
import pickle, mimetypes, zipfile, tarfile

from conpaas.log import create_logger
from conpaas.web.agent.role import NginxProxy, PHPProcessManager, Nginx

WebServer = Nginx
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

def check_nofiles(kwargs, exceptfor=[]):
  for key in kwargs:
    if isinstance(kwargs[key], dict) and key not in exceptfor:
      raise AgentException(E_ARGS_UNEXPECTED, [key], detail='Not expecting a file in "%s"' % key)

def _get(get_params, class_file, pClass):
  if not exists(class_file):
    return {'opState': 'ERROR', 'error': AgentException(E_CONFIG_NOT_EXIST).message}
  try:
    fd = open(class_file, 'r')
    p = pickle.load(fd)
    fd.close()
  except Exception as e:
    ex = AgentException(E_CONFIG_READ_FAILED, pClass.__name__, class_file, detail=e)
    logger.exception(ex.message)
    return {'opState': 'ERROR', 'error': ex.message}
  else:
    return {'opState': 'OK', 'return': p.status()}

def _create(post_params, class_file, pClass):
  if exists(class_file):
    return {'opState': 'ERROR', 'error': AgentException(E_CONFIG_EXISTS).message}
  try:
    if type(post_params) != dict: raise TypeError()
    p = pClass(**post_params)
  except (ValueError, TypeError) as e:
    ex = AgentException(E_ARGS_INVALID, detail=str(e))
    return {'opState': 'ERROR', 'error': ex.message}
  except Exception as e:
    ex = AgentException(E_UNKNOWN, detail=e)
    logger.exception(e)
    return {'opState': 'ERROR', 'error': ex.message}
  else:
    try:
      fd = open(class_file, 'w')
      pickle.dump(p, fd)
      fd.close()
    except Exception as e:
      ex = AgentException(E_CONFIG_COMMIT_FAILED, detail=e)
      logger.exception(ex.message)
      return {'opState': 'ERROR', 'error': ex.message}
    else:
      return {'opState': 'OK'}

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
    return {'opState': 'ERROR', 'error': ex.message}
  except Exception as e:
    ex = AgentException(E_UNKNOWN, detail=e)
    logger.exception(e)
    return {'opState': 'ERROR', 'error': ex.message}
  else:
    try:
      fd = open(class_file, 'w')
      pickle.dump(p, fd)
      fd.close()
    except Exception as e:
      ex = AgentException(E_CONFIG_COMMIT_FAILED, detail=e)
      logger.exception(ex.message)
      return {'opState': 'ERROR', 'error': ex.message}
    else:
      return {'opState': 'OK'}

def _stop(get_params, class_file, pClass):
  if not exists(class_file):
    return {'opState': 'ERROR', 'error': AgentException(E_CONFIG_NOT_EXIST).message}
  try:
    try:
      fd = open(class_file, 'r')
      p = pickle.load(fd)
      fd.close()
    except Exception as e:
      ex = AgentException(E_CONFIG_READ_FAILED, detail=e)
      logger.exception(ex.message)
      return {'opState': 'ERROR', 'error': ex.message}
    p.stop()
    remove(class_file)
    return {'opState': 'OK'}
  except Exception as e:
    ex = AgentException(E_UNKNOWN, detail=e)
    logger.exception(e)
    return {'opState': 'ERROR', 'error': ex.message}


webserver_file = '/tmp/webserverfile'

web_lock = Lock()

def _webserver_get_params(kwargs):
  check_nofiles(kwargs)
  ret = {}
  
  if 'doc_root' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'doc_root')
  ret['doc_root'] = kwargs.pop('doc_root')
  
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not kwargs['port'].isdigit():
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  
  php = []
  i = 0
  while 'php.%d.ip' % (i) in kwargs and 'php.%d.port' % (i) in kwargs:
    ip = kwargs.pop('php.%d.ip' % i)
    port = kwargs.pop('php.%d.port' % i)
    if not port.isdigit():
      raise AgentException(E_ARGS_INVALID, detail='Invalid "php.%d.port" value' % i)
    php.append([ip, int(port)])
    i += 1
  ret['php'] = php
  
  if len(kwargs) != 0:
    raise AgentException(E_ARGS_UNEXPECTED, kwargs.keys())
  return ret

@expose('GET')
def getWebServerState(kwargs):
  """GET state of WebServer"""
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  with web_lock:
    return _get(kwargs, webserver_file, WebServer)

@expose('POST')
def createWebServer(kwargs):
  """Create the WebServer"""
  try: kwargs = _webserver_get_params(kwargs)
  except AgentException as e:
    return {'opState': 'ERROR', 'error': e.message}
  else:
    with web_lock:
      return _create(kwargs, webserver_file, WebServer)

@expose('POST')
def updateWebServer(kwargs):
  """UPDATE the WebServer"""
  try: kwargs = _webserver_get_params(kwargs)
  except AgentException as e:
    return {'opState': 'ERROR', 'error': e.message}
  else:
    with web_lock:
      return _update(kwargs, webserver_file, WebServer)

@expose('POST')
def stopWebServer(kwargs):
  """KILL the WebServer"""
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  with web_lock:
    return _stop(kwargs, webserver_file, WebServer)


httpproxy_file = '/tmp/httpproxyfile'

httpproxy_lock = Lock()

def _httpproxy_get_params(kwargs):
  check_nofiles(kwargs)
  ret = {}
  
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not kwargs['port'].isdigit():
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  
  backends = []
  i = 0
  while 'backends.%d.ip' % (i) in kwargs and 'backends.%d.port' % (i) in kwargs:
    ip = kwargs.pop('backends.%d.ip' % i)
    port = kwargs.pop('backends.%d.port' % i)
    if not port.isdigit():
      raise AgentException(E_ARGS_INVALID, detail='Invalid "backends.%d.port" value' % i)
    backends.append([ip, int(port)])
    i += 1
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
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  with httpproxy_lock:
    return _get(kwargs, httpproxy_file, HttpProxy)

@expose('POST')
def createHttpProxy(kwargs):
  """Create the HttpProxy"""
  try: kwargs = _httpproxy_get_params(kwargs)
  except AgentException as e:
    return {'opState': 'ERROR', 'error': e.message}
  else:
    with httpproxy_lock:
      return _create(kwargs, httpproxy_file, HttpProxy)

@expose('POST')
def updateHttpProxy(kwargs):
  """UPDATE the HttpProxy"""
  try: kwargs = _httpproxy_get_params(kwargs)
  except AgentException as e:
    return {'opState': 'ERROR', 'error': e.message}
  else:
    with httpproxy_lock:
      return _update(kwargs, httpproxy_file, HttpProxy)

@expose('POST')
def stopHttpProxy(kwargs):
  """KILL the HttpProxy"""
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  with httpproxy_lock:
    return _stop(kwargs, httpproxy_file, HttpProxy)

php_file = '/tmp/phpfile'

php_lock = Lock()

def _php_get_params(kwargs):
  check_nofiles(kwargs)
  ret = {}
  
  if 'port' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'port')
  if not kwargs['port'].isdigit():
    raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
  ret['port'] = int(kwargs.pop('port'))
  if 'scalaris' not in kwargs:
    raise AgentException(E_ARGS_MISSING, 'scalaris')
  ret['scalaris'] = kwargs.pop('scalaris')
  configuration = {}
  i = 0
  while 'configuration.%d.key' % (i) in kwargs and 'configuration.%d.value' % (i) in kwargs:
    key = kwargs.pop('configuration.%d.key' % i)
    value = kwargs.pop('configuration.%d.value' % i)
    configuration[key] = value
    i += 1
  ret['configuration'] = configuration
  
  if len(kwargs) != 0:
    raise AgentException(E_ARGS_UNEXPECTED, kwargs.keys())
  return ret

@expose('GET')
def getPHPState(kwargs):
  """GET state of PHPProcessManager"""
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  with php_lock:
    return _get(kwargs, php_file, PHPProcessManager)

@expose('POST')
def createPHP(kwargs):
  """Create the PHPProcessManager"""
  try: kwargs = _php_get_params(kwargs)
  except AgentException as e:
    return {'opState': 'ERROR', 'error': e.message}
  else:
    with php_lock:
      return _create(kwargs, php_file, PHPProcessManager)

@expose('POST')
def updatePHP(kwargs):
  """UPDATE the PHPProcessManager"""
  try: kwargs = _php_get_params(kwargs)
  except AgentException as e:
    return {'opState': 'ERROR', 'error': e.message}
  else:
    with php_lock:
      return _update(kwargs, php_file, PHPProcessManager)

@expose('POST')
def stopPHP(kwargs):
  """KILL the PHPProcessManager"""
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  with php_lock:
    return _stop(kwargs, php_file, PHPProcessManager)

@expose('POST')
def updateCode(kwargs):
  if 'file' not in kwargs:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  file = kwargs.pop('file')
  
  if 'filetype' not in kwargs:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  filetype = kwargs.pop('filetype')
  
  if 'codeVersionId' not in kwargs:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  codeVersionId = kwargs.pop('codeVersionId')
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  if not isinstance(file, dict):
    return {'opState': 'ERROR', 'error': AgentException(E_ARGS_INVALID, detail='"file" should be a file').message}
  
  if filetype == 'zip': source = zipfile.ZipFile(file['file'], 'r')
  elif filetype == 'tar': source = tarfile.open(fileobj=file['file'])
  else: return {'opState': 'error', 'ERROR': 'Unknown archive type ' + str(filetype)}
  
  target_dir = join('/var/www/', codeVersionId)
  if exists(target_dir):
    rmtree(target_dir)
  source.extractall(target_dir)
  return {'opState': 'OK'}

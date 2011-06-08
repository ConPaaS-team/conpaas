'''
Created on Jun 7, 2011

@author: ales
'''

S_INIT = 'INIT'
S_PROLOGUE = 'PROLOGUE'
S_RUNNING = 'RUNNING'
S_ADAPTING = 'ADAPTING'
S_EPILOGUE = 'EPILOGUE'
S_STOPPED = 'STOPPED'
S_ERROR = 'ERROR'

E_ARGS_UNEXPECTED = 0
E_CONFIG_NOT_EXIST = 1
E_CONFIG_READ_FAILED = 2
E_CONFIG_EXISTS = 3
E_ARGS_INVALID = 4
E_UNKNOWN = 5
E_CONFIG_COMMIT_FAILED = 6
E_ARGS_MISSING = 7
E_ARGS_INVALID = 8
E_IAAS_REQUEST_FAILED = 9
E_STATE_ERROR = 10
E_CODE_VERSION_ERROR = 11

E_STRINGS = [  
  'Unexpected arguments %s', # 1 param (a list)
  'No configuration exists',
  'Failed to read configuration state of %s from %s', # 2 params
  'Configuration file already exists',
  'Invalid arguments',
  'Unknown error',
  'Failed to commit configuration',
  'Missing argument: %s',
  'Invalid arguments',
  'Failed to request resources from IAAS',
  'Cannot perform requested operation in current state',
  'No code version selected',  
]

memcache = None
dstate = None
exposed_functions = {}
config = None

class ManagerException(Exception):
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

@expose('GET')
def listServiceNodes(kwargs):
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
    #dstate = memcache.get(DEPLOYMENT_STATE)    
    if dstate != S_RUNNING and dstate != S_ADAPTING:
        return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
    
    #config = memcache.get(CONFIG)
    return {
          'opState': 'OK',
          'sql': [ serviceNode.vmid for serviceNode in config.getMySQLNodes() ],
          }
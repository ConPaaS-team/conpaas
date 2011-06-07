from threading import Lock
from string import Template
from os import kill, makedirs
from os.path import join, devnull, exists
from subprocess import Popen

from conpaas.log import create_logger
from conpaas.web.misc import verify_port
from signal import SIGHUP, SIGINT

import pickle

exposed_functions = {}

E_ARGS_UNEXPECTED = 0
E_CONFIG_NOT_EXIST = 1
E_CONFIG_READ_FAILED = 2
E_CONFIG_EXISTS = 3
E_ARGS_INVALID = 4
E_UNKNOWN = 5
E_CONFIG_COMMIT_FAILED = 6
E_ARGS_MISSING = 7

E_STRINGS = [  
  'Unexpected arguments %s', # 1 param (a list)
  'No configuration exists',
  'Failed to read configuration state of %s from %s', # 2 params
  'Configuration file already exists',
  'Invalid arguments',
  'Unknown error',
  'Failed to commit configuration',
  'Missing argument: %s'
]

web_lock = Lock()
logger = create_logger(__name__)
mysql_file = "/tmp/conpaassql" 

S_PREFIX    = "/tmp/"
S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'
S_MYSQL_HOME  = S_PREFIX.join('conpaas/conf/mysql')

class MySQLServerConfiguration:
    
    def __init__(self):
        '''Holds the configuration of the server.
        '''
        self.port=3308
        self.pid_file='/var/lib/mysql/temp.pid'
        self.bind_address='127.0.0.1'
        
class MySQLServer:
    CONF_TEMPLATE = '''
user ${USER};
worker_processes  1;

error_log  ${ERROR_LOG};
pid        ${PID_FILE};

mysql {
  access_log  ${ACCESS_LOG};
  
  server {
    listen       ${PORT} default;
    server_name  localhost;

  }
}
  '''
  
    cmd='/etc/init.d/mysql'
    cmd_start=join(cmd,' start')
    cmd_stop=join(cmd,' stop')
  
    def __init__(self, configuration):
        '''Creates a new MySQLServer object.    
        port   : port to wich the web server listens for incoming connections.
        '''
        self.state = S_INIT
        self.restart_count = 0
        self.configure(configuration)
        self.start()
        self.stop_sig = SIGINT
  
    def configure(self, configuration=None):
        port = int(configuration.port)      
        verify_port(port)
        if self.state == S_INIT:
            if not exists(S_MYSQL_HOME):
                makedirs(S_MYSQL_HOME)
        self.config_dir = S_MYSQL_HOME
        self.config_file = join(self.config_dir, 'mysql.conf')
        self.access_log = join(self.config_dir, 'access.log')
        self.error_log = join(self.config_dir, 'error.log')
        self.pid_file = join(self.config_dir, 'mysql.pid')
        self.user = 'www-data'
        self.port = port
        self._write_config()
        self.start_args = [self.cmd_start]
  
    def _write_config(self):
        '''Write configuration file.'''    
        template = Template(self.CONF_TEMPLATE)
        conf_fd = open(self.config_file, 'w')
        conf_fd.write(template.substitute(ACCESS_LOG=self.access_log, ERROR_LOG=self.error_log,
                        PID_FILE=self._current_pid_file(),
                        USER=self.user, PORT=self.port))
        conf_fd.close()
        logger.debug('MySQLServer configuration written to %s' % (self.config_file))  
   
    def start(self):
        self.state = S_STARTING
        devnull_fd = open(devnull, 'w')
        proc = Popen(self.start_args, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        if proc.wait() != 0:
            logger.critical('Failed to start mysql server (code=%d)' % proc.returncode)
        raise OSError('Failed to start mysql server (code=%d)' % proc.returncode)
        self.state = S_RUNNING
        logger.info('MySql started')
  
    def stop(self):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            if exists(self._current_pid_file()):
                try:
                    pid = int(open(self._current_pid_file(), 'r').read().strip())
                except IOError as e:
                    logger.exception('Failed to open PID file "%s"' % (self._current_pid_file()))
                    raise e
                except (ValueError, TypeError) as e:
                    logger.exception('PID in "%s" is invalid' % (self._current_pid_file()))
                    raise e                
                try:
                    kill(pid, self.stop_sig)
                    self.state = S_STOPPED
                    logger.info('WebServer stopped')
                except (IOError, OSError) as e:
                    logger.exception('Failed to kill WebServer PID=%d' % (pid))
                    raise e
            else:
                logger.critical('Could not find PID file %s to kill WebServer' % (self._current_pid_file()))
                raise IOError('Could not find PID file %s to kill WebServer' % (self._current_pid_file()))
        else:
            logger.warning('Request to kill WebServer while it is not running')

    def restart(self):
        self.restart_count += 1
        self._write_config()
    
        try:
            pid = int(open(self._current_pid_file(increment=-1), 'r').read().strip())
        except IOError as e:
            logger.exception('Failed to open PID file "%s"' % (self._current_pid_file(increment=-1)))
            raise e
        except (ValueError, TypeError) as e:
            logger.exception('PID in "%s" is invalid' % (self._current_pid_file(increment=-1)))
            raise e
    
        try:
            kill(pid, SIGHUP)
        except (IOError, OSError):
            logger.exception('Failed to "gracefully" kill WebServer PID=%d' % (pid))
            raise e
        else:
            self.post_restart()
            logger.info('WebServer restarted')
  
    def post_restart(self): pass
  
    def status(self):
        return {'state': self.state,                
                'port': self.port}

def expose(http_method):
    def decorator(func):
        if http_method not in exposed_functions:
            exposed_functions[http_method] = {}
        exposed_functions[http_method][func.__name__] = func
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped
    return decorator

class AgentException(Exception):
    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.args = args
        if 'detail' in kwargs:
            self.message = '%s DETAIL:%s' % ( (E_STRINGS[code] % args), str(kwargs['detail']) )
        else:
            self.message = E_STRINGS[code] % args

def _mysqlserver_get_params(post_params):
    '''TODO: check for file inclusion. Add aditional parameters. '''
    ret = {}
    if 'port' not in post_params:
        raise AgentException(E_ARGS_MISSING, 'port')
    if not post_params['port'].isdigit():
        raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
    ret['port'] = int(post_params.pop('port'))
    if len(post_params) != 0:
        raise AgentException(E_ARGS_UNEXPECTED, post_params.keys())
    return ret

@expose('GET')
def getMySQLServerState(kwargs):
    """GET state of WebServer"""
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    with web_lock:
        try:
            fd = open(mysql_file, 'r')
            p = pickle.load(fd)
            fd.close()
        except Exception as e:
            ex = AgentException(E_CONFIG_READ_FAILED, MySQLServer.__name__, mysql_file, detail=e)
            logger.exception(ex.message)
            return {'opState': 'ERROR', 'error': ex.message}
        else:
            return {'opState': 'OK', 'return': p.status()}
        
@expose('POST')
def createMySQLServer(post_params):
    """Create the MySQLServer"""
    try: post_params = _mysqlserver_get_params(post_params)
    except AgentException as e:
        return {'opState': 'ERROR', 'error': e.message}
    else:
        with web_lock:
            if exists(mysql_file):
                return {'opState': 'ERROR', 'error': AgentException(E_CONFIG_EXISTS).message}
            try:
                if type(post_params) != dict: raise TypeError()
                p = MySQLServer(**post_params)
            except (ValueError, TypeError) as e:
                ex = AgentException(E_ARGS_INVALID, detail=str(e))
                return {'opState': 'ERROR', 'error': ex.message}
            except Exception as e:
                ex = AgentException(E_UNKNOWN, detail=e)
                logger.exception(e)
                return {'opState': 'ERROR', 'error': ex.message}
            else:
                try:
                    fd = open(mysql_file, 'w')
                    pickle.dump(p, fd)
                    fd.close()
                except Exception as e:
                    ex = AgentException(E_CONFIG_COMMIT_FAILED, detail=e)
                    logger.exception(ex.message)
                    return {'opState': 'ERROR', 'error': ex.message}
                else:
                    return {'opState': 'OK'}
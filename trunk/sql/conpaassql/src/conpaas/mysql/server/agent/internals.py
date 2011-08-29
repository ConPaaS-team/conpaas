from threading import Lock
from string import Template
from os import kill, makedirs, remove
from os.path import join, devnull, exists
from subprocess import Popen

from conpaas.log import create_logger
from subprocess import Popen
from os.path import devnull, exists

import socket
import os
import ConfigParser
import MySQLdb
import pickle


exposed_functions = {}

CONFIGURATION_FILE='configuration.cnf'

E_ARGS_UNEXPECTED = 0
E_CONFIG_NOT_EXIST = 1
E_CONFIG_READ_FAILED = 2
E_CONFIG_EXISTS = 3
E_ARGS_INVALID = 4
E_UNKNOWN = 5
E_CONFIG_COMMIT_FAILED = 6
E_ARGS_MISSING = 7
E_MYSQL = 8

E_STRINGS = [  
  'Unexpected arguments %s', # 1 param (a list)
  'Unable to open configuration file: %s',
  'Failed to parse configuration file error: %s',
  'Configuration file already exists',
  'Invalid arguments',
  'Unknown error. Description: %s',
  'Failed to commit configuration',
  'Missing argument: %s',
  'MySQL reported an error: %s'
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
S_MYSQL_HOME  = S_PREFIX + 'conpaas/conf/mysql'

class MySQLServerConfiguration:
    
    def __init__(self):
        '''holds the configuration of the server.
        '''
        logger.debug("Entering init MySQLServerConfiguration")
        self.hostname = socket.gethostname()
        self.restart_count = 0
        self.pid_file = "/var/lib/mysql/" + self.hostname + ".pid"
        self.config_dir = os.getcwd()
        self.access_log = os.getcwd() + '/access.log'
        self.error_log =  os.getcwd() + '/error.log'        
        
        self.conn_location = ''
        self.conn_username = ''
        self.conn_password = ''
        
        self.mycnf_filepath = ''
        self.path_mysql_ssr = ''
        self.port_client = ''
        self.port_mysqld = ''
        self.bind_address = ''
        self.data_dir = ''
        
        self.read_config()
        
        logger.debug("Leaving init MySQLServerConfiguration")
        
    def read_config(self):
        logger.debug("Entering read_config")
        try:
            logger.debug("Trying to get params from configuration file ")
            config = ConfigParser.ConfigParser()
            #config.readfp(open("/home/danaia/Desktop/worskpace_eclipse/conpaas-sql-trunk-rev-107/conpaassql/src/configuration.cnf"))
            config.readfp(open(os.getcwd() + "/" + CONFIGURATION_FILE))
            self.conn_location = config.get("MySQL_root_connection", "location")
            self.conn_password = config.get("MySQL_root_connection", "password")
            self.conn_username = config.get("MySQL_root_connection", "username")
            logger.debug("Got parameters for root connection to MySQL")
            self.mycnf_filepath = config.get("MySQL_configuration","my_cnf_file")
            self.path_mysql_ssr = config.get("MySQL_configuration","path_mysql_ssr")
            file = open(self.mycnf_filepath)
            my_cnf_text = file.read()
            config.readfp( self.MySQLConfigParser(my_cnf_text))    
            self.port_mysqld = config.get ("mysqld", "port")      
            self.bind_address = config.get ("mysqld", "bind-address")
            self.data_dir = config.get ("mysqld", "datadir")
            os.system("rm temp.cnf")
            logger.debug("Got configuration parameters")
        except ConfigParser.Error, err:
            ex = AgentException(E_CONFIG_READ_FAILED, str(err))
            logger.critical(ex.message)
        except IOError, err:
            ex = AgentException(E_CONFIG_NOT_EXIST, str(err))
            logger.critical(ex.message)  
        logger.debug("Leaving read_config")
        
    def change_config(self, id_param, param):
        if id_param == 'datadir':
            os.system("sed -i 's\datadir\t\t= " + self.data_dir +"|datadir\t\t= " + param + "|g' " + self.mycnf_filepath)
            self.data_dir = param 
        elif id_param == 'port':
            os.system("sed -i 's/port\t\t= " + self.port_mysqld +"/port\t\t= " + param + "/g' " + self.mycnf_filepath)            
            self.port_mysqld = param
        elif id_param == 'bind-address':
            os.system("sed -i 's/bind-address\t\t= " + self.bind_address +"/bind-address\t\t= " + param + "/g' " + self.mycnf_filepath)            
            self.bind_address = param
        else:
            ex = AgentException(E_CONFIG_READ_FAILED, "cant find id: " + id_param)
            raise Exception(ex.message)
    
    def MySQLConfigParser(self, text):
        #comments inside
        while text.count("#")>0:
            text = text[0:text.index("#")] + text[text.index("\n",text.index("#")):]
        zac = 0
        while text.count("\n",zac)>1:
            if ( text[text.index("\n",zac)+1:text.index("\n",text.index("\n",zac+1))].find("[") == -1 
               & text[text.index("\n",zac)+1:text.index("\n",text.index("\n",zac+1))].find("=") == -1):
                text = text[0:text.index("\n",zac)+1] + text[text.index("\n",text.index("\n",zac+1)):]
            zac = text.index("\n", zac+1)         
        # \n inside
        while text.count("\t")>0:
            text = text[0:text.index("\t")] + text[text.index("\t")+1:]
        while text.count(" ")>0:
            text = text[0:text.index(" ")] + text[text.index(" ")+1:]
        while text.count("\n\n")>0:
            text = text[0:text.index("\n\n")] + text[text.index("\n\n")+1:]
        file = open(os.getcwd()+"/temp.cnf", "w")
        file.write(text)
        file.close()
        file = open(os.getcwd()+"/temp.cnf","r")
        return file
    
    def add_user_to_MySQL(self, new_username, new_password):
        db = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db.cursor()
        exc.execute ("create user '" + new_username + "'@'localhost' identified by '" + new_password + "'")
        exc.execute ("grant all privileges on *.* TO '" + new_username + "'@'localhost' with grant option;")
        exc.execute ("create user '" + new_username + "'@'%' identified by '" + new_password + "'")
        exc.execute ("grant all privileges on *.* TO '" + new_username + "'@'%' with grant option;")
        db.close()
        
    def remove_user_to_MySQL(self, username):
        db = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db.cursor()
        exc.execute ("drop user '" + username +"'@'localhost'")
        exc.execute ("drop user '" + username +"'@'%'")
        db.close()
    
    def get_users_in_MySQL(self):
        db = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db.cursor()
        exc.execute("SELECT user, host FROM mysql.user")
        rows = exc.fetchall()
        db.close()
        ret = {'opState': 'OK'}
        i = 0
        for row in rows:
            i = i+1
            ret['info' + str(i)] = {'location': row[0], 'username': row[1]}
        return ret
    
    def create_MySQL_with_dump(self, f):
        logger.debug("Entering create_MySQL_with_dump")
        try:
            mysqldump = f.read()
            logger.debug("temporary writing file to: : " + os.getcwd() +  '/mysqldump')
            file(os.getcwd() + '/mysqldump' , "wb").write(mysqldump)
            os.system("mysql -u " + self.conn_username + " -p"  + self.conn_password + " < " + os.getcwd() + '/mysqldump')
            os.system("rm mysqldump")
            logger.debug("Leaving create_MySQL_with_dump")
            return {'opState':'OK'}
        except Exception as e:
            ex = AgentException(E_UNKNOWN,e.message)
            logger.exception(ex.message)
            return {'opState': 'ERROR', 'error': e.message}   
    
class MySQLServer:
    def __init__(self):
        logger.debug("Entering MySQLServer initialization")
        self.config = MySQLServerConfiguration()
        self.state = S_INIT
        logger.debug("Leaving MySQLServer initialization")
        
    def post_restart(self): pass
    ''' TODO: things that are done after restart
    '''
        
    def start(self):
        #TODO: could look for PID file ?
            logger.debug("Entering MySQLServer.start")
            self.state = S_STARTING            
            devnull_fd = open(devnull, 'w')
            logger.debug('Starting with arguments:' + self.config.path_mysql_ssr + " start")
            proc = Popen([self.config.path_mysql_ssr, "start"], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
            logger.debug("MySQL started")
            proc.wait()
            logger.debug("Server started.")
            if exists(self.config.pid_file) == False:
                logger.critical('Failed to start mysql server.)')
                self.state = S_STOPPED
                raise OSError('Failed to start mysql server.')            
            if proc.wait() != 0:
                logger.critical('Failed to start mysql server (code=%d)' % proc.returncode)
                self.state = S_STOPPED
                raise OSError('Failed to start mysql server (code=%d)' % proc.returncode)            
            self.state = S_RUNNING
            logger.info('MySql started')
            logger.debug('Leaving MySQLServer.start')
    
    def stop(self):
        logger.debug('Entering MySQLServer.stop')
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            if exists(self.config.pid_file):
                try:
                    int(open(self.config.pid_file, 'r').read().strip())                    
                    devnull_fd = open(devnull, 'w')
                    logger.debug('Stopping with arguments:' + self.config.path_mysql_ssr + " stop")
                    proc = Popen([self.config.path_mysql_ssr, "stop"], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
                    logger.debug("Stopping server")
                    proc.wait()                                        
                    if exists(self.config.pid_file) == True:
                        logger.critical('Failed to stop mysql server.)')
                        self.state = S_RUNNING
                        raise OSError('Failed to stop mysql server.')                        
                    self.state = S_STOPPED
                except IOError as e:
                    self.state = S_STOPPED
                    logger.exception('Failed to open PID file "%s"' % (self.pid_file))
                    raise e
                except (ValueError, TypeError) as e:
                    self.state = S_STOPPED
                    logger.exception('PID in "%s" is invalid' % (self.pid_file))
                    raise e
            else:
                logger.critical('Could not find PID file %s to kill WebServer' % (self.pid_file))
                self.state = S_STOPPED
                logger.debug('Leaving MySQLServer.stop')
                raise IOError('Could not find PID file %s to kill WebServer' % (self.pid_file))                
        else:
            logger.warning('Request to kill WebServer while it is not running')
        logger.debug('Leaving MySQLServer.stop')
        
    def restart(self):
        logger.debug("Entering MySQLServer restart")
        self.config.restart_count += 1 
        logger.debug("Restart count just increased to: " + str(self.config.restart_count))
        try:
            int(open(self.config.pid_file, 'r').read().strip())
            devnull_fd = open(devnull, 'w')
            logger.debug('Restarting with arguments:' + self.config.path_mysql_ssr + " restart")
            proc = Popen([self.config.path_mysql_ssr, "restart"] , stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
            logger.debug("Restarting mysql server")
            proc.wait()                            
            if exists(self.config.pid_file) == False:
                logger.critical('Failed to restart mysql server.)')
                raise OSError('Failed to restart mysql server.')            
        except IOError as e:
            logger.exception('Failed to open PID file "%s"' % (self._current_pid_file(increment=-1)))
            self.state = S_STOPPED
            raise e
        except (ValueError, TypeError) as e:
            logger.exception('PID in "%s" is invalid' % (self._current_pid_file(increment=-1)))
            self.state = S_STOPPED
            raise e    
        else:
            self.post_restart()
            self.state = S_RUNNING
            logger.info('MySQL restarted')          
        logger.debug("Leaving MySQLServer restart")

    def status(self):
        logger.debug('Entering MySQLServer.status')
        logger.debug('Leaving MySQLServer.status')
        return {'state': self.state,                
                'port': self.config.port_mysqld}     
        
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
    logger.debug('Got post_params %s' % post_params)
    if 'port' not in post_params:
        raise AgentException(E_ARGS_MISSING, 'port')
    if not post_params['port'].isdigit():
        raise AgentException(E_ARGS_INVALID, detail='Invalid "port" value')
    ret['port'] = int(post_params.pop('port'))
    if len(post_params) != 0:
        raise AgentException(E_ARGS_UNEXPECTED, post_params.keys())
    return ret

def getMySQLServerState_old(kwargs):
    """GET state of WebServer"""
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    with web_lock:
        try:
            if os.path.exists(mysql_file):
                fd = open(mysql_file, 'r')
                p = pickle.load(fd)
                fd.close()
            else:
                return {'opState':'OK','return': 'shutdown'}
        except Exception as e:
            ex = AgentException(E_CONFIG_READ_FAILED, MySQLServer.__name__, mysql_file, detail=e)
            logger.exception(ex.message)
            return {'opState': 'ERROR', 'error': ex.message}
        else:
            return {'opState': 'OK', 'return': p.status()}
        
        
@expose('POST')
def createMySQLServer(post_params):
    logger.debug("Entering createMySQLServer")
    try:
        niam.start()
        logger.debug("Leaving createMySQLServer")
        return {'opState': 'OK'}
    except Exception as e:
        logger.exception("Error: " + str(e))
        return {'opState': 'ERROR', 'error': str(e)}
    
def createMySQLServer_old(post_params):
    """Create the MySQLServer"""
    logger.debug('Entering createMySQLServer')
    try: post_params = _mysqlserver_get_params(post_params)
    except AgentException as e:
        return {'opState': 'ERROR', 'error': e.message}
    else:
        with web_lock:
            if exists(mysql_file):
                logger.debug('Leaving createMySQLServer')
                return {'opState': 'ERROR', 'error': AgentException(E_CONFIG_EXISTS).message}
            try:
                if type(post_params) != dict: raise TypeError()
                p = MySQLServer(**post_params)                
            except (ValueError, TypeError) as e:
                ex = AgentException(E_ARGS_INVALID, detail=str(e))
                logger.debug('Leaving createMySQLServer')
                return {'opState': 'ERROR', 'error': ex.message}
            except Exception as e:
                ex = AgentException(E_UNKNOWN, detail=e)
                logger.exception(e)
                logger.debug('Leaving createMySQLServer')
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
                
def stopMySQLServer_old(kwargs):
    """KILL the WebServer"""
    if len(kwargs) != 0:
        return {'opState': 'ERROR', 'error': AgentException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
    with web_lock:
        try:
            try:
                fd = open(mysql_file, 'r')
                p = pickle.load(fd)
                fd.close()
            except Exception as e:
                ex = AgentException(E_CONFIG_READ_FAILED, 'stopMySQLServer',str(mysql_file), detail=e)
                logger.exception(ex.message)
                return {'opState': 'ERROR', 'error': ex.message}
            p.stop()
            remove(mysql_file)
            return {'opState': 'OK'}
        except Exception as e:
            ex = AgentException(E_UNKNOWN, detail=e)
            logger.exception(e)
            return {'opState': 'ERROR', 'error': ex.message}        

'''
    Shuts down the whole Agent together with MySQL server.
'''
def shutdownMySQLServerAgent(kwargs):
    """Shutdown the Agent"""
    niam.stop()    
    from conpaas.mysql.server.agent.server import agentServer
    agentServer.shutdown()
    import sys
    sys.exit(0)
    
@expose('POST')
def stopMySQLServer(params):
    logger.debug("Entering stopMySQLServer")
    try:
        niam.stop()
        logger.debug("Leaving stopMySQLServer")
        return {'opState':'OK'}
    except Exception as e:
        ex = AgentException(E_UNKNOWN, detail=e)
        logger.exception(e)
        logger.debug('Leaving createMySQLServer')
        return {'opState': 'ERROR', 'error': ex.message}

@expose('POST')
def restartMySQLServer(params):
    logger.debug("Entering restartMySQLServer")
    try:
        niam.restart()
        logger.debug("Leaving restartMySQLServer")
        return {'opState':'OK'}
    except Exception as e:
        ex = AgentException(E_UNKNOWN, detail=e)
        logger.exception(e)
        logger.debug('Leaving createMySQLServer')
        return {'opState': 'ERROR', 'error': ex.message}

@expose('GET')
def getMySQLServerState(params):
    logger.debug("Entering getMySQLServerState")
    try: 
        status = niam.status()
        logger.debug("Leaving getMySQLServerState")
        return {'opState':'OK', 'return': status}
    except Exception as e:
        ex = AgentException(E_UNKNOWN, detail=e)
        logger.exception(e)
        logger.debug('Leaving createMySQLServer')
        return {'opState': 'ERROR', 'error': ex.message}
    
@expose('POST')
def setMySQLServerConfiguration(params):
    logger.debug("Entering setMySQLServerConfiguration")
    try:
        niam.config.change_config(params['id_param'], params["value"])  
        logger.debug("Leaving setMySQLServerConfiguration")
        return {'opState':'OK'}
    except Exception as e:
        ex = AgentException(E_UNKNOWN, detail=e)
        logger.exception(e)
        logger.debug('Leaving createMySQLServer')
        return {'opState': 'ERROR', 'error': ex.message}  

@expose('POST')
def createNewMySQLuser(params):
    logger.debug("Entering createNewMySQLuser")
    if len(params) != 2:
        ex = AgentException(E_ARGS_UNEXPECTED, params)
        logger.exception(ex.message) 
        return {'opState': 'ERROR', 'error': ex.message}
    try:
        niam.config.add_user_to_MySQL(params['username'], params['password'])
        logger.debug("Leaving createNewMySQLuser")
        return {'opState': 'OK'}
    except MySQLdb.Error, e:
        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        logger.exception(ex.message) 
        return {'opState': 'ERROR', 'error': ex.message}  
    
@expose('POST')
def removeMySQLuser(params):
    logger.debug("Entering removeMySQLuser")
    if len(params) != 1:
        ex = AgentException(E_ARGS_UNEXPECTED, params)
        logger.exception(ex.message) 
        return {'opState': 'ERROR', 'error': ex.message}  
    try:
        niam.config.remove_user_to_MySQL(params['username'])
        logger.debug("Leaving removeMySQLuser")
        return {'opState': 'OK'}
    except MySQLdb.Error, e:
        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        logger.exception(ex.message) 
        return {'opState': 'ERROR', 'error': ex.message}  
    
@expose('GET')
def listAllMySQLusers(params):
    logger.debug("Entering listAllMySQLusers")
    try:
        ret = niam.config.get_users_in_MySQL()
        logger.debug("Leaving listAllMySQLusers")
        return ret
    except MySQLdb.Error, e:
        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        logger.exception(ex.message) 
        return {'opState': 'ERROR', 'error': ex.message} 

@expose('POST')
def create_with_MySQLdump(params):
    logger.debug("Entering create_with_MySQLdump")
    params['mysqldump']  
    f = params['mysqldump']['file']
    ret = niam.config.create_MySQL_with_dump(f)
    return ret   

  
niam = MySQLServer()
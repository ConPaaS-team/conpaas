"""
Created on November, 2011

   This module contains internals of the ConPaaS MySQL Server. ConPaaS MySQL Server consists of several
   nodes with different roles
     

   :platform: Linux, Debian
   :synopsis: Internals of agent service for ConPaaS MySQL Servers.
   :moduleauthor: Ales Cernivec <ales.cernivec@xlab.si> 

"""

from threading import Lock
from string import Template
from os import kill, makedirs, remove
from os.path import join, devnull, exists
from subprocess import Popen
from threading import Thread
from conpaas.log import create_logger
from subprocess import Popen
from os.path import devnull, exists

import socket
import os
import ConfigParser
import MySQLdb
import pickle
import io
import time
from conpaas.web.http import HttpJsonResponse, HttpErrorResponse, _jsonrpc_post
from conpaas.mysql.utils.log import get_logger_plus
from conpaas.mysql.adapters.supervisor import SupervisorSettings, Supervisor
from conpaas.mysql.adapters.mysql.config import MySQLConfig
from conpaas.mysql.server.agent.maintain_connection import MaintainAgentConnection

exposed_functions = {}

CONFIGURATION_FILE='configuration.cnf'
DATABASE_DUMP_LOCATION='/tmp/contrail_dbdump.db'

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
  'Invalid arguments: %s',
  'Unknown error. Description: %s',
  'Failed to commit configuration',
  'Missing argument: %s',
  'MySQL reported an error: %s'
]

SUPERVISOR_MYSQL_NAME="mysqld"

web_lock = Lock()
# logger = create_logger(__name__)
logger, flog, mlog = get_logger_plus(__name__)

mysql_file = "/tmp/conpaassql" 

S_PREFIX    = "/tmp/"
S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'
S_MYSQL_HOME  = S_PREFIX + 'conpaas/conf/mysql'

agent = None

class MySQLServerConfiguration:
    """
    Holds configuration of the MySQL server.
    
    supervisor_settings holds Settings for the supervisor.
     
    """
       
    dummy_config = False
    mysqld_configuration = None
    supervisor_settings = None
            
    @mlog
    def __init__(self, config, _dummy_config=False):
        """
        Creates a configuration from `config`. 
        
        :param config: Configuration read with ConfigParser.
        :type config: ConfigParser
        :param  _dummy_config: Set to `True` when used in unit testing.
        :type boolean: boolean value.
        """
        
        self.dummy_config = _dummy_config
        '''holds the configuration of the server.
        '''        
        logger.debug("Entering init MySQLServerConfiguration")
        self.hostname = socket.gethostname()
        self.restart_count = 0
        self.agent = {}
        self.manager = {}
    
        try:
            supervisor_port = config.get ("supervisor", "port")
            supervisor_user = config.get ("supervisor", "user")
            supervisor_password = config.get ("supervisor", "password")
            self.supervisor_settings = SupervisorSettings(supervisor_user, supervisor_password, supervisor_port)            
            logger.debug("Trying to get params from configuration file ")        
            self.conn_location = config.get("MySQL_root_connection", "location")
            logger.debug('conn_location before %s' % self.conn_location )
            self.conn_location = config.get("ConPaaSSQL","agent_interface")
            logger.debug('conn_location after %s' % self.conn_location )
            
            self.conn_username = config.get("MySQL_root_connection", "username")
            self.conn_password = config.get("MySQL_root_connection", "password")      
            logger.debug("Got parameters for root connection to MySQL")
            self.mycnf_filepath = config.get("MySQL_configuration","my_cnf_file")            

            self.agent["port"] = config.get("ConPaaSSQL","agent_port")
            self.agent["ip"] = config.get("ConPaaSSQL","agent_interface")
            self.agent["vm_id"] = config.get("ConPaaSSQL","vm_id")
            self.agent["vm_name"] = config.get("ConPaaSSQL","vm_name")
            self.manager["port"] = config.get("ConPaaSSQL","manager_port")
            self.manager["ip"] = config.get("ConPaaSSQL","manager_ip")
            
            logger.debug("My Manager is here: %s" % self.manager)
            logger.debug("My interface should be here: %s" % self.agent)
            
            self.mysqld_configuration = MySQLConfig(self.mycnf_filepath)
            self.port_mysqld = self.mysqld_configuration.get("mysqld", "port") 
            self.bind_address = self.mysqld_configuration.get("mysqld", "bind-address") 
            self.data_dir = self.mysqld_configuration.get("mysqld", "datadir")
            
            logger.debug('Changeing bind-address to mysqld: %s' % self.conn_location )
            self.change_config('mysqld', 'bind-address', self.conn_location) 
            logger.debug("Got configuration parameters")
        except ConfigParser.Error, err:
            ex = AgentException(E_CONFIG_READ_FAILED, str(err))
            logger.critical(ex.message)
        except IOError, err:
            ex = AgentException(E_CONFIG_NOT_EXIST, str(err))
            logger.critical(ex.message)                
        logger.debug("Leaving init MySQLServerConfiguration")
    
    @mlog    
    def change_config(self, section, id_param, param):
        """
        Changes MySQL configuration with `id_param` to value of `param`.
        :param section: What section to change.
        :type id_param: str
        :param id_param: What to change.
        :type id_param: str
        :param param: value of to change the `id_param` to.
        :type param: str  
        
        """
        self.mysqld_configuration.set(section, id_param, param)
        self.mysqld_configuration.save_asnew_config()
                        
    @mlog
    def add_user_to_MySQL(self, new_username, new_password):
        db = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db.cursor()
        exc.execute ("create user '" + new_username + "'@'localhost' identified by '" + new_password + "'")
        exc.execute ("grant all privileges on *.* TO '" + new_username + "'@'localhost' with grant option;")
        exc.execute ("create user '" + new_username + "'@'%' identified by '" + new_password + "'")
        exc.execute ("grant all privileges on *.* TO '" + new_username + "'@'%' with grant option;")
        db.close()
     
    @mlog    
    def remove_user_to_MySQL(self, username):
        db = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db.cursor()
        exc.execute ("drop user '" + username +"'@'localhost'")
        exc.execute ("drop user '" + username +"'@'%'")
        db.close()
    
    @mlog
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
            ret['info' + str(i)] = {'location': row[1], 'username': row[0]}
        return ret
    
    '''Before creating a data snapshot or starting 
    the replication process, you should record the 
    position of the binary log on the master. You will 
    need this information when configuring the slave so 
    that the slave knows where within the binary log to 
    start executing events. See Section 15.1.1.4, Obtaining 
    the Replication Master Binary Log Coordinates. 

1st session
mysql> FLUSH TABLES WITH READ LOCK;

2nd session
mysql > SHOW MASTER STATUS;
record the values

close 2nd session

on the master 
 mysqldump --all-databases --lock-all-tables >dbdump.db

1st session
mysql>UNLOCK TABLES;

    '''
    @mlog
    def replication_record_the_position(self):
        '''1st session
        '''
        db1 = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db1.cursor()
        exc.execute("FLUSH TABLES WITH READ LOCK;")
        '''2nd session
        '''
        db2 = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db2.cursor()
        exc.execute("SHOW MASTER STATUS;")
        rows = exc.fetchall()
        db2.close()
        i = 0
        ret = {'opState': 'OK'}
        for row in rows:
            i = i+1
            ret['position' + str(i)] = {'binfile': row[0], 'position': row[1]}        
        os.system("mysqldump -u " + self.conn_username + " -p"  + self.conn_password + "--all-databases --lock-all-tables > " + DATABASE_DUMP_LOCATION)
        exc = db1.cursor()
        exc.execute("UNLOCK TABLES;")
        db1.close()
        return ret

    '''
        @param master_host: hostname of the master node.
        @param master_log_file: filename of the master log.
        @param master_log_pos: position of the master log file.
        @param slave_server_id: id which will be written into my.cnf.
    
    '''
    @mlog
    def set_up_replication_slave(self, master_host, master_log_file, master_log_pos, slave_server_id):
        logger.debug('Entering set_up_replication_slave')        
        logger.debug("Creating sql query for replication slave-master connection")
        db = MySQLdb.connect(self.conn_location, self.conn_username, self.conn_password)
        exc = db.cursor()
        query=("CHANGE MASTER TO  MASTER_HOST='%s', " + 
                    "MASTER_USER='%s', " +
                    "MASTER_PASSWORD='%s', " 
                    "MASTER_LOG_FILE='%s', " +  
                    "MASTER_LOG_POS=%s;" % (master_host, self.conn_username, self.conn_password, master_log_file, master_log_pos))
        logger.debug("Created query: " + query)
        exc.execute(query)
        db.close()
        logger.debug("Adding server-id into my.cnf")        
        file = open(self.mycnf_filepath)
        content = file.read()
        mysqlconfig = ConfigParser.RawConfigParser(allow_no_value=True)               
        mysqlconfig.readfp(io.BytesIO(content))
        mysqlconfig.set("mysqld", "server-id", slave_server_id)      
        mysqlconfig.set("mysqld", "skip-slave-start", slave_server_id)        
        file.close()
        os.remove(self.mycnf_filepath)
        newfile=open(self.mycnf_filepath,"w")
        logger.debug("Writing new configuration file.")
        mysqlconfig.write(newfile)
        newfile.close()
        logger.debug("Restarting mysql server due to changed server-id.")
        agent.restart()
        logger.debug('Exiting set_up_replication_slave')
    
    @mlog
    def create_MySQL_with_dump(self, f):
        logger.debug("Entering create_MySQL_with_dump")
        try:
            mysqldump = f.read()
            logger.debug("temporary writing file to: : " + os.getcwd() +  '/mysqldump')
            file(os.getcwd() + '/mysqldump' , "wb").write(mysqldump)
            os.system("mysql -u " + self.conn_username + " -p"  + self.conn_password + " < " + os.getcwd() + '/mysqldump')
            os.system("rm mysqldump")
            logger.debug("Leaving create_MySQL_with_dump")
            return HttpJsonResponse({'return':'OK'})
        except Exception as e:
            ex = AgentException(E_UNKNOWN,e.message)
            logger.exception(ex.message)
            return HttpJsonResponse({'return': 'ERROR', 'error': e.message})   
    
class MySQLServer:
    """
    Handles MySQL server daemon.
    
    :param configInput: Configuration read with ConfigParser.
    :type configInput: ConfigParser
      
    :param _dummy_backend: Set to True for unit testing.
    :type _dummy_backend: boolean    
    """
    
    dummy_backend = False
    
    supervisor = None
    
    @mlog
    def __init__(self, configInput, _dummy_backend=False):
        """
        Creates MySQL configuration. 
        """
        
        logger.debug("Entering MySQLServer initialization")
        self.config = MySQLServerConfiguration(configInput, _dummy_backend)
        if not _dummy_backend: 
            self.supervisor = Supervisor(self.config.supervisor_settings)
        else:
            logger.debug("Not creating supervisor, due to dummy_backend")
        logger.debug("Starting the server")
       
        self.start()
        self.dummy_backend = _dummy_backend
        logger.debug("Start with registering to the manager.")
        
        MaintainAgentConnection(self).start()
        #Thread(target=maintain_connection(self)).start()
        logger.debug("Leaving MySQLServer initialization")
    
    @mlog
    def post_restart(self): pass
    """ Things that are done after restart. Not implemented yet.
    """
    
    @mlog  
    def start(self):
            """
            Starts MySQL server deamon. It also changes `self.state` to `S_RUNNING`.
            """                    
            self.state = S_STARTING
            status = self.supervisor.info(SUPERVISOR_MYSQL_NAME)
            logger.debug('Current status is %s' % status)
            if status['statename'] == "RUNNING":
                logger.debug("Mysqld is already running.")
                self.state = S_RUNNING
                return
            
            if self.dummy_backend == False:                
                try:
                    self.supervisor.start(SUPERVISOR_MYSQL_NAME)
                except Exception as err:
                    logger.error("Error: %s " % str(err))
                status = self.supervisor.info(SUPERVISOR_MYSQL_NAME)
                logger.debug("Server started: %s" % status)
                if status['statename'] == "STOPPED":
                    logger.critical('Failed to start mysql server.)')
                    self.state = S_STOPPED
                    raise OSError('Failed to start mysql server.')                          
            else:
                logger.debug("Running with dummy backend")
            self.state = S_RUNNING
            logger.info('MySql started')
    
    @mlog    
    def stop(self):
        logger.debug('Entering MySQLServer.stop')
        status = self.supervisor.info(SUPERVISOR_MYSQL_NAME)
        if status['statename'] == "NOT_RUNNING":
            logger.debug("Mysqld is already stopped.")
            return
        if self.dummy_backend:
            if self.state == S_RUNNING:
                logger.debug("Stopping server")
                self.state = S_STOPPING
                self.state = S_STOPPED
                logger.debug('Leaving MySQLServer.stop')            
        else:
            if self.state == S_RUNNING:
                self.state = S_STOPPING
                status = self.supervisor.info(SUPERVISOR_MYSQL_NAME)
                logger.debug("Status: %s " % status)
                if status['statename'] == "RUNNING":                
                    logger.debug("Stopping server")
                    self.supervisor.stop(SUPERVISOR_MYSQL_NAME)             
                    status = self.supervisor.info(SUPERVISOR_MYSQL_NAME)
                    logger.debug("New status is: %s" % status)
                    if not status['statename'] == "STOPPED":
                        logger.critical('Failed to stop mysql server.)')
                    self.state = S_STOPPED
                else:
                    logger.debug("Setting state to S_STOPPED. I did nothing.")
                    logger.debug("Status: %s " % status)
                    self.state = S_STOPPED
                    logger.debug('Leaving MySQLServer.stop')                                    
            else:
                logger.warning('Request to kill WebServer while it is not running')
        logger.debug('Leaving MySQLServer.stop')
    
    @mlog    
    def restart(self):
        logger.debug("Entering MySQLServer restart")
        self.config.restart_count += 1 
        logger.debug("Restart count just increased to: " + str(self.config.restart_count))
        if self.dummy_backend:
            logger.debug("Restarting mysql server")
            self.state = S_RUNNING
            logger.info('MySQL restarted') 
        else:            
            logger.debug("Stopping the server")
            self.stop()
            logger.debug("Starting the server")
            self.start()
            logger.info('MySQL restarted')          
        logger.debug("Leaving MySQLServer restart")
    
    @mlog
    def status(self):
        logger.debug('Entering MySQLServer.status')
        logger.debug('Leaving MySQLServer.status')
        return {'id': self.config.agent['vm_id'],
                'state': self.state,
                'name': self.config.agent['vm_name'],
                'ip': self.config.agent['ip'],                
                'port': self.config.agent['port'],
                'mysqld_port': self.config.port_mysqld, 
                'supervisor_data': self.supervisor.info(SUPERVISOR_MYSQL_NAME)}     
        
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

        
@expose('POST')
def start_server(post_params):
    """
    Creates an agent server. Calls to :py:meth:`MySQLServer.start`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

         return HttpJsonResponse({'return': 'ERROR', 'error': str(e)})
         
    :returns: HttpJsonResponse
         
    """
    logger.debug("Entering start_server")
    try:
        agent.start()
        logger.debug("Leaving start_server")
        return HttpJsonResponse({'return': 'OK'})
    except Exception as e:
        logger.exception("Error: " + str(e))
        return HttpJsonResponse({'return': 'ERROR', 'error': str(e)})        
                  
def shutdownMySQLServerAgent(kwargs):
    """
    Shuts down the whole Agent together with MySQL server.
    """
    agent.stop()    
    from conpaas.mysql.server.agent.server import agentServer
    agentServer.shutdown()
    import sys
    sys.exit(0)
    
@expose('POST')
def stop_server(params):
    """
    Stops the MySQL server. Calls to :py:meth:`MySQLServer.stop`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

         return HttpJsonResponse({'return': 'ERROR', 'error': str(e)})
         
    :returns: HttpJsonResponse
    """
    logger.debug("Entering stop_server")
    try:
        agent.stop()
        logger.debug("Leaving stop_server")
        return HttpJsonResponse ({'return':'OK'})
    except Exception as e:
        ex = AgentException(E_UNKNOWN, 'stop_server', detail=e)
        logger.exception(e)
        logger.debug('Leaving stop_server')
        return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})

@expose('POST')
def restart_server(params):
    """
    Restarts the MySQL server. Calls to :py:meth:`MySQLServer.restart`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

         return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})
         
    :returns: HttpJsonResponse
    """
    
    logger.debug("Entering restart_server")
    try:
        agent.restart()
        logger.debug("Leaving restart_server")
        return HttpJsonResponse ({'return':'OK'})
    except Exception as e:
        ex = AgentException(E_UNKNOWN, 'restart_server', detail=e)
        logger.exception(e)
        logger.debug('Leaving restart_server')
        return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})

@expose('GET')
def get_server_state(params):
    """
    Gets the MySQL server state. Calls to :py:meth:`MySQLServer.status`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': status})
         
    if Exception was raised returns:

    .. code-block:: python

        return HttpJsonResponse({'return': status})
         
    :returns: HttpJsonResponse
    :raises: AgentException
    """
    
    logger.debug("Entering get_server_state")
    try: 
        status = agent.status()
        logger.debug("Leaving get_server_state")
        return HttpJsonResponse({'return': status})
    except Exception as e:
        ex = AgentException(E_UNKNOWN, 'get_server_state', detail=e)
        logger.exception(e)
        logger.debug('Leaving get_server_state')
        return HttpJsonResponse({'return': status})
    
@expose('POST')
def set_server_configuration(params):
    logger.debug("Entering set_server_configuration")
    try:
        agent.config.change_config(params['section'], params['id_param'], params["value"])
        restart_server(None)
        logger.debug("Leaving set_server_configuration")
        return HttpJsonResponse ({'return':'OK'})
    except Exception as e:
        ex = AgentException(E_UNKNOWN, 'set_server_configuration', detail=e)
        logger.exception(e)
        logger.debug('Leaving set_server_configuration')
        return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})  

@expose('POST')
def configure_user(params):
    """
    Configures the new MySQL server user. Calls to :py:meth:`MySQLServerConfiguration.add_user_to_MySQL`. If no Exception was raised returns:
    
    .. code-block:: python

        return HttpJsonResponse ({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

        return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message}) 
         
    :param username: Username for the new user.
    :param type: str
    :param password: Password for the new user.
    :param type: str
    :returns: HttpJsonResponse
    :raises: AgentException
    """
    logger.debug("Entering configure_user")
    if 'username' not in params: return HttpErrorResponse(AgentException(E_ARGS_MISSING,'username missing' ,'configure_user').message)
    username = params.pop('username')
    if 'password' not in params: return HttpErrorResponse(AgentException(E_ARGS_MISSING,'password missing' ,'configure_user').message)
    password = params.pop('password')
    if len(params) != 0:
        return HttpErrorResponse(AgentException(E_ARGS_UNEXPECTED,'too many parameters', AgentException.keys()).message)
    try:
        logger.debug("configuring new user " + username)
        agent.config.add_user_to_MySQL(username, password)
        logger.debug("Leaving configure_user")
        return HttpJsonResponse ({'return': 'OK'})
    except MySQLdb.Error, e:
        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        logger.exception(ex.message) 
        return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})  
    
@expose('POST')
def delete_user(params):
    """
    Deletes a user from MySQL server. Calls to :py:meth:`MySQLServerConfiguration.remove_user_to_MySQL`. If no Exception was raised returns:
    
    .. code-block:: python

        return HttpJsonResponse ({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

        return HttpJsonResponse({'return': 'ERROR', 'error': ex.message}) 
         
    :param username: Username for the user that will be removed.
    :param type: str
    :returns: HttpJsonResponse
    :raises: AgentException
    
    """    
    
    logger.debug("Entering delete_user")
    if len(params) != 1:
        ex = AgentException(E_ARGS_UNEXPECTED, params)
        logger.exception(ex.message) 
        return HttpJsonResponse({'return': 'ERROR', 'error': ex.message})  
    try:
        agent.config.remove_user_to_MySQL(params['username'])
        logger.debug("Leaving delete_user")
        HttpJsonResponse({'return': 'OK'})
    except MySQLdb.Error, e:
        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        logger.exception(ex.message) 
        return HttpJsonResponse({'return': 'ERROR', 'error': ex.message})  
    
@expose('GET')
def get_all_users(params):
    """
    Gets all configured users. Calls to :py:meth:`MySQLServerConfiguration.get_users_in_MySQL`. If no Exception was raised returns:
    
    .. code-block:: python

        return HttpJsonResponse ({'return': 'OK'})
         
    if AgentException was raised returns:

    .. code-block:: python

        return HttpJsonResponse( {'users': 'ERROR', 'error': ex.message}) 
         
    :param username: Username for the user that will be removed.
    :param type: str
    :returns: HttpJsonResponse ({'users': ret})
    :raises: AgentException    
    """    
    
    logger.debug("Entering get_all_users")
    try:
        ret = agent.config.get_users_in_MySQL()
        logger.debug("Got response: " + str(ret))
        logger.debug("Leaving get_all_users")
        return HttpJsonResponse({'users': ret})        
    except MySQLdb.Error, e:
        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        logger.exception(ex.message) 
        return HttpJsonResponse( {'users': 'ERROR', 'error': ex.message}) 

@expose('UPLOAD')
def create_with_MySQLdump(params):
    """
    Executes SQL clauses send as a file `params` . Calls to :py:meth:`MySQLServerConfiguration.create_MySQL_with_dump`.
              
    :param params: File containing SQL clauses.
    :param type: str
    :returns: HttpJsonResponse
    :raises: AgentException    
    """  
    
    logger.debug("Entering create_with_MySQLdump")
    file=params['mysqldump']
    f=file.file
    #f = params['mysqldump']['file']
    ret = agent.config.create_MySQL_with_dump(f)
    return ret

@expose('POST')
def set_up_replica_master(params):
    """
    Sets up a replica master. 
             
    :param username: Username for the user that will be removed.
    :param type: str
    :returns: HttpJsonResponse({'opState': 'OK'}  )
    :raises: AgentException    
    """  
    
    agent.stop()
    path=agent.config.mycnf_filepath
    file = open(path)
    content = file.read()
    #mysqlconfig = ConfigParser.RawConfigParser(allow_no_value=True)               
    #mysqlconfig.readfp(io.BytesIO(content))
    #mysqlconfig.set("mysqld", "server-id", "1")
    #mysqlconfig.set("mysqld", "log_bin", "/var/log/mysql/mysql-bin.log")
    mysqlconfig = MySQLConfig(); 
    mysqlconfig.config_file = agent.config.mycnf_filepath
    mysqlconfig.set("mysqld", "server-id", "1")
    mysqlconfig.set("mysqld", "log_bin", "/var/log/mysql/mysql-bin.log")
    mysqlconfig.save()
    file.close()
    os.remove(path)
    newfile=open(path,"w")
    #mysqlconfig.write(newfile)
    newfile.close()
    position = agent.config.replication_record_the_position()
    return {'opState': 'OK'}


@expose('POST')
def set_up_replica_slave(params):
    """
    Sets up a replica slave node.

    1)Change server id in the my.cnf. 

    2)You will need to configure the slave with settings 
    for connecting to the master, such as the host name, login credentials, and binary 
    log file name and position. See Section 15.1.1.10, Setting the Master Configuration 
    on the Slave. 
    
    Example:
        mysql>CHANGE MASTER TO  MASTER_HOST='vm-10-1-0-10', MASTER_USER='root', 
        MASTER_PASSWORD='topole48', MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS=106;
    
    :param master_host: hostname of the master node.
    :param master_log_file: filename of the master log.
    :param master_log_pos: position of the master log file.
    :param slave_server_id: id which will be written into my.cnf.
           
    :returns: HttpJsonResponse({'opState': 'OK'}  )
    :raises: AgentException     
    """

    logger.debug('Entering set_up_replica_slave')
    if len(params) != 4:
        ex = AgentException(E_ARGS_UNEXPECTED, params)
        logger.exception(ex.message) 
        return {'opState': 'ERROR', 'error': ex.message}  
    agent.config.set_up_replication_slave(params['master_host'], 
                                          params['master_log_file'],
                                          params['master_log_pos'],
                                          params['slave_server_id'])
    logger.debug('Entering set_up_replica_slave')
    return {'opState': 'OK'}    
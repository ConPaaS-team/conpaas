# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import os, socket
import ConfigParser
import MySQLdb

from os.path import devnull, exists
from os import kill
from subprocess import Popen

from conpaas.core.log import create_logger

S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'

sql_logger = create_logger(__name__)

class MySQLServer(object):
    """
    Holds configuration of the MySQL server.
    """

    def __init__(self, config):
        """
        Creates a configuration from `config`. 
        
        :param config: Configuration read with ConfigParser.
        :type config: ConfigParser
        :param  _dummy_config: Set to `True` when used in unit testing.
        :type boolean: boolean value.
        """
        sql_logger.debug("Entering init MySQLServerConfiguration")
        try:
            hostname = socket.gethostname()

            # Get connection settings
            self.pid_file = "/var/lib/mysql/" + hostname + ".pid"
            sql_logger.debug("Trying to get params from configuration file ")        
            self.conn_location = config.get('MySQL_root_connection', 'location')
            self.conn_username = config.get("MySQL_root_connection", "username")
            self.conn_password = config.get("MySQL_root_connection", "password")
            sql_logger.debug("Got parameters for root connection to MySQL")

            # Get MySQL configuration parameters
            self.mysqldump_path = config.get('agent', 'MYSQLDUMP_PATH')
            self.mycnf_filepath = config.get("MySQL_configuration","my_cnf_file")
            self.path_mysql_ssr = config.get("MySQL_configuration","path_mysql_ssr")
            # We need to remove the bind-address option (the default one is 
            # 127.0.0.1 = accepting conections only on local interface)
            #ConfigParser can't be used for my.cnf because of options without value, thus:
            f = open(self.mycnf_filepath, "r")
            lines = f.readlines()
            f.close()
            f = open(self.mycnf_filepath, "w")
            for line in lines:
                if not "bind-address" in line:
                    f.write(line)
                if "expire_logs_days" in line:
                    f.write("log_error=/root/mysql.log\n")
            f.close()

            self.wsrep_filepath = config.get("Galera_configuration","wsrep_file")
            self.wsrep_user = config.get("Galera_configuration","wsrep_sst_username")
            self.wsrep_password = config.get("Galera_configuration","wsrep_sst_password")
            self.wsrep_provider = config.get("Galera_configuration", "wsrep_provider")
            self.wsrep_sst_method = config.get("Galera_configuration","wsrep_sst_method")
            self.wsrepconfig = ConfigParser.ConfigParser()
            self.wsrepconfig.optionxform=str # to preserve case in option names
            self.wsrepconfig.read(self.wsrep_filepath)

        except ConfigParser.Error:
            sql_logger.exception('Could not read config file')
        except IOError:
            sql_logger.exception('Config file doesn\'t exist')

        # Creating a supervisor object
        sql_logger.debug("Leaving init MySQLServerConfiguration")

    def _load_dump(self, f):
        sql_logger.debug("Entering load_dump")
        try:
            mysqldump = f.read()
            d = open('/tmp/mysqldump.db', 'w')
            d.write(mysqldump)
            d.close()
            os.system("mysql -u root  -p"  + self.conn_password + " < /tmp/mysqldump.db")
            #os.system('rm /tmp/mysqldump.db')
            sql_logger.debug("Leaving load_dump")
        except Exception as e:
            sql_logger.exception('Failed to load dump')
            raise e

    def start(self):
        # Note: There seems to be a bug in the debian/mysql package. Sometimes, mysql says it
        # failed to start, even though it started - mysql conpaas service tries to restart myql server
        # three times if this error is reported, but when testing Galera this led into "address 
        # already in use" because mysql service was started
        self.state = S_STARTING
        devnull_fd = open(devnull, 'w')
        proc = Popen([self.path_mysql_ssr, "start"], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        proc.wait()
        sql_logger.debug('Mysql server started')
        self.state = S_RUNNING

    def stop(self):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            if exists(self.pid_file):
                try:
                    pid = int(open(self.pid_file, 'r').read().strip())
                except IOError as e:
                    sql_logger.exception('Failed to open PID file "%s"' % (self.pid_file))
                    raise e
                except (ValueError, TypeError) as e:
                    sql_logger.exception('PID in "%s" is invalid' % (self.pid_file))
                    raise e
	    
                try:
                    kill(pid, self.stop_sig)
                    self.state = S_STOPPED
                    sql_logger.info('mysqld stopped')
                except (IOError, OSError) as e:
                    sql_logger.exception('Failed to kill mysqld PID=%d' % (pid))
                    raise e
            else:
                sql_logger.critical('Could not find PID file %s to kill mysqld' % (self.pid_file))
                raise IOError('Could not find PID file %s to kill mysqld' % (self.pid_file))
        else:
            sql_logger.warning('Request to kill mysqld while it is not running')

    def restart(self):
        sql_logger.debug("Entering MySQLServer restart")
        try:
            devnull_fd = open(devnull, 'w')
            sql_logger.debug('Restarting with arguments:' + self.config.path_mysql_ssr + " restart")
            proc = Popen([self.path_mysql_ssr, "restart"] , stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
            sql_logger.debug("Restarting mysql server")
            proc.wait()                            
            if exists(self.pid_file) == False:
                sql_logger.critical('Failed to restart mysql server.)')
                raise OSError('Failed to restart mysql server.')
            self.state = S_RUNNING
            sql_logger.info('MySQL restarted')          
        except IOError as e:
            sql_logger.exception('Failed to open PID file "%s"' % (self._current_pid_file(increment=-1)))
            self.state = S_STOPPED
            raise e
        except (ValueError, TypeError) as e:
            sql_logger.exception('PID in "%s" is invalid' % (self._current_pid_file(increment=-1)))
            self.state = S_STOPPED
            raise e    
        sql_logger.debug("Leaving MySQLServer restart")
        
    

class MySQLMaster(MySQLServer):
    ''' Class describing a MySQL replication master. 
        It can be initializad with a dump, or without '''

    def __init__(self, config=None, master_server_id=0, dump=None):
        sql_logger.debug("Entering init MySQLServerConfiguration")
        MySQLServer.__init__(self, config)
        
        path = self.wsrep_filepath
        self.wsrepconfig.set("mysqld", "wsrep_cluster_address", "\"gcomm://\"")
        self.wsrepconfig.set("mysqld", "wsrep_provider", self.wsrep_provider)
        self.wsrepconfig.set("mysqld", "wsrep_sst_method", self.wsrep_sst_method)
        self.wsrepconfig.set("mysqld", "wsrep_sst_auth", "%s:%s" % (self.wsrep_user, self.wsrep_password))
        os.remove(path)
        newf = open(path,"w")
        self.wsrepconfig.write(newf)
        newf.close()
    
        # Start the replication master
        self.start()

        # Change root password - not set as installation
        os.system("mysqladmin -u root password "  + self.conn_password)

	    #TODO: add user conn_userame and grant privileges to it from any host 
        self.add_user(self.conn_username, self.conn_password)
        self.add_user(self.wsrep_user, self.wsrep_password)


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

    def take_snapshot(self):
        '''1st session
        '''
        db1 = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db1.cursor()
        exc.execute("FLUSH TABLES WITH READ LOCK;")
        '''2nd session
        '''
        db2 = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db2.cursor()
        exc.execute("SHOW MASTER STATUS;")
        rows = exc.fetchall()
        db2.close()
        i = 0
        ret = {}
        for row in rows:
            i = i+1
	    ret['position' + str(i)] = {'binfile': row[0], 'position': row[1], 'mysqldump_path': self.mysqldump_path}

	# dump everything except test?
        os.system("mysql --user=root --password=" + self.conn_password + \
                  " --batch --skip-column-names " + \
                  "--execute=\"SHOW DATABASES\" | egrep -v \"information_schema|test\" " + \
                  "| xargs mysqldump --user=root --password=" + self.conn_password + \
                  " --lock-all-tables --databases > " + self.mysqldump_path)

        exc = db1.cursor()
        exc.execute("UNLOCK TABLES;")
        db1.close()
        return ret
    
    def add_user(self, new_username, new_password):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute ("create user '" + new_username + "'@'localhost' identified by '" + new_password + "'")
        exc.execute ("grant all privileges on *.* TO '" + new_username + "'@'localhost' with grant option;")
        exc.execute ("create user '" + new_username + "'@'%' identified by '" + new_password + "'")
        exc.execute ("grant all privileges on *.* TO '" + new_username + "'@'%' with grant option;")
        exc.execute ("flush privileges;")
        db.close()

    def load_dump(self, file):
        self._load_dump(file)
   
    def remove_user(self, username):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute ("drop user '" + username +"'@'localhost'")
        exc.execute ("drop user '" + username +"'@'%'")
        exc.execute ("flush privileges;")
        db.close()
    
    def get_users(self):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
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

    def set_password(self, username, password):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute ("set password for '" + username + "'@'%' = password('" + password + "')")
        db.close()

    def status(self):
        return {'state': self.state,
                'port': self.port 
               }

class MySQLSlave(MySQLServer):
    ''' Class describing a MySQL replication slave. 
    '''
    def __init__(self, config = None, master_host = None):
        MySQLServer.__init__(self, config)
        
        path = self.wsrep_filepath
        self.wsrepconfig.set("mysqld", "wsrep_cluster_address", "gcomm://%s" % master_host)
        self.wsrepconfig.set("mysqld", "wsrep_provider", self.wsrep_provider)
        self.wsrepconfig.set("mysqld", "wsrep_sst_method", self.wsrep_sst_method)
        self.wsrepconfig.set("mysqld", "wsrep_sst_auth", self.wsrep_user + ":" + self.wsrep_password)
        os.remove(path)
        newf = open(path,"w")
        self.wsrepconfig.write(newf)
        newf.close()
  
        # Start the replication slave
        self.start()
        
    def status(self):
        return {'state': self.state,
                'port': self.port 
               }

if __name__ == "__main__":
    config_file = "/home/miha/Desktop/agent.cfg"
    #config_file = "/home/miha/Desktop/manager.cfg"
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file))
    master = MySQLMaster(config)
    
    
    
    
    

# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import os
import socket
import time
import ConfigParser
import MySQLdb

from os.path import devnull
from subprocess import Popen

from conpaas.core.log import create_logger
from conpaas.core.misc import run_cmd_code

S_INIT = 'INIT'
S_STARTING = 'STARTING'
S_RUNNING = 'RUNNING'
S_STOPPING = 'STOPPING'
S_STOPPED = 'STOPPED'
import logging 
sql_logger = create_logger(__name__)


class MySQLServer(object):
    """
    Holds configuration of the MySQL server.
    """

    class_file = 'mysqld.pickle'

    def __init__(self, config, nodes):
        """
        Creates a configuration from `config`.

        :param config: Configuration read with ConfigParser.
        :type config: ConfigParser
        :param  _dummy_config: Set to `True` when used in unit testing.
        :type boolean: boolean value.
        """

        sql_logger.debug("Entering init MySQLServerConfiguration")
        try:
            #hostname = socket.gethostname()

            # Get connection settings
            #self.pid_file = "/var/lib/mysql/" + hostname + ".pid"
            sql_logger.debug("Trying to get params from configuration file ")
            self.conn_location = config.get('MySQL_root_connection', 'location')
            self.conn_username = config.get("MySQL_root_connection", "username")
            self.conn_password = config.get("MySQL_root_connection", "password")
            sql_logger.debug("Got parameters for root connection to MySQL")

            # Get MySQL configuration parameters
            self.mysqldump_path = config.get('agent', 'MYSQLDUMP_PATH')
            self.mycnf_filepath = config.get("MySQL_configuration", "my_cnf_file")
            self.path_mysql_ssr = config.get("MySQL_configuration", "path_mysql_ssr")
            # We need to remove the bind-address option (the default one is
            # 127.0.0.1 = accepting connections only on local interface)
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

            self.wsrep_filepath = config.get("Galera_configuration", "wsrep_file")
            self.wsrep_user = config.get("Galera_configuration", "wsrep_sst_username")
            self.wsrep_password = config.get("Galera_configuration", "wsrep_sst_password")
            self.wsrep_provider = config.get("Galera_configuration", "wsrep_provider")
            self.wsrep_sst_method = config.get("Galera_configuration", "wsrep_sst_method")

            self.glbd_location = config.get("Galera_configuration", "glbd_location")

            self.wsrepconfig = ConfigParser.ConfigParser()
            self.wsrepconfig.optionxform = str  # to preserve case in option names
            self.wsrepconfig.read(self.wsrep_filepath)
            path = self.wsrep_filepath
            cluster_nodes = ','.join(nodes)
            self.wsrepconfig.set("mysqld", "wsrep_cluster_address", "\"gcomm://%s\"" % cluster_nodes)
            self.wsrepconfig.set("mysqld", "wsrep_provider", self.wsrep_provider)
            self.wsrepconfig.set("mysqld", "wsrep_sst_method", self.wsrep_sst_method)
            self.wsrepconfig.set("mysqld", "wsrep_sst_auth", "%s:%s" % (self.wsrep_user, self.wsrep_password))
            os.remove(path)
            newf = open(path, "w")
            self.wsrepconfig.write(newf)
            newf.close()

            self.state = S_STOPPED

            # Start
            self.start()

            # Change root password when starting
            is_first_node = len(nodes) == 0
            if is_first_node:
                os.system("mysqladmin -u root password " + self.conn_password)
                #TODO: add user conn_userame and grant privileges to it from any host
                self.add_user(self.conn_username, self.conn_password)
                self.add_user(self.wsrep_user, self.wsrep_password)

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
            os.system("mysql -u root  -p" + self.conn_password + " < /tmp/mysqldump.db")
            #os.system('rm /tmp/mysqldump.db')
            sql_logger.debug("Leaving load_dump")
        except Exception as e:
            sql_logger.exception('Failed to load dump')
            raise e

    def _wait_daemon_started(self):
        code = 1
        while code != 0:
            poll_cmd = "mysql -u mysql" \
                       + " -BN" \
                       + " -e \"SHOW STATUS LIKE 'wsrep_local_state_comment';\""
            sql_logger.debug("Polling mysql daemon: %s" % poll_cmd)
            out, error, code = run_cmd_code(poll_cmd)
            if code != 0:
                wait_time = 5
                sql_logger.info("MySQL daemon is not ready yet: %s %s."
                                " Returned error code %s."
                                " Retrying in %s seconds."
                                % (out, error, code, wait_time))
                time.sleep(wait_time)
            else:
                sql_logger.info("MySQL daemon is ready with state: %s" % out)

    def start(self):
        # Note: There seems to be a bug in the debian/mysql package. Sometimes, mysql says it
        # failed to start, even though it started - mysql conpaas service tries to restart myql server
        # three times if this error is reported, but when testing Galera this led into "address
        # already in use" because mysql service was started
        if self.state == S_RUNNING:
            sql_logger.warning("Ignoring a start MySQL call because state is already RUNNING.")
        else:
            self.state = S_STARTING
            devnull_fd = open(devnull, 'w')
            proc = Popen([self.path_mysql_ssr, "start"], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
            return_code = proc.wait()
            if return_code != 0:
                self.state = S_STOPPED
                raise Exception('Failed to start MySQL Galera daemon: return code is %s.' % return_code)
            self._wait_daemon_started()
            sql_logger.debug('MySQL server started')
            self.state = S_RUNNING

    def stop(self):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            try:
                proc = Popen([self.path_mysql_ssr, "stop"], close_fds=True)
                return_code = proc.wait()
                if return_code != 0:
                    self.state = S_RUNNING
                    raise Exception('Return code is %s.' % return_code)
                self.state = S_STOPPED
                sql_logger.info('Daemon mysqld stopped')
            except Exception as e:
                sql_logger.exception('Failed to stop MySQL daemon: %s' % e)
                raise e
        else:
            sql_logger.warning('Requested to stop MySQL daemon'
                               ' while it was in state %s'
                               ' when state %s was expected.'
                               % (self.state, S_RUNNING))

    def restart(self):
        sql_logger.debug("Restarting MySQLServer...")
        devnull_fd = open(devnull, 'w')
        sql_logger.debug('Restarting with arguments:' + self.path_mysql_ssr + " restart")
        proc = Popen([self.path_mysql_ssr, "restart"], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        sql_logger.debug("Restarting mysql server")
        proc.wait()
        self.state = S_RUNNING
        sql_logger.info('MySQL restarted.')

    """Before creating a data snapshot or starting
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
    """

    def take_snapshot(self):
        """1st session
        """
        db1 = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db1.cursor()
        exc.execute("FLUSH TABLES WITH READ LOCK;")
        #2nd session
        db2 = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db2.cursor()
        exc.execute("SHOW MASTER STATUS;")
        rows = exc.fetchall()
        db2.close()
        i = 0
        ret = {}
        for row in rows:
            i = i + 1
            ret['position' + str(i)] = {'binfile': row[0], 'position': row[1], 'mysqldump_path': self.mysqldump_path}

        # dump everything except test?
        os.system("mysql --user=root --password=" + self.conn_password +
                  " --batch --skip-column-names " +
                  "--execute=\"SHOW DATABASES\" | egrep -v \"information_schema|test\" " +
                  "| xargs mysqldump --user=root --password=" + self.conn_password +
                  " --lock-all-tables --databases > " + self.mysqldump_path)

        exc = db1.cursor()
        exc.execute("UNLOCK TABLES;")
        db1.close()
        return ret

    def add_user(self, new_username, new_password):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute("create user '" + new_username + "'@'localhost' identified by '" + new_password + "'")
        exc.execute("grant all privileges on *.* TO '" + new_username + "'@'localhost' with grant option;")
        exc.execute("create user '" + new_username + "'@'%' identified by '" + new_password + "'")
        exc.execute("grant all privileges on *.* TO '" + new_username + "'@'%' with grant option;")
        exc.execute("flush privileges;")
        db.close()

    def load_dump(self, dump_file):
        self._load_dump(dump_file)

    def remove_user(self, username):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute("drop user '" + username + "'@'localhost'")
        exc.execute("drop user '" + username + "'@'%'")
        exc.execute("flush privileges;")
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
            i = i + 1
            ret['info' + str(i)] = {'location': row[1], 'username': row[0]}
        return ret

    def set_password(self, username, password):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute("set password for '" + username + "'@'%' = password('" + password + "')")
        db.close()

    def getLoad (self):
        logger=logging.getLogger('__name__')
	flog=logging.FileHandler('/var/log/franco.log')
	logger.addHandler(flog)
	logger.setLevel(logging.WARNING)
	logger.error('siamo almeno a destinazione: password= %s ' % self.conn_password )
	db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute("SHOW STATUS LIKE 'wsrep_local_recv_queue_avg';")
    	result=exc.fetchone()[1]
        logger.error('siamo almeno a destinazione\nResult= %s' % result)
	db.close()
	return result

class GLBNode(object):
    """
    Class describing a Galera Load Balancer Node.
    """

    class_file = 'glbd.pickle'

    def __init__(self, config, nodes):
        sql_logger.debug('GLB: __init__: %s, %s' % (config, nodes))
        self.galera_nodes = nodes
        self.state = S_STOPPED
        self.glbd_location = config.get('Galera_configuration', 'glbd_location')
        self.start(nodes)
        

    def start(self, hosts=None):
        hosts = hosts or []
        self.state = S_STARTING
        devnull_fd = open(devnull, 'w')
        command = [self.glbd_location, "start"]
        proc = Popen(command, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        proc.wait()
        sql_logger.debug('GLB node started')
        self.state = S_RUNNING
        if hosts:
            self.add(hosts)
        

    def stop(self):
        self.state = S_STOPPING
        devnull_fd = open(devnull, 'w')
        command = [self.glbd_location, "stop"]
        proc = Popen(command, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        proc.wait()
        sql_logger.debug('GLB node stopped')
        self.state = S_STOPPED

    def add(self, hosts=None):
        hosts = hosts or []
	sql_logger.debug('GLB: try to add nodes to balance: %s' % hosts)
        if self.state != S_RUNNING:
            raise Exception("Wrong state to add nodes to GLB: state is %s, instead of expected %s." % (self.state, S_RUNNING))
        devnull_fd = open(devnull, 'w')
        command = [self.glbd_location, "add"]
        for i in hosts:
		command.extend([i])
        	proc = Popen(command, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        	proc.wait()
		command.pop()
	sql_logger.debug('GLB: added nodes to balance: %s' % hosts)

    def remove(self, hosts=None):
        hosts = hosts or []
        if self.state != S_RUNNING:
            raise Exception("Wrong state to remove nodes to GLB: state is %s, instead of expected %s." % (self.state, S_RUNNING))
        devnull_fd = open(devnull, 'w')
        command = [self.glbd_location, "remove"]
        for i in hosts:
                command.extend([i])
                proc = Popen(command, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
                proc.wait()
                command.pop()
        sql_logger.debug('GLB: removed nodes to balance: %s' % hosts)


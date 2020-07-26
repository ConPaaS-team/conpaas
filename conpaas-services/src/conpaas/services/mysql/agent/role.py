# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import os
import socket
import time
import ConfigParser
import MySQLdb

from os.path import devnull, join, lexists
from subprocess import Popen, PIPE

from conpaas.core.log import create_logger
from conpaas.core.misc import run_cmd_code, run_cmd

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

    def __init__(self, config, nodes, device_name):
        """
        Creates a configuration from `config`.

        :param config: Configuration read with ConfigParser.
        :type config: ConfigParser
        :param  _dummy_config: Set to `True` when used in unit testing.
        :type boolean: boolean value.
        """
        sql_logger.debug("Trying to Mount the device.")
        try:
            # Mount device
            self.dev_name = "/dev/%s" % device_name
            self.mount_point = "/media/GaleraDisk"
            self.mkdir_cmd = "mkdir -p %s" % self.mount_point
            self.mount(True)
        except ConfigParser.Error:
            sql_logger.warning('Could not mount the device')
        sql_logger.debug("Entering init MySQLServerConfiguration")
        try:
            #hostname = socket.gethostname()

            # Get connection settings
            #self.pid_file = "/var/lib/mysql/" + hostname + ".pid"
            sql_logger.debug("Trying to get params from configuration file ")
            self.conn_location = config.get('MySQL_root_connection', 'location')
            self.conn_username = config.get("MySQL_root_connection", "username")
            self.conn_password = config.get("MySQL_root_connection", "password") # root password
            sql_logger.debug("Got parameters for root connection to MySQL")

            # Get MySQL configuration parameters
            self.manager_ip = config.get('agent', 'MANAGER_IP')
            self.mysqldump_path = config.get('agent', 'MYSQLDUMP_PATH')
            self.var_cache = config.get('agent', 'VAR_CACHE')
            self.error_log = join(self.var_cache, 'mysql.log')
            self.mycnf_filepath = config.get("MySQL_configuration", "my_cnf_file")
            self.path_mysql_ssr = config.get("MySQL_configuration", "path_mysql_ssr")

            #Creating the MySQL directory tree in the external disk
            sql_logger.debug("Creating the MySQL directory tree in the external disk")
            run_cmd("mkdir -p %s/data/" % self.mount_point)
            run_cmd("mkdir -p %s/tmp/" % self.mount_point)
            run_cmd("cp -a /var/lib/mysql/* %s/data/" % self.mount_point)
            run_cmd("chown  -R mysql:mysql  %s/" % self.mount_point)

            # We need to remove the bind-address option (the default one is
            # 127.0.0.1 = accepting connections only on local interface)
            #ConfigParser can't be used for my.cnf because of options without value
            sql_logger.debug("Updating the MySQL configuration files")
            f = open(self.mycnf_filepath, "r")
            lines = f.readlines()
            f.close()
            f = open(self.mycnf_filepath, "w")
            for line in lines:
                if "datadir" in line:
                    f.write("datadir = %s/data/\n" % self.mount_point)
                elif "log_error" in line:
                    f.write("log_error = %s\n" % self.error_log)
                #elif "socket" in line:
                #    f.write("socket = %s/data/\n" % self.mount_point)
                elif "bind-address" in line:
                    pass
                else:
                    f.write(line)
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
            cluster_nodes = ','.join(nodes)
            self.wsrepconfig.set("mysqld", "wsrep_cluster_address", "\"gcomm://%s\"" % cluster_nodes)
            self.wsrepconfig.set("mysqld", "wsrep_provider", self.wsrep_provider)
            self.wsrepconfig.set("mysqld", "wsrep_sst_method", self.wsrep_sst_method)
            self.wsrepconfig.set("mysqld", "wsrep_sst_auth", "%s:%s" % (self.wsrep_user, self.wsrep_password))
            os.remove(self.wsrep_filepath)
            newf = open(self.wsrep_filepath, "w")
            self.wsrepconfig.write(newf)
            newf.close()

            is_first_node = len(nodes) == 0

            self.state = S_STOPPED
            # Start
            self.start(is_first_node)

            # Change root password when starting
            if is_first_node:
                os.system("mysqladmin -u root password " + self.conn_password)
                self.allow_root_connections(self.manager_ip)
                self.add_user(self.conn_username, self.conn_password)
                self.add_user(self.wsrep_user, self.wsrep_password)

        except ConfigParser.Error:
            sql_logger.warning('Could not read config file')
        except IOError:
            sql_logger.warning('Config file doesn\'t exist')

        # Creating a supervisor object
        sql_logger.debug("Leaving init MySQLServerConfiguration")

    def _load_dump(self, f):
        sql_logger.debug("Entering load_dump")
        try:
            mysqldump = f.read()
            d = open('/tmp/mysqldump.db', 'w')
            d.write(mysqldump)
            d.close()
            os.system("mysql -u root -p" + self.conn_password + " < /tmp/mysqldump.db")
            #os.system('rm /tmp/mysqldump.db')
            sql_logger.debug("Leaving load_dump")
        except Exception as e:
            sql_logger.warning('Failed to load dump')
            raise e

    def _wait_daemon_started(self, is_first_node):
        if is_first_node:
            # for the first node there is no password set yet
            password = ""
        else:
            password = "-p%s " % self.conn_password

        code = 1
        while code != 0:
            poll_cmd = ("mysql -u root %s"
                        "-BN "
                        "-e \"SHOW STATUS LIKE 'wsrep_local_state_comment';\""
                        % password)
            sql_logger.debug("Polling the MySQL daemon") #: %s" % poll_cmd)
            out, error, code = run_cmd_code(poll_cmd)
            if code != 0:
                wait_time = 5
                sql_logger.info("MySQL daemon is not ready yet: %s %s."
                                " Returned error code %s."
                                " Retrying in %s seconds."
                                % (out.strip(), error.strip(), code, wait_time))
                time.sleep(wait_time)
            else:
                sql_logger.info("MySQL daemon is ready with state: %s" % out.strip())

    def start(self, is_first_node):
        # Note: There seems to be a bug in the debian/mysql package. Sometimes, mysql says it
        # failed to start, even though it started - mysql conpaas service tries to restart myql server
        # three times if this error is reported, but when testing Galera this led into "address
        # already in use" because mysql service was started
        if self.state == S_RUNNING:
            sql_logger.warning("Ignoring a start MySQL call because state is already RUNNING.")
        else:
            self.state = S_STARTING
            sql_logger.debug('Starting the MySQL server')
            devnull_fd = open(devnull, 'w')
            proc = Popen([self.path_mysql_ssr, "start"], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
            return_code = proc.wait()
            if return_code != 0:
                self.state = S_STOPPED
                raise Exception('Failed to start MySQL daemon: return code is %s.' % return_code)
            sql_logger.info('MySQL server started, checking if it\'s ready')
            self._wait_daemon_started(is_first_node)
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
                sql_logger.warning('Failed to stop MySQL daemon: %s' % e)
                raise e
            try:
                self.unmount()
            except Exception as e:
                sql_logger.warning('Failed to unmount disk %s' % self.dev_name)
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
    position of the binary log on the main. You will
    need this information when configuring the subordinate so
    that the subordinate knows where within the binary log to
    start executing events. See Section 15.1.1.4, Obtaining
    the Replication Main Binary Log Coordinates.

    1st session
    mysql> FLUSH TABLES WITH READ LOCK;

    2nd session
    mysql > SHOW MASTER STATUS;
    record the values

    close 2nd session

    on the main
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

    def allow_root_connections(self, manager_ip):
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute("create user 'root'@'" + manager_ip + "' identified by '" + self.conn_password + "'")
        exc.execute("grant all privileges on *.* TO 'root'@'" + manager_ip + "' with grant option;")
        exc.execute("flush privileges;")
        db.close()

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
        db = MySQLdb.connect(self.conn_location, 'root', self.conn_password)
        exc = db.cursor()
        exc.execute("SHOW STATUS LIKE 'wsrep_local_recv_queue_avg';")
        result=exc.fetchone()[1]
        db.close()
        return result

    def mount(self, mkfs):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        # waiting for our block device to be available
        dev_found = False
        dev_prefix = self.dev_name.split('/')[2][:-1]

        for attempt in range(1, 11):
            sql_logger.info("MySQL node waiting for block device %s" % self.dev_name)
            if lexists(self.dev_name):
                dev_found = True
                break
            else:
                # On EC2 the device name gets changed
                # from /dev/sd[a-z] to /dev/xvd[a-z]
                if lexists(self.dev_name.replace(dev_prefix, 'xvd')):
                    dev_found = True
                    self.dev_name = self.dev_name.replace(dev_prefix, 'xvd')
                    break

            time.sleep(10)

        # create mount point
        run_cmd(self.mkdir_cmd)

        if dev_found:
            sql_logger.info("MySQL node has now access to %s" % self.dev_name)

            # prepare block device
            if mkfs:
                sql_logger.info("Creating new file system on %s" % self.dev_name)
                self.prepare_args = ['mkfs.ext4', '-q', '-m0', self.dev_name]
                proc = Popen(self.prepare_args, stdin=PIPE, stdout=devnull_fd,
                        stderr=devnull_fd, close_fds=True)

                proc.communicate(input="y") # answer interactive question with y
                if proc.wait() != 0:
                    sql_logger.critical('Failed to prepare storage device:(code=%d)' %
                            proc.returncode)
                else:
                    sql_logger.info('File system created successfully')
            else:
                sql_logger.info(
                  "Not creating a new file system on %s" % self.dev_name)
                time.sleep(10)

            # mount
            self.mount_args = ['mount', self.dev_name, self.mount_point]
            mount_cmd = ' '.join(self.mount_args)
            sql_logger.debug("Running command '%s'" % mount_cmd)
            _, err = run_cmd(mount_cmd)

            if err:
                sql_logger.critical('Failed to mount storage device: %s' % err)
            else:
                sql_logger.info("MySQL node has prepared and mounted %s" % self.dev_name)
        else:
            sql_logger.critical("Block device %s unavailable, falling back to image space"
                    % self.dev_name)

    def unmount(self):
        # kill all processes still using the volume
        sql_logger.info("Killing all processes using the storage volume")
        fuser_args = ['fuser', '-km', self.dev_name]
        fuser_cmd = ' '.join(fuser_args)
        sql_logger.debug("Running command '%s'" % fuser_cmd)
        run_cmd(fuser_cmd)

        # unmount
        sql_logger.info("Trying to unmount the storage volume")
        unmount_args = ['umount', self.dev_name]
        unmount_cmd = ' '.join(unmount_args)
        sql_logger.debug("Running command '%s'" % unmount_cmd)
        _, err = run_cmd(unmount_cmd)
        if err:
            sql_logger.critical('Failed to unmount storage device: %s' % err)
        else:
            sql_logger.info("MySQL node has succesfully unmounted %s" % self.dev_name)


class GLBNode(object):
    """
    Class describing a Galera Load Balancer Node.
    """

    class_file = 'glbd.pickle'

    def __init__(self, config, nodes, device_name=None):
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

# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from os.path import exists, join
from os import remove
from threading import Lock
import pickle

#from conpaas.core.misc import get_ip_address
from conpaas.core.agent import BaseAgent
from conpaas.services.galera.agent import role

from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse, FileUploadField
from conpaas.core.expose import expose
from conpaas.core.misc import check_arguments, is_list, is_string, is_uploaded_file

#logging
import logging

# daemons identifier
MYSQLD = 'mysqld'
GLBD = 'glbd'


class AgentException(Exception):
    pass


class GaleraAgent(BaseAgent):

    def __init__(self, config_parser):
        BaseAgent.__init__(self, config_parser)
        self.config_parser = config_parser

        self.my_ip = config_parser.get('agent', 'MY_IP')
        self.VAR_TMP = config_parser.get('agent', 'VAR_TMP')
        self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
        self.VAR_RUN = config_parser.get('agent', 'VAR_RUN')

        self.mysqld_file = join(self.VAR_TMP, 'mysqld.pickle')

        self.lock = Lock()

        # list of roles running in this agent
        self.running_roles = []

    @expose('POST')
    def start_mysqld(self, kwargs):
        """
        Start a mysqld daemon.

        Parameters
        ----------
        nodes : list of IP:port
            list of IP addresses and port of other nodes of this
            synchronization group. If empty or absent, then a new
            synchronization group will be created by Galera.
        device_name : string
            the block device where the disks are attached to
        """        
        try:
            exp_params = [('nodes', is_list, []),
                          ('device_name', is_string)]
            nodes, device_name = check_arguments(exp_params, kwargs)
            with self.lock:
                mysql_role = role.MySQLServer
                self._start(mysql_role, nodes, device_name)
                self.running_roles.append(mysql_role)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse()

    def _start(self, roleClass, nodes, device_name=None):
        if exists(roleClass.class_file):
            raise AgentException('Cannot start %s: file %s already exists.'
                                 % (roleClass, roleClass.class_file))
        p = roleClass(self.config_parser, nodes, device_name)
        try:
            fd = open(roleClass.class_file, 'w')
            pickle.dump(p, fd)
            fd.close()
        except Exception as ex:
            err_msg = "Failed to store file: %s" % ex
            self.logger.exception(err_msg)
            raise AgentException(err_msg)

    @expose('POST')
    def stop(self, kwargs):
        """
        Stop all daemons running in this agent (mysqld daemon and glbd daemon
        if any).

        No parameters.
        """
        if len(kwargs) > 0:
            self.logger.warning('Galera agent "stop" was called with arguments that will be ignored: "%s"' % kwargs)
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
            for role in self.running_roles:
                self._stop(role)
            self.running_roles = []
        except AgentException as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse()

    def _stop(self, roleClass):
        if not exists(roleClass.class_file):
            raise AgentException('Cannot stop daemon: file %s does not exist.'
                                 % roleClass.class_file)
        try:
            fd = open(roleClass.class_file, 'r')
            p = pickle.load(fd)
            fd.close()
            p.stop()
            remove(roleClass.class_file)
        except Exception as ex:
            err_msg = "Cannot stop daemon: %s" % ex
            self.logger.exception(err_msg)
            raise AgentException(err_msg)

    def _set_password(self, username, password):
        if not role.MySQLServer in self.running_roles:
            raise AgentException("Cannot set password: agent is not running a mysqld daemon.")
        try:
            fd = open(role.MySQLServer.class_file, 'r')
            p = pickle.load(fd)
            p.set_password(username, password)
            fd.close()
        except Exception as ex:
            self.logger.exception()
            raise AgentException("Cannot set password: %s" % ex)

    def _load_dump(self, dump_file):
        if not role.MySQLServer in self.running_roles:
            raise AgentException("Cannot load dump: agent is not running a mysqld daemon.")
        try:
            fd = open(role.MySQLServer.class_file, 'r')
            p = pickle.load(fd)
            p.load_dump(dump_file)
            fd.close()
        except Exception as ex:
            self.logger.exception()
            raise AgentException("Cannot load file: %s" % ex)

    @expose('POST')
    def set_password(self, kwargs):
        """
        Set a new password.

        Parameters
        ----------
        username : string
            user's identifier
        password : string
            new password
        """
        self.logger.debug('Updating password')
        try:
            exp_params = [('username', is_string),
                          ('password', is_string)]
            username, password = check_arguments(exp_params, kwargs)
            self._set_password(username, password)
            return HttpJsonResponse()
        except AgentException as ex:
            return HttpErrorResponse("%s" % ex)

    @expose('UPLOAD')
    def load_dump(self, kwargs):
        #TODO: archive the dump?
        try:
            exp_params = [('mysqldump_file', is_uploaded_file)]
            dump_file = check_arguments(exp_params, kwargs)
            self._load_dump(dump_file.file)
        except AgentException as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse()

    @expose('POST')
    def start_glbd(self, kwargs):
        """
        Start a glbd daemon (Galera Load Balancer daemon).

        Parameters
        ----------
        nodes : list of strings with format 'ip_addr:port'
            list of nodes to balance.
        """
        try:
            exp_params = [('nodes', is_list, [])]
            nodes = check_arguments(exp_params, kwargs)
            with self.lock:
                glb_role = role.GLBNode
                self._start(glb_role, nodes)
                self.running_roles.append(glb_role)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse()

    @expose('POST')
    def add_glbd_nodes(self, kwargs):
        """
        Add nodes to balance to the Galera Load Balancer.

        Parameters
        ----------
        nodes : list of strings with format 'ip_addr:port'
            list of nodes to balance.
        """
        if not role.GLBNode in self.running_roles:
            raise AgentException("Cannot add nodes: agent is not running a glbd daemon.")
        try:
            exp_params = [('nodesIp', is_list, [])]
            nodes = check_arguments(exp_params, kwargs)
	    with self.lock:
		fd = open(role.GLBNode.class_file, 'r')
                p = pickle.load(fd)
		p.add(  nodes)
                fd.close()		
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse()

    @expose('POST')
    def remove_glbd_nodes(self, kwargs):
        """
        Remove nodes to balance to the Galera Load Balancer.

        Parameters
        ----------
        nodes : list of strings with format 'ip_addr:port'
            list of nodes to balance.
        """
        if not role.GLBNode in self.running_roles:
            raise AgentException("Cannot remove nodes: agent is not running a glbd daemon.")
        try:
            exp_params = [('nodes', is_list, [])]
            nodes = check_arguments(exp_params, kwargs)
            with self.lock:
                fd = open(role.GLBNode.class_file, 'r')
                p = pickle.load(fd)
                p.remove(nodes)
                fd.close()
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse()

    @expose('GET')
    def getLoad(self, kwargs):
        """
        Returns the local load of the single nodes.

        """
	if len(kwargs) > 0:
            self.logger.warning('Galera agent "stop" was called with arguments that will be ignored: "%s"' % kwargs)
        try:
	    exp_params = []
	    check_arguments(exp_params, kwargs)
	    fd = open(role.MySQLServer.class_file, 'r')
	    p = pickle.load(fd)
	    load=p.getLoad()
            fd.close()
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        else:
            return HttpJsonResponse({
                                 'load': load 
                                     })

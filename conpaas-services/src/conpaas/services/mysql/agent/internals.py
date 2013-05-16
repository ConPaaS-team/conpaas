'''
Copyright (c) 2010-2013, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created in February, 2012

@author: alesc, aaasz
'''

from os.path import exists, join
from os import remove
from threading import Lock
import pickle

#from conpaas.core.misc import get_ip_address
from conpaas.core.agent import BaseAgent, AgentException
from conpaas.services.mysql.agent import role 

from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse, FileUploadField
from conpaas.core.expose import expose

class MySQLAgent(BaseAgent):

    def __init__(self, config_parser):
      BaseAgent.__init__(self, config_parser)
      self.config_parser = config_parser

      self.my_ip = config_parser.get('agent', 'MY_IP')
      self.VAR_TMP = config_parser.get('agent', 'VAR_TMP')
      self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
      self.VAR_RUN = config_parser.get('agent', 'VAR_RUN')

      self.master_file = join(self.VAR_TMP, 'master.pickle')
      self.slave_file = join(self.VAR_TMP, 'slave.pickle')
     
      self.master_lock = Lock()
      self.slave_lock = Lock()
     
    def _get(self, get_params, class_file, pClass):
        if not exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(class_file, 'r')
            p = pickle.load(fd)
            fd.close()
        except Exception as e:
            ex = AgentException(AgentException.E_CONFIG_READ_FAILED, 
                pClass.__name__, class_file, detail=e)
            self.logger.exception(ex.message)
            return HttpErrorResponse(ex.message)
        else:
            return HttpJsonResponse({'return': p.status()})

    def _create(self, post_params, class_file, pClass):
        if exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_EXISTS).message)
        try:
            if type(post_params) != dict:
                raise TypeError()
            self.logger.debug('Creating class')
            p = pClass(**post_params)
            self.logger.debug('Created class')
        except (ValueError, TypeError) as e:
            ex = AgentException(AgentException.E_ARGS_INVALID, detail=str(e))
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)
        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)
        else:
            try:
                self.logger.debug('Openning file %s' % class_file)
                fd = open(class_file, 'w')
                pickle.dump(p, fd)
                fd.close()
            except Exception as e:
                ex = AgentException(AgentException.E_CONFIG_COMMIT_FAILED, 
                    detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)
            else:
                self.logger.debug('Created class file')
                return HttpJsonResponse()
	    
    def _stop(self, get_params, class_file, pClass):
        if not exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            try:
                fd = open(class_file, 'r')
                p = pickle.load(fd)
                fd.close()
            except Exception as e:
                ex = AgentException(AgentException.E_CONFIG_READ_FAILED, detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)
            p.stop()
            remove(class_file)
            return HttpJsonResponse()
        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)

    ################################################################################
    #                      methods executed on a MySQL Master                      #
    ################################################################################
    def _master_get_params(self, kwargs):
        ret = {}
        if 'master_server_id' not in kwargs:
            raise AgentException(AgentException.E_ARGS_MISSING, 'master_server_id')
        ret['master_server_id'] = kwargs.pop('master_server_id')
        if len(kwargs) != 0:
            raise AgentException(AgentException.E_ARGS_UNEXPECTED, kwargs.keys())
        ret['config'] = self.config_parser
        return ret
     
    def _slave_get_params(self, kwargs):
        ret = {}
        if 'slaves' not in kwargs:
            raise AgentException(AgentException.E_ARGS_MISSING, 'slaves')
        ret = kwargs.pop('slaves')

        if len(kwargs) != 0:
            raise AgentException(AgentException.E_ARGS_UNEXPECTED, kwargs.keys())

        return ret

    # TODO: clean code
    def _perform_action(self, args):
        if not exists(self.master_file):
            return HttpErrorResponse(AgentException(AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(self.master_file, 'r')
            p = pickle.load(fd)
            func = getattr(p, method)
            if callable(func):
                ret = func(args)
            else:
                raise
            fd.close()
        except Exception as e:
            ex = AgentException(AgentException.E_CONFIG_READ_FAILED, 
			    role.MySQLMaster.__name__, self.master_file, detail=e)
            self.logger.exception(ex.message)
            raise
        else:
            return ret

    def _take_snapshot(self):
        if not exists(self.master_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(self.master_file, 'r')
            p = pickle.load(fd)
            ret = p.take_snapshot()
            fd.close()
        except Exception as e:
            ex = AgentException(AgentException.E_CONFIG_READ_FAILED, 
			    role.MySQLMaster.__name__, self.master_file, detail=e)
            self.logger.exception(ex.message)
            raise
        else:
            return ret

    def _set_password(self, username, password):
        if not exists(self.master_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(self.master_file, 'r')
            p = pickle.load(fd)
            p.set_password(username, password)
            fd.close()
        except Exception as e:
            ex = AgentException(AgentException.E_CONFIG_READ_FAILED, 
			    role.MySQLMaster.__name__, self.master_file, detail=e)
            self.logger.exception(ex.message)
            raise

    def _register_slave(self, slave_ip):
        if not exists(self.master_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(self.master_file, 'r')
            p = pickle.load(fd)
            p.register_slave(slave_ip)
            fd.close()
        except Exception as e:
            ex = AgentException(AgentException.E_CONFIG_READ_FAILED, 
			    role.MySQLMaster.__name__, self.master_file, detail=e)
            self.logger.exception(ex.message)
            raise

    def _load_dump(self, f):
        if not exists(self.master_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(self.master_file, 'r')
            p = pickle.load(fd)
            p.load_dump(f)
            fd.close()
        except Exception as e:
            ex = AgentException(AgentException.E_CONFIG_READ_FAILED, 
			    role.MySQLMaster.__name__, self.master_file, detail=e)
            self.logger.exception(ex.message)
            raise
        
    @expose('POST')
    def create_master(self, kwargs):
      """Create a replication master"""
      self.logger.debug('Creating master')
      try: 
        kwargs = self._master_get_params(kwargs)
        self.logger.debug('master server id = %s' % kwargs['master_server_id']) 
      except AgentException as e:
        return HttpErrorResponse(e.message)
      else:
        with self.master_lock:
          return self._create(kwargs, self.master_file, role.MySQLMaster)

    @expose('POST')
    def set_password(self, kwargs):
      """Create a replication master"""
      self.logger.debug('Updating password')
      try:
        if 'username' not in kwargs:
            raise AgentException(AgentException.E_ARGS_MISSING, 'username')
        username = kwargs.pop('username')
        if 'password' not in kwargs:
            raise AgentException(AgentException.E_ARGS_MISSING, 'password')
        password = kwargs.pop('password')
        if len(kwargs) != 0:
            raise AgentException(AgentException.E_ARGS_UNEXPECTED, kwargs.keys())
        self._set_password(username, password)
        return HttpJsonResponse()
      except AgentException as e:
        return HttpErrorResponse(e.message)
 
    @expose('UPLOAD')
    def load_dump(self, kwargs):
        self.logger.debug('Uploading mysql dump ') 
        self.logger.debug(kwargs) 
        #TODO: archive the dump?
        if 'mysqldump_file' not in kwargs:
             return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'mysqldump_file').message)
        file = kwargs.pop('mysqldump_file')
        if not isinstance(file, FileUploadField):
             return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_INVALID, 
                    detail='"mysqldump_file" should be a file').message)
        try:
            self._load_dump(file.file)
        except AgentException as e:
            return HttpErrorResponse(e.message)
        else:
            return HttpJsonResponse()

    @expose('GET')
    def get_master_state(self, kwargs):
      """GET state of Master"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(
            AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      with web_lock:
        return _get(kwargs, self.master_file, role.MySQLMaster)

    @expose('POST')
    def create_slave(self, kwargs):
      '''
	 Creates a slave. Steps:
             1. do a mysqldump and record position
             2. send the dump to the slave agent and let it
	        start the mysql slave
      '''
      self.logger.debug('master in create_slave ')
      ret = self._take_snapshot()

      # TODO: why multiple keys?
      for position in ret.keys():
          master_log_file = ret[position]['binfile']
          master_log_pos = ret[position]['position']
          mysqldump_path = ret[position]['mysqldump_path']
      try: 
          kwargs = self._slave_get_params(kwargs)
	  for key in kwargs:
               # TODO: Why do I receive the slave_ip in unicode??  
               slave = kwargs[key]
               self._register_slave(str(slave['ip'])) 
               from conpaas.services.mysql.agent import client
               client.setup_slave(str(slave['ip']), slave['port'], \
                             key, \
			     self.my_ip, master_log_file, \
                             master_log_pos, mysqldump_path)
               self.logger.debug('Created slave %s' % str(slave['ip']))
          return HttpJsonResponse()
      except AgentException as e:
        return HttpErrorResponse(e.message)

    ################################################################################
    #                      methods executed on a MySQL Slave                       #
    ################################################################################
    def _slave_get_setup_params(self, kwargs):
        ret = {}
        if 'mysqldump_file' not in kwargs:
             return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'mysqldump_file').message)
        file = kwargs.pop('mysqldump_file')
        if not isinstance(file, FileUploadField):
             return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_INVALID, 
                    detail='"mysqldump_file" should be a file').message)
        ret['mysqldump_file'] = file.file

        if 'master_host' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'master_host').message)
        ret['master_host'] = kwargs.pop('master_host')
  
        if 'master_log_file' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'master_log_file').message)
        ret['master_log_file'] = kwargs.pop('master_log_file')

        if 'master_log_pos' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'master_log_pos').message)
        ret['master_log_pos'] = kwargs.pop('master_log_pos')

        if 'slave_server_id' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'slave_server_id').message)
        ret['slave_server_id'] = kwargs.pop('slave_server_id')

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)
      
        ret['config'] = self.config_parser
        return ret

    @expose('UPLOAD')
    def setup_slave(self, kwargs):
        self.logger.debug('slave in setup_slave ') 
        self.logger.debug(kwargs)
        #TODO: archive the dump?
        """Create a replication Slave"""
        try:
            kwargs = self._slave_get_setup_params(kwargs)
        except AgentException as e:
            return HttpErrorResponse(e.message)
        else:
            with self.slave_lock:
                return self._create(kwargs, self.slave_file, role.MySQLSlave)

    @expose('GET')
    def get_slave_state(self, kwargs):
      """GET state of Slave"""
      if len(kwargs) != 0:
        return HttpErrorResponse(AgentException(AgentException.E_ARGS_UNEXPECTED, 
                                 kwargs.keys()).message)
      with slave_lock:
        return _get(kwargs, self.slave_file, role.MySQLSlave)

    # TODO: Update slave - if manager changes! 

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

Created May, 2012

@author Dragos Diaconescu

'''
from os.path import exists, join
from os import remove

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse
from conpaas.services.xtreemfs.agent import role    
from conpaas.core.agent import BaseAgent, AgentException

from threading import Lock
import pickle

class XtreemFSAgent(BaseAgent):
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser 
                                # (hopefully the new service won't need anything extra)
        BaseAgent.__init__(self, config_parser)
        role.init(config_parser)
        self.gen_string = config_parser.get('agent','STRING_TO_GENERATE')
        
        self.VAR_TMP = config_parser.get('agent','VAR_TMP')

        self.dir_file = join(self.VAR_TMP,'dir.pickle')
        self.mrc_file = join(self.VAR_TMP,'mrc.pickle')
        self.osd_file = join(self.VAR_TMP,'osd.pickle')
        self.mrc_lock = Lock()
        self.dir_lock = Lock()
        self.osd_lock = Lock()

        self.DIR = role.DIR
        self.MRC = role.MRC
        self.OSD = role.OSD
        
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
                self.logger.debug('dump file %s loaded' %class_file)
                fd.close()
            except Exception as e:
                ex = AgentException(
                    AgentException.E_CONFIG_READ_FAILED, detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)
            p.stop()
            remove(class_file)
            return HttpJsonResponse()
        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)


    @expose('POST')
    def createMRC(self, kwargs):
        try: 
            kwargs = self._MRC_get_params(kwargs)     
        except AgentException as e:
            return HttpErrorResponse(e.message)
        else:
            with self.mrc_lock:
                return self._create(kwargs, self.mrc_file, self.MRC)

    @expose('POST')
    def createDIR(self, kwargs):
        with self.dir_lock:
            return self._create(kwargs, self.dir_file, self.DIR)
    

    @expose('POST')
    def createOSD(self, kwargs):
        try:
            kwargs = self._OSD_get_params(kwargs)
        except AgentException as e:
            return HttpErrorResponse(e.message)
        else:
            with self.osd_lock:
                return self._create(kwargs, self.osd_file, self.OSD)

    @expose('POST')
    def stopOSD(self, kwargs):
        """Kill the OSD service"""
        with self.osd_lock:
            return self._stop(kwargs, self.osd_file, self.OSD)       

    def _MRC_get_params(self, kwargs):
        ret = {}
        if 'dir_serviceHost' not in kwargs:
            raise AgentException(
                AgentException.E_ARGS_MISSING, 'dir service host')
        ret['dir_serviceHost'] = kwargs.pop('dir_serviceHost')
        return ret
 
    def _OSD_get_params(self, kwargs):
        ret = {}
        if 'dir_serviceHost' not in kwargs:
            raise AgentException(
                AgentException.E_ARGS_MISSING, 'dir service host')
        ret['dir_serviceHost'] = kwargs.pop('dir_serviceHost')
        return ret    

    @expose('POST')
    def startup(self, kwargs):
        self.state = 'RUNNING'
        self.logger.info('Agent started up')
        return HttpJsonResponse()

    @expose('GET')
    def get_helloworld(self, kwargs):
        if self.state != 'RUNNING':
            return HttpErrorResponse('ERROR: Wrong state to get_helloworld')
        return HttpJsonResponse({'result':self.gen_string})


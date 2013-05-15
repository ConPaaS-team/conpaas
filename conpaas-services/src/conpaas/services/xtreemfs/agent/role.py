'''
Copyright (c) 2010-2012, Contrail consortium.
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
 3. Neither the name of the <ORGANIZATION> nor the
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


Created on May, 2012

@author: Dragos Diaconescu
'''

from os.path import join, devnull, exists
from os import kill, chown, setuid, setgid
from pwd import getpwnam
from signal import SIGINT, SIGTERM, SIGUSR2, SIGHUP
from subprocess import Popen
from shutil import rmtree, copy2
from Cheetah.Template import Template
from threading import Thread
from conpaas.core.misc import verify_port, verify_ip_port_list, verify_ip_or_domain
from conpaas.core.log import create_logger
from conpaas.core.https.server import HttpJsonResponse
import subprocess
import uuid

S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'

logger = create_logger(__name__)

ETC = None

def init(config_parser):
    global MRC_STARTUP,DIR_STARTUP,OSD_STARTUP,OSD_REMOVE,XTREEM_TMPL
    MRC_STARTUP = config_parser.get('mrc','MRC_STARTUP')
    DIR_STARTUP = config_parser.get('dir','DIR_STARTUP')
    OSD_STARTUP = config_parser.get('osd','OSD_STARTUP')
    OSD_REMOVE  = config_parser.get('osd','OSD_REMOVE')
    global ETC
    ETC = config_parser.get('agent','ETC')


class MRC:
    def __init__(self,dir_serviceHost = None):
        self.state = S_INIT         
        self.start_args = [MRC_STARTUP,'start']        
        self.config_template = join(ETC,'mrcconfig.properties')
        logger = create_logger(__name__)
        logger.info('MRC server initialized')
        self.uuid_nr = uuid.uuid1()
        self.configure(dir_serviceHost)
        self.start()

    def start(self):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        proc = Popen(self.start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            logger.critical('Failed to start mrc service:(code=%d)' %proc.returncode)
        logger.info('MRC Service started:') 
        self.state = S_RUNNING
    def configure(self,dir_serviceHost):
        if dir_serviceHost == None: raise TypeError('Dir service host required')
        
        self.dir_serviceHost = dir_serviceHost    
        self._write_config()
    def _write_config(self):
        tmpl = open(self.config_template).read()
        template = Template(tmpl,{
                            'dir_serviceHost' : self.dir_serviceHost,
                            'uuid' : self.uuid_nr
                        })
        conf_fd = open('/etc/xos/xtreemfs/mrcconfig.properties','w')
        conf_fd.write(str(template))
        conf_fd.close()

class DIR():
    def __init__(self):
        self.state = S_INIT         
        self.start_args = [DIR_STARTUP,'start']
        self.config_template = join(ETC,'dirconfig.properties')
        logger.info('DIR server initialized')
        self.uuid_nr = uuid.uuid1()
        self.configure()
        self.start()
    def start(self):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        proc = Popen(self.start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        
        if proc.wait() != 0:
            logger.critical('Failed to start dir service:(code=%d)' %proc.returncode)
        logger.info('DIR Service started:') 
        self.state = S_RUNNING
    def configure(self):
        self._write_config()
    def _write_config(self):
        tmpl = open(self.config_template).read()
        template = Template(tmpl,{
                            'uuid' : self.uuid_nr
                        })
        conf_fd = open('/etc/xos/xtreemfs/dirconfig.properties','w')
        conf_fd.write(str(template))
        conf_fd.close()

class OSD:
    def __init__(self,dir_serviceHost = None):
        self.state = S_INIT         
        self.config_template = join(ETC,'osdconfig.properties')
        logger.info('OSD server initialized')
        self.uuid_nr = uuid.uuid1()
        self.configure(dir_serviceHost)
        self.dir_servicePort = 32638
        self.start_args = [OSD_STARTUP,'start']
        self.stop_args = [OSD_STARTUP,'stop']
        self.remove_args = [OSD_REMOVE, '-dir ' + str(self.dir_serviceHost) + ':' + str(self.dir_servicePort), 'uuid:' + str(self.uuid_nr)]
        self.start()

    def start(self):
        self.state = S_STARTING
        devnull_fd = open(devnull,'w')
        proc = Popen(self.start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            logger.critical('Failed to start osd service:(code=%d)' %proc.returncode)
        logger.info('OSD Service started:') 
        self.state = S_RUNNING
    def configure(self,dir_serviceHost):
        if dir_serviceHost == None: raise TypeError('Dir service host required')
        self.dir_serviceHost = dir_serviceHost    
        self._write_config()
    def _write_config(self):
        tmpl = open(self.config_template).read()
        template = Template(tmpl,{
                            'dir_serviceHost' : self.dir_serviceHost,
                            'uuid' : self.uuid_nr
                        })
        conf_fd = open('/etc/xos/xtreemfs/osdconfig.properties','w')
        conf_fd.write(str(template))
        conf_fd.close()
    def stop(self):
        if self.state == S_RUNNING:
            self.state = S_STOPPING
            devnull_fd = open(devnull,'w')
            # remove (drain) OSD to avoid data loss
            logger.info('OSD Service remove commandline: ' + str(self.remove_args))
            logger.info('OSD Service stop commandline: ' + str(self.stop_args))  
            proc = Popen(self.remove_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
            if proc.wait() != 0:
                logger.critical('Failed to remove osd service:(code=%d)' %proc.returncode)
            logger.info('OSD Service removed:') 
            # stop OSD
            proc = Popen(self.stop_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
            if proc.wait() != 0:
                logger.critical('Failed to stop osd service:(code=%d)' %proc.returncode)
            logger.info('OSD Service stopped:') 
            self.state = S_STOPPED
        else:
            logger.warning('Request to stop OSD service while it is not running')      


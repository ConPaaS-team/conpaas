# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from os.path import join, devnull, lexists
from subprocess import Popen
from Cheetah.Template import Template
from conpaas.core.log import create_logger
import uuid
import time

S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'

logger = create_logger(__name__)

MRC_STARTUP = None
DIR_STARTUP = None
OSD_STARTUP = None
OSD_REMOVE = None
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

        # waiting for our block device to be available
        dev_name = "sdb"
        dev_found = False

        for attempt in range(1, 11):
            logger.info("OSD node waiting for block device %s" % dev_name)
            if lexists("/dev/%s" % dev_name):
                dev_found = True
                break

            time.sleep(10)

        if dev_found:
            logger.info("OSD node has now access to %s" % dev_name)
        else:
            logger.critical("Block device %s unavailable" % dev_name)

        logger.debug(str(self.start_args))

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


import subprocess
from conpaas.mysql.utils.log import get_logger_plus


logger, flog, mlog = get_logger_plus(__name__)

class ExecuteException(Exception):
    pass

class Execute(object):
    @mlog
    def execute(self, command, geterr=False):
        logger.info('execute: %s' % command)
        
        p = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        out, err = p.communicate()
        
        status = p.wait()
        
        if err:
            logger.debug('local err: %s' % err)
            
            if geterr:
                return err
            
            if status != 0:
                raise Exception(err)
        
        logger.debug('local out: %s' % out)
        
        return out

class RemoteExecuteSettings(object):
    ssh_user = None
    ssh_key = None
    ssh_host = None
    ssh_port = None
    ignore_host_key = None

class RemoteExecute(object):
    settings = RemoteExecuteSettings
    
    @mlog
    def execute(self, command, geterr=False):
        ignore_host_key = self.settings.ignore_host_key
        
        d = {
            'ssh_user': self.settings.ssh_user,
            'ssh_key': self.settings.ssh_key,
            'ssh_host': self.settings.ssh_host,
            'ssh_port': self.settings.ssh_port,
            'strict_host_key_checking': 'no' if ignore_host_key else 'yes',
            'cmd': command
        }
        
        remote = (u'ssh '
                    '-i "%(ssh_key)s" '
                    '-o StrictHostKeyChecking=%(strict_host_key_checking)s '
                    '-p %(ssh_port)d '
                    '%(ssh_user)s@%(ssh_host)s %(cmd)s' % d)
        
        logger.info('remote execute: %s' % remote)
        
        p = subprocess.Popen(remote, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        out, err = p.communicate()
        
        status = p.wait()
        
        if err:
            logger.debug('remote err: %s' % err)
            
            if geterr:
                return err
            
            if status != 0:
                raise ExecuteException(err)
        
        logger.debug('remote out: %s' % out)
        
        return out

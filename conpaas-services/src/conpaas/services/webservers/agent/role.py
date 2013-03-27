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


Created on Jan 21, 2011

@author: ielhelw
'''

from os.path import join, devnull, exists
from os import kill, chown, setuid, setgid
from pwd import getpwnam
from signal import SIGINT, SIGTERM, SIGUSR2, SIGHUP
from subprocess import Popen
from shutil import rmtree, copy2
from Cheetah.Template import Template

from conpaas.core.misc import verify_port, verify_ip_port_list, verify_ip_or_domain
from conpaas.core.log import create_logger

S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'

logger = create_logger(__name__)

NGINX_CMD = None
PHP_FPM = None
TOMCAT_INSTANCE_CREATE = None
TOMCAT_STARTUP = None

VAR_TMP = None
VAR_CACHE = None
VAR_RUN = None
ETC = None
MY_IP = None

def init(config_parser):
  global NGINX_CMD, PHP_FPM, TOMCAT_INSTANCE_CREATE, TOMCAT_STARTUP
  NGINX_CMD = config_parser.get('nginx', 'NGINX')
  PHP_FPM = config_parser.get('php', 'PHP_FPM')
  TOMCAT_INSTANCE_CREATE = config_parser.get('tomcat', 'TOMCAT_INSTANCE_CREATE')
  TOMCAT_STARTUP = config_parser.get('tomcat', 'TOMCAT_STARTUP')
  global VAR_TMP, VAR_CACHE, VAR_RUN, ETC, MY_IP
  VAR_TMP = config_parser.get('agent', 'VAR_TMP')
  VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
  VAR_RUN = config_parser.get('agent', 'VAR_RUN')
  ETC = config_parser.get('agent', 'ETC')
  MY_IP = config_parser.get('agent', 'MY_IP')


class Nginx:
  
  def start(self):
    self.state = S_STARTING
    devnull_fd = open(devnull, 'w')
    proc = Popen(self.start_args, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
    if proc.wait() != 0:
      logger.critical('Failed to start web server (code=%d)' % proc.returncode)
      raise OSError('Failed to start web server (code=%d)' % proc.returncode)
    self.state = S_RUNNING
    logger.info('WebServer started')
  
  def stop(self):
    if self.state == S_RUNNING:
      self.state = S_STOPPING
      if exists(self.pid_file):
        try:
          pid = int(open(self.pid_file, 'r').read().strip())
        except IOError as e:
          logger.exception('Failed to open PID file "%s"' % (self.pid_file))
          raise e
        except (ValueError, TypeError) as e:
          logger.exception('PID in "%s" is invalid' % (self.pid_file))
          raise e
        
        try:
          kill(pid, self.stop_sig)
          self.state = S_STOPPED
          logger.info('WebServer stopped')
        except (IOError, OSError) as e:
          logger.exception('Failed to kill WebServer PID=%d' % (pid))
          raise e
      else:
        logger.critical('Could not find PID file %s to kill WebServer' % (self.pid_file))
        raise IOError('Could not find PID file %s to kill WebServer' % (self.pid_file))
    else:
      logger.warning('Request to kill WebServer while it is not running')
  
  def restart(self):
    self._write_config()
    
    try:
      pid = int(open(self.pid_file, 'r').read().strip())
    except IOError as e:
      logger.exception('Failed to open PID file "%s"' % (self.pid_file))
      raise e
    except (ValueError, TypeError) as e:
      logger.exception('PID in "%s" is invalid' % (self.pid_file))
      raise e
    
    try:
      kill(pid, SIGHUP)
    except (IOError, OSError):
      logger.exception('Failed to "gracefully" kill WebServer PID=%d' % (pid))
      raise e
    else:
      self.post_restart()
      logger.info('WebServer restarted')
  
  def post_restart(self): pass


class NginxStatic(Nginx):
  def __init__(self, port=None, code_versions=None):
    self.cmd = NGINX_CMD
    self.config_template = join(ETC, 'nginx-static.tmpl')
    self.state = S_INIT
    self.configure(port=port, code_versions=code_versions)
    self.start()
    self.stop_sig = SIGINT
  
  def configure(self, port=None, code_versions=None):
    verify_port(port)
    self.port = port
    if not isinstance(code_versions, list):
      raise TypeError('code_versions should be a list of strings')
    for i in code_versions:
      if not isinstance(i, basestring):
        raise TypeError('code_versions should be a list of strings')
    
    self.code_versions = code_versions
    if self.state == S_INIT:
      self.config_file = join(VAR_CACHE, 'nginx-static.conf')
      self.access_log = join(VAR_CACHE, 'nginx-static-access.log')
      self.timed_log = join(VAR_CACHE, 'nginx-static-timed.log')
      self.error_log = join(VAR_CACHE, 'nginx-static-error.log')
      self.pid_file = join(VAR_RUN, 'nginx-static.pid')
      self.user = 'www-data'
    self._write_config()
    self.start_args = [self.cmd, '-c', self.config_file]
  
  def _write_config(self):
    tmpl = open(self.config_template).read()
    template = Template(tmpl,
                        {
                         'user'         : self.user,
                         'port'         : self.port,
                         'error_log'    : self.error_log,
                         'access_log'   : self.access_log,
                         'timed_log'    : self.timed_log,
                         'pid_file'     : self.pid_file,
                         'doc_root'     : join(VAR_CACHE, 'www'),
                         'code_versions': self.code_versions})
    conf_fd = open(self.config_file, 'w')
    conf_fd.write(str(template))
    conf_fd.close()
    logger.debug('web server configuration written to %s' % (self.config_file))
    
  def status(self):
    return {'state': self.state,
    'port': self.port,
    'code_versions': self.code_versions}


class NginxProxy(Nginx):
  
  def __init__(self, port=None, code_version=None, cdn=None, web_list=[], fpm_list=[], tomcat_list=[], tomcat_servlets=[]):
    self.cmd = NGINX_CMD
    self.config_template = join(ETC, 'nginx-proxy.tmpl')
    self.state = S_INIT
    self.configure(port=port, code_version=code_version, cdn=cdn, web_list=web_list, fpm_list=fpm_list, tomcat_list=tomcat_list, tomcat_servlets=tomcat_servlets)
    self.start()
    self.stop_sig = SIGINT
  
  def _write_config(self):
    tmpl = open(self.config_template).read()
    conf_fd = open(self.config_file, 'w')
    template = Template(tmpl, {
                               'user'             : self.user,
                               'port'             : self.port,
                               'error_log'        : self.error_log,
                               'access_log'       : self.access_log,
                               'timed_log'        : self.timed_log,
                               'pid_file'         : self.pid_file,
                               'doc_root'         : join(VAR_CACHE, 'www'),
                               'code_version'     : self.codeversion,
                               'proxy_ip'         : MY_IP,
                               'web_list'         : self.web_list,
                               'fpm_list'         : self.fpm_list,
                               'tomcat_list'      : self.tomcat_list,
                               'tomcat_servlets'  : self.tomcat_servlets,
                               'cdn'              : self.cdn,
                               })
    conf_fd.write(str(template))
    conf_fd.close()
    logger.debug('Load Balancer configuration written to %s' % (self.config_file))
  
  def configure(self, port=None, code_version=None, cdn=None, web_list=[], fpm_list=[], tomcat_list=[], tomcat_servlets=[]):
    verify_port(port)
    port = int(port)
    verify_ip_port_list(web_list)
    verify_ip_port_list(fpm_list)
    verify_ip_port_list(tomcat_list)
    if self.state == S_INIT:
      self.config_file = join(VAR_CACHE, 'nginx-proxy.conf')
      self.access_log = join(VAR_CACHE, 'nginx-proxy-access.log')
      self.timed_log = join(VAR_CACHE, 'nginx-proxy-timed.log')
      self.error_log = join(VAR_CACHE, 'nginx-proxy-error.log')
      self.pid_file = join(VAR_RUN, 'nginx-proxy.pid')
      self.user = 'www-data'
    self.port = port
    self.codeversion = code_version
    self.cdn = cdn
    self.web_list = web_list
    self.fpm_list = fpm_list
    self.tomcat_list = tomcat_list
    self.tomcat_servlets = tomcat_servlets
    self._write_config()
    self.start_args = [self.cmd, '-c', self.config_file]
  
  def status(self):
    return {'state': self.state,
            'port': self.port,
            'code_version': self.codeversion,
            'cdn': self.cdn,
            'web_list': self.web_list,
            'fpm_list': self.fpm_list,
            'tomcat_list': self.tomcat_list,
            'tomcat_servlets': self.tomcat_servlets,
            }


class Tomcat6:
  
  def __init__(self, tomcat_port=None):
    self.config_template = join(ETC, 'tomcat-server-xml.tmpl')
    self.instance_dir = join(VAR_CACHE, 'tomcat_instance')
    self.config_file = join(self.instance_dir, 'conf', 'server.xml')
    self.start_args = [TOMCAT_STARTUP, '-security']
    self.shutdown_args = [join(self.instance_dir, 'bin', 'shutdown.sh')]
    verify_port(tomcat_port)
    devnull_fd = open(devnull, 'w')
    proc = Popen([TOMCAT_INSTANCE_CREATE, '-p', str(tomcat_port), self.instance_dir], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
    if proc.wait() != 0:
      logger.critical('Failed to initialize tomcat (code=%d)' % proc.returncode)
      raise OSError('Failed to initialize tomcat (code=%d)' % proc.returncode)
    try: self.www_user = getpwnam('www-data')
    except KeyError:
      logger.exception('Failed to find user id of www-data')
      raise OSError('Failed to find user id of www-data')
    for child in ['logs', 'temp', 'work']:
      try:
        chown(join(self.instance_dir, child), self.www_user.pw_uid, self.www_user.pw_gid)
      except OSError:
        logger.exception('Failed to change ownership of %s' % child)
        raise
    self.state = S_INIT
    self.configure(tomcat_port=tomcat_port)
    self.start()
  
  def configure(self, tomcat_port=None):
    if tomcat_port == None: raise TypeError('tomcat_port is required')
    self.port = tomcat_port
    tmpl = open(self.config_template).read()
    template = Template(tmpl, {'port': self.port})
    fd = open(self.config_file, 'w')
    fd.write(str(template))
    fd.close()
    copy2(join(ETC, 'tomcat-catalina.policy'),
          join(self.instance_dir, 'work', 'catalina.policy'))
  
  def demote(self):
    setgid(self.www_user.pw_gid)
    setuid(self.www_user.pw_uid)
  
  def restart(self): pass
  
  def start(self):
    self.state = S_STARTING
    devnull_fd = open(devnull, 'w')
    proc = Popen(self.start_args, env={'CATALINA_BASE': self.instance_dir},
                 preexec_fn=self.demote, # run tomcat under user www-data
                 stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
    if proc.wait() != 0:
      logger.critical('Failed to start tomcat (code=%d)' % proc.returncode)
      raise OSError('Failed to start tomcat (code=%d)' % proc.returncode)
    self.state = S_RUNNING
    logger.info('Tomcat started')
  
  def stop(self):
    if self.state == S_RUNNING:
      self.state = S_STOPPING
      devnull_fd = open(devnull, 'w')
      proc = Popen(self.shutdown_args, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
      if proc.wait() != 0:
        logger.critical('Failed to stop tomcat (code=%d)' % proc.returncode)
        raise OSError('Failed to stop tomcat (code=%d)' % proc.returncode)
      self.state = S_STOPPED
      logger.info('Tomcat stopped')
      rmtree(self.instance_dir, ignore_errors=True)
    else:
      logger.warning('Request to kill tomcat while it is not running')
  
  def status(self):
    return {'state': self.state}
  

class PHPProcessManager:
  
  def __init__(self, port=None, scalaris=None, configuration=None):
    self.config_template = join(ETC, 'fpm.tmpl')
    self.cmd = PHP_FPM
    self.state = S_INIT
    self.configure(port=port, scalaris=scalaris, configuration=configuration)
    self.start()
  
  def configure(self, port=None, scalaris=None, configuration=None):
    if port == None: raise TypeError('port is required')
    verify_port(port)
    verify_ip_or_domain(scalaris)
    if configuration and not isinstance(configuration, dict):
      raise TypeError('configuration is not a dict')
    if self.state == S_INIT:
      self.scalaris_config = join(VAR_CACHE, 'fpm-scalaris.conf')
      self.config_file = join(VAR_CACHE, 'fpm.conf')
      self.error_log = join(VAR_CACHE, 'fpm-error.log')
      self.access_log = join(VAR_CACHE, 'fpm-access.log')
      self.pid_file = join(VAR_RUN, 'fpm.pid')
      self.user = 'www-data'
      self.group = 'www-data'
      self.max_children = 1
      self.max_requests = 100
      self.servers_start = 1
      self.servers_spare_min = 1
      self.servers_spare_max = 1
      self.scalaris = scalaris
    tmpl = open(self.config_template).read()
    fd = open(self.config_file, 'w')
    template = Template(tmpl, {
                               'pid_file':          self.pid_file,
                               'error_log':         self.error_log,
                               'port':              port,
                               'user':              self.user,
                               'group':             self.group,
                               'access_log':        self.access_log,
                               'max_children':      self.max_children,
                               'max_requests':      self.max_requests,
                               'servers_start':     self.servers_start,
                               'servers_spare_min': self.servers_spare_min,
                               'servers_spare_max': self.servers_spare_max,
                               'properties':        configuration})
    fd.write(str(template))
    fd.close()
    
    fd = open(self.scalaris_config, 'w')
    fd.write("http://%s:8000/jsonrpc.yaws" % (scalaris))
    fd.close()
    self.port = port
    self.configuration = configuration
  
  def start(self):
    self.state = S_STARTING
    devnull_fd = open(devnull, 'w')
    proc = Popen([self.cmd, '--fpm-config', self.config_file], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
    if proc.wait() != 0:
      logger.critical('Failed to start the php-fpm')
      raise OSError('Failed to start the php-fpm')
    self.state = S_RUNNING
    logger.info('php-fpm started')
  
  def stop(self):
    if self.state == S_RUNNING:
      self.state = S_STOPPING
      if exists(self.pid_file):
        try:
          pid = int(open(self.pid_file, 'r').read().strip())
        except IOError as e:
          logger.exception('Failed to open PID file "%s"' % (self.pid_file))
          raise e
        except (ValueError, TypeError) as e:
          logger.exception('PID in "%s" is invalid' % (self.pid_file))
          raise e
        try:
          kill(pid, SIGTERM)
          self.state = S_STOPPED
          logger.info('php-fpm stopped')
        except (IOError, OSError) as e:
          logger.exception('Failed to kill php-fpm PID=%d' % (pid))
          raise e
      else:
        logger.critical('Could not find PID file %s to kill php-fpm' % (self.pid_file))
        raise IOError('Could not find PID file %s to kill php-fpm' % (self.pid_file))
    else:
      logger.warning('Request to kill php-fpm while it is not running')
  
  def restart(self):
    if self.state != S_RUNNING:
      logger.warning('php-fpm not running in order to restart')
    if exists(self.pid_file):
      try:
        pid = int(open(self.pid_file, 'r').read().strip())
      except IOError as e:
        logger.exception('Failed to open PID file "%s"' % (self.pid_file))
        raise e
      except (ValueError, TypeError) as e:
        logger.exception('PID in "%s" is invalid' % (self.pid_file))
        raise e
      try:
        ## Graceful restart for PHP-FPM: send it a SIGUSR2.
        ## It will reload the same configuration file and apply the changes.
        ## The new PID value will be written to the same PID file.
        kill(pid, SIGUSR2)
      except (IOError, OSError) as e:
        logger.exception('Failed to kill php-fpm PID=%d' % (pid))
        raise e
    else:
      logger.critical('Could not find PID file %s to restart php-fpm' % (self.pid_file))
      raise IOError('Could not find PID file %s to restart php-fpm' % (self.pid_file))
  
  def status(self):
    return {'state': self.state, 'port': self.port}


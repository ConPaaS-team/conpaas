'''
Created on Jan 21, 2011

@author: ielhelw
'''

from os.path import join, devnull, exists
from os import kill, makedirs
from signal import SIGINT, SIGTERM, SIGUSR2, SIGHUP
from string import Template
from subprocess import Popen


from conpaas.web.misc import verify_port, verify_ip_port_list, verify_ip_or_domain
from conpaas.log import create_logger

S_INIT        = 'INIT'
S_STARTING    = 'STARTING'
S_RUNNING     = 'RUNNING'
S_STOPPING    = 'STOPPING'
S_STOPPED     = 'STOPPED'

logger = create_logger(__name__)

class BaseWebServer:
  
  def __init__(self, doc_root, port, php, stop_sig):
    '''Creates a new WebServer object.
    
    doc_root: filesystem path where the webserver should serve documents from.
    port: port to wich the web server listens for incoming connections.
    php: list of [IP, PORT] values of the backend PHP processes.
    '''
    self.state = S_INIT
    self.restart_count = 0
    self.configure(doc_root, port, php)
    self.start()
    self.stop_sig = stop_sig
  
  def _current_pid_file(self, increment=0):
    return self.pid_file
  
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
      if exists(self._current_pid_file()):
        try:
          pid = int(open(self._current_pid_file(), 'r').read().strip())
        except IOError as e:
          logger.exception('Failed to open PID file "%s"' % (self._current_pid_file()))
          raise e
        except (ValueError, TypeError) as e:
          logger.exception('PID in "%s" is invalid' % (self._current_pid_file()))
          raise e
        
        try:
          kill(pid, self.stop_sig)
          self.state = S_STOPPED
          logger.info('WebServer stopped')
        except (IOError, OSError) as e:
          logger.exception('Failed to kill WebServer PID=%d' % (pid))
          raise e
      else:
        logger.critical('Could not find PID file %s to kill WebServer' % (self._current_pid_file()))
        raise IOError('Could not find PID file %s to kill WebServer' % (self._current_pid_file()))
    else:
      logger.warning('Request to kill WebServer while it is not running')
  
  def restart(self):
    self.restart_count += 1
    self._write_config()
    
    try:
      pid = int(open(self._current_pid_file(increment=-1), 'r').read().strip())
    except IOError as e:
      logger.exception('Failed to open PID file "%s"' % (self._current_pid_file(increment=-1)))
      raise e
    except (ValueError, TypeError) as e:
      logger.exception('PID in "%s" is invalid' % (self._current_pid_file(increment=-1)))
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
  
  def status(self):
    return {'state': self.state,
    'doc_root': self.doc_root,
    'port': self.port,
    'php': self.php}


class Nginx(BaseWebServer):
  CONF_TEMPLATE = '''
user ${USER};
worker_processes  1;

error_log  ${ERROR_LOG};
pid        ${PID_FILE};

events {
  worker_connections  1024;
  # multi_accept on;
}

http {
  include       /conpaas/etc/nginx/mime.types;
  access_log  ${ACCESS_LOG};
  sendfile        on;
  #tcp_nopush     on;
  #keepalive_timeout  0;
  keepalive_timeout  65;
  tcp_nodelay        on;
  gzip  on;
  gzip_disable "MSIE [1-6]\.(?!.*SV1)";

${FCGI}
  
  server {
    listen       ${PORT} default;
    root           ${DOC_ROOT}/$$http_conpaasversion;
    server_name  localhost;
    port_in_redirect off;
    
    if ( $$document_root = '${DOC_ROOT}/' ) {
      return 404;
    }
    
    location    / {
      index         index.html index.htm index.php;
    }
    ${PHP_HANDLER}
  }
}
  '''
  
  cmd = '/conpaas/sbin/nginx'
  
  def __init__(self, doc_root=None, port=None, php=None):
    BaseWebServer.__init__(self, doc_root, port, php, SIGINT)
  
  def _write_config(self):
    '''Write configuration file.'''
    fcgi_conf = ''
    php_handler = ''
    if self.php:
      fcgi_conf = 'upstream backend {\n'
      for f in self.php:
        fcgi_conf += 'server %s:%d;\n' % (f[0], f[1])
      fcgi_conf += '}\n'
      php_handler = '''
      location ~ \.php$ {
      include         /conpaas/etc/nginx/fastcgi_params;
      fastcgi_param  SCRIPT_FILENAME $document_root$fastcgi_script_name;
      fastcgi_pass    backend;
    }'''
    
    template = Template(self.CONF_TEMPLATE)
    conf_fd = open(self.config_file, 'w')
    conf_fd.write(template.substitute(DOC_ROOT=self.doc_root,
                        ACCESS_LOG=self.access_log, ERROR_LOG=self.error_log,
                        PID_FILE=self._current_pid_file(),
                        USER=self.user, PORT=self.port, FCGI=fcgi_conf, PHP_HANDLER=php_handler))
    conf_fd.close()
    logger.debug('WebServer configuration written to %s' % (self.config_file))
  
  def configure(self, doc_root=None, port=None, php=None):
    port = int(port)
    if doc_root == None: raise TypeError('doc_root is required')
    if port == None: raise TypeError('port is required')
    if type(doc_root) != str and type(doc_root) != unicode:
      raise TypeError('doc_root must be a valid string (%s)' % type(doc_root).__name__)
    verify_port(port)
    if php != None:
      verify_ip_port_list(php)
    if self.state == S_INIT:
      if not exists('/conpaas/conf/nginx-web'):
        makedirs('/conpaas/conf/nginx-web')
      self.config_dir = '/conpaas/conf/nginx-web'
      self.config_file = join(self.config_dir, 'nginx.conf')
      self.access_log = join(self.config_dir, 'access.log')
      self.error_log = join(self.config_dir, 'error.log')
      self.pid_file = join(self.config_dir, 'nginx.pid')
      self.user = 'www-data'
    self.doc_root = doc_root
    self.port = port
    self.php = php
    self._write_config()
    self.start_args = [self.cmd, '-c', self.config_file]


class BaseProxy:
  def __init__(self, port=None, backends=None, codeversion=None):
    if port == None: raise TypeError('port is required')
    self.state = S_INIT
    self.configure(port=port, backends=backends, codeversion=codeversion)
    self.start()
  
  def configure(self, port=None, backends=None, codeversion=None): pass
  
  def start(self):
    self.state = S_STARTING
    devnull_fd = open(devnull, 'w')
#    proc = Popen(self.start_args, stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
    proc = Popen(self.start_args, close_fds=True)
    if proc.wait() != 0:
      logger.critical('Failed to start the proxy')
      raise OSError('Failed to start the proxy')
    self.state = S_RUNNING
    logger.info('Proxy started')
  
  def stop(self): pass
  
  def restart(self): pass
  
  def status(self):
    return {'state': self.state, 'port': self.port, 'backends': self.backends}


class NginxProxy(BaseProxy):
  CONF_TEMPLATE = '''
#user ${USER};
worker_processes  1;

error_log  ${ERROR_LOG};
pid        ${PID_FILE};

events {
  worker_connections  1024;
  # multi_accept on;
}

http {
  include       /conpaas/etc/nginx/mime.types;
  include         /conpaas/etc/nginx/fastcgi_params;
  access_log  ${ACCESS_LOG};
  sendfile        on;
  #tcp_nopush     on;
  keepalive_timeout  65;
  tcp_nodelay        on;
  gzip  off;

upstream backend {
${BACKENDS}
}
  
  server {
    listen       ${PORT} default;
    server_name  localhost;
    
    location    / {
      proxy_set_header Conpaasversion '${CODE_VERSION}';
      proxy_set_header Host $$host;
      proxy_set_header X-Real-IP $$remote_addr;
      proxy_pass http://backend;
    }
  }
}
  '''
  CONF_TEMPLATE_NO_VERSION = '''
#user ${USER};
worker_processes  1;

error_log  ${ERROR_LOG};
pid        ${PID_FILE};

events {
  worker_connections  1024;
  # multi_accept on;
}

http {
  include       /conpaas/etc/nginx/mime.types;
  include         /conpaas/etc/nginx/fastcgi_params;
  access_log  ${ACCESS_LOG};
  sendfile        on;
  #tcp_nopush     on;
  keepalive_timeout  65;
  tcp_nodelay        on;
  gzip  off;

upstream backend {
${BACKENDS}
}
  
  server {
    listen       ${PORT} default;
    server_name  localhost;
    
    location    / {
      root /conpaas/html;
      rewrite ^(.*)$$ /default.html break;
    }
  }
}
  '''
  
  cmd = '/conpaas/sbin/nginx'
  
  def __init__(self, port=None, backends=None, codeversion=None):
    BaseProxy.__init__(self, port=port, backends=backends, codeversion=codeversion)
  
  def _current_pid_file(self, increment=0):
    return self.pid_file
  
  def _write_config(self):
    '''Write configuration file.'''
    backends_conf = ''
    if self.backends:
      backends_conf = ''
      for f in self.backends:
        backends_conf += 'server %s:%d;\n' % (f[0], f[1])
    
    conf_fd = open(self.config_file, 'w')
    if self.codeversion != '':
      template = Template(self.CONF_TEMPLATE)
      conf_fd.write(template.substitute(ACCESS_LOG=self.access_log, ERROR_LOG=self.error_log,
                          PID_FILE=self._current_pid_file(),
                          USER=self.user, PORT=self.port, BACKENDS=backends_conf, CODE_VERSION=self.codeversion))
    else:
      template = Template(self.CONF_TEMPLATE_NO_VERSION)
      conf_fd.write(template.substitute(ACCESS_LOG=self.access_log, ERROR_LOG=self.error_log,
                          PID_FILE=self._current_pid_file(),
                          USER=self.user, PORT=self.port, BACKENDS=backends_conf))
    conf_fd.close()
    logger.debug('WebServer configuration written to %s' % (self.config_file))
  
  def configure(self, port=None, backends=None, codeversion=None):
    port = int(port)
    if port == None: raise TypeError('port is required')
    verify_port(port)
    if backends != None:
      verify_ip_port_list(backends)
    if codeversion == None: raise TypeError('codeversion is required')
    if self.state == S_INIT:
      if not exists('/conpaas/conf/nginx-proxy'):
        makedirs('/conpaas/conf/nginx-proxy')
      self.config_dir = '/conpaas/conf/nginx-proxy'
      self.config_file = join(self.config_dir, 'nginx.conf')
      self.access_log = join(self.config_dir, 'access.log')
      self.error_log = join(self.config_dir, 'error.log')
      self.pid_file = join(self.config_dir, 'nginx.pid')
      self.user = 'www-data'
    self.port = port
    self.backends = backends
    self.codeversion = codeversion
    self._write_config()
    self.start_args = [self.cmd, '-c', self.config_file]
  
  def stop(self):
    if self.state == S_RUNNING:
      self.state = S_STOPPING
      if exists(self._current_pid_file()):
        try:
          pid = int(open(self._current_pid_file(), 'r').read().strip())
        except IOError as e:
          logger.exception('Failed to open PID file "%s"' % (self._current_pid_file()))
          raise e
        except (ValueError, TypeError) as e:
          logger.exception('PID in "%s" is invalid' % (self._current_pid_file()))
          raise e
        
        try:
          kill(pid, SIGINT)
          self.state = S_STOPPED
          logger.info('nginx proxy stopped')
        except (IOError, OSError) as e:
          logger.exception('Failed to kill nginx proxy PID=%d' % (pid))
          raise e
      else:
        logger.critical('Could not find PID file %s to kill nginx proxy' % (self._current_pid_file()))
        raise IOError('Could not find PID file %s to kill nginx proxy' % (self._current_pid_file()))
    else:
      logger.warning('Request to kill nginx proxy while it is not running')
  
  def restart(self):
    self._write_config()
    
    try:
      pid = int(open(self._current_pid_file(increment=-1), 'r').read().strip())
    except IOError as e:
      logger.exception('Failed to open PID file "%s"' % (self._current_pid_file(increment=-1)))
      raise e
    except (ValueError, TypeError) as e:
      logger.exception('PID in "%s" is invalid' % (self._current_pid_file(increment=-1)))
      raise e
    
    try:
      kill(pid, SIGHUP)
    except (IOError, OSError):
      logger.exception('Failed to "gracefully" restart nginx proxy PID=%d' % (pid))
      raise e
    else:
      logger.info('WebServer restarted')

  
class PHPProcessManager:
  
  CONF_TEMPLATE = '''[global]
pid = ${PID_FILE}
error_log = ${ERROR_LOG}
;log_level = notice
daemonize = yes
[www]
listen = 0.0.0.0:${PORT}
;listen.allowed_clients = 127.0.0.1
user = ${USER}
group = ${GROUP}
pm = dynamic
pm.max_children = ${MAX_CHILDREN}
pm.start_servers = ${SERVERS_START}
pm.min_spare_servers = ${SERVERS_SPARE_MIN}
pm.max_spare_servers = ${SERVERS_SPARE_MAX}
pm.max_requests = ${MAX_REQUESTS}

;; PHP configuration variables can be passed as follows
; php_admin_value[VAR_NAME] = VALUE
;; eg:
; php_admin_value[upload_max_filesize] = 50M

'''
  cmd = '/conpaas/sbin/php-fpm'
  
  def __init__(self, port=None, scalaris=None, configuration=None):
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
      if not exists('/conpaas/conf/fpm'):
        makedirs('/conpaas/conf/fpm')
      self.config_dir = '/conpaas/conf/fpm'
      self.scalaris_config = join(self.config_dir, 'scalaris.conf')
      self.config_file = join(self.config_dir, 'fpm.conf')
      self.error_log = join(self.config_dir, 'error.log')
      self.pid_file = join(self.config_dir, 'fpm.pid')
      self.user = 'www-data'
      self.group = 'www-data'
      self.max_children = 1
      self.max_requests = 100
      self.servers_start = 1
      self.servers_spare_min = 1
      self.servers_spare_max = 1
      self.scalaris = scalaris
    fd = open(self.config_file, 'w')
    t = Template(self.CONF_TEMPLATE)
    fd.write(t.substitute(PID_FILE=self.pid_file, ERROR_LOG=self.error_log,\
                 PORT=port, USER=self.user, GROUP=self.group,\
                 MAX_CHILDREN=self.max_children, MAX_REQUESTS=self.max_requests,\
                 SERVERS_START=self.servers_start,\
                 SERVERS_SPARE_MIN=self.servers_spare_min,\
                 SERVERS_SPARE_MAX=self.servers_spare_max))
    fd.write('\n\n')
    if configuration:
      for k in configuration:
        fd.write('php_admin_value[%s] = %s\n' % (k, configuration[k]))
    fd.close()
    
    fd = open(self.scalaris_config, 'w')
    fd.write("http://%s:8000/jsonrpc.yaws" % (scalaris))
    fd.close()
    self.port = port
    self.configuration = configuration
  
  def start(self):
    self.state = S_STARTING
    devnull_fd = open(devnull, 'w')
    proc = Popen([self.cmd, '-n', '--fpm-config', self.config_file], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
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

if __name__ == '__main__':
  p = NginxProxy(7777, [['127.0.0.1', 80]], '')
  

"""
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
""" 

import os

from shutil import copyfile, copy

from Cheetah.Template import Template

from conpaas.core.misc import run_cmd

class BaseGanglia(object):
    """Basic Ganglia configuration and startup. Valid for both managers and
    agents. Not to be used directly!"""

    GANGLIA_ETC   = '/etc/ganglia'
    GANGLIA_CONFD = os.path.join(GANGLIA_ETC, 'conf.d')
    GMOND_CONF    = os.path.join(GANGLIA_ETC, 'gmond.conf')
    GANGLIA_MODULES_DIR = '/usr/lib/ganglia/python_modules/'

    def __init__(self):
        """Set basic values"""
        self.cluster_name = 'conpaas'
        self.setuid = 'no'
        self.host_dmax = 300

        # Set by subclasses
        self.manager_ip = None
        self.cps_home = None
    
    def configure(self):
        """Create Ganglia configuration. Gmond is needed by managers and
        agents."""
        os.mkdir(self.GANGLIA_CONFD)
        os.mkdir(self.GANGLIA_MODULES_DIR)

        # Copy modpython.conf
        src = os.path.join(self.cps_home, 'contrib', 'ganglia_modules', 
            'modpython.conf') 
        copy(src, self.GANGLIA_CONFD)

        # Write gmond.conf
        values = {
            'clusterName': self.cluster_name, 'setuid': self.setuid,
            'hostdmax': self.host_dmax, 'managerIp': self.manager_ip
        }
        src = open(os.path.join(self.cps_home, 'config', 'ganglia', 
            'ganglia-gmond.tmpl')).read()
        open(self.GMOND_CONF, 'w').write(str(Template(src, values)))
        
    def add_modules(self, modules):
        """Install additional modules and restart ganglia-monitor"""
        for module in modules:
            # Copy conf files into ganglia conf.d
            filename = os.path.join(self.cps_home, 'contrib', 
                'ganglia_modules', module + '.pyconf') 

            copy(filename, os.path.join(self.GANGLIA_CONFD, module + '.conf'))

            # Copy python modules
            filename = os.path.join(self.cps_home, 'contrib', 
                'ganglia_modules', module + '.py') 
            copy(filename, self.GANGLIA_MODULES_DIR)

        # Restart ganglia-monitor
        run_cmd('/etc/init.d/ganglia-monitor restart')

    def start(self):
        """Services startup"""
        _, err = run_cmd('/etc/init.d/ganglia-monitor start')
        if err:
            return 'Error starting ganglia-monitor: %s' % err

class ManagerGanglia(BaseGanglia):

    GMETAD_CONF = '/etc/ganglia/gmetad.conf'

    def __init__(self, config_parser):
        """Same as for the base case, but with localhost as manager_ip"""
        BaseGanglia.__init__(self)

        self.manager_ip = '127.0.0.1'
        self.cps_home = config_parser.get('manager', 'CONPAAS_HOME')

    def configure(self):
        """Here we also need to configure gmetad and the ganglia frontend"""
        BaseGanglia.configure(self)

        # Write gmetad.conf
        src = open(os.path.join(self.cps_home, 'config', 'ganglia',
            'ganglia-gmetad.tmpl')).read()
        tmpl = Template(src, { 'clusterName': self.cluster_name })
        open(self.GMETAD_CONF, 'w').write(str(tmpl))

        # Frontend configuration
        os.mkdir('/var/www')
        run_cmd('cp -a /root/ConPaaS/contrib/ganglia_frontend/ganglia /var/www')

        copy(os.path.join(self.cps_home, 'contrib', 'ganglia_modules', 
            'nginx-manager.conf'), '/var/cache/cpsagent')

        copy('/etc/nginx/fastcgi_params', '/var/cache/cpsagent/')

        copy(os.path.join(self.cps_home, 'contrib', 'ganglia_modules', 
            'www.conf'), '/etc/php5/fpm/pool.d/')

        copyfile(os.path.join(self.cps_home, 'config', 'ganglia', 
            'ganglia_frontend.tmpl'), '/etc/nginx/nginx.conf')
        
    def start(self):
        """We also need to start gmetad, php5-fpm and nginx"""
        err = BaseGanglia.start(self)
        if err:
            return err

        cmds = ( '/etc/init.d/gmetad start',
                 '/etc/init.d/php5-fpm start',
                 '/usr/sbin/nginx -c /var/cache/cpsagent/nginx-manager.conf' )

        for cmd in cmds:
            _, err = run_cmd(cmd)
            if err:
                return "Error executing '%s': %s" % (cmd, err)

class AgentGanglia(BaseGanglia):

    def __init__(self, config_parser):
        """Same as for the base case, but with proper manager_ip"""
        BaseGanglia.__init__(self)

        self.manager_ip = config_parser.get('agent', 'IP_WHITE_LIST')
        self.cps_home   = config_parser.get('agent', 'CONPAAS_HOME')

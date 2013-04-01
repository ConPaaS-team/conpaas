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
import urlparse

from Cheetah.Template import Template

from conpaas.core.misc import run_cmd
from conpaas.core.log import create_logger

IPOP_CONF_DIR = "/opt/ipop/etc/"

def get_ipop_namespace(config_parser):
    if config_parser.has_section('manager'):
        section = 'manager'
    else:
        section = 'agent'

    app_id = config_parser.get(section, 'APP_ID')
    base_namespace = config_parser.get(section, 'IPOP_BASE_NAMESPACE')

    base_namespace = urlparse.urlparse(base_namespace).netloc
    return "cps-%s-%s" % (base_namespace, app_id)

def configure_ipop(tmpl_dir, namespace, ip_base, netmask, ip_address=None, 
                   udp_port=0):
    """Create or re-write the configuration files required by IPOP.

    By omitting ip_address, the resulting IPOP configuration will be DHCP
    based. By omitting udp_port, a random port will be chosen.
    """
    wanted_params = {
        'bootstrap.config': (),
        'node.config': ( 'udp_port', ),
        'ipop.config': ( 'namespace', ),
        'ipop.vpn.config': ( 'ip_address', 'netmask', 'dhcp', 
                             'static', 'use_ipop_hostname' ),
        'dhcp.config': ( 'ip_base', 'netmask', 'namespace', ),
    }
        
    procedure_args = {
        'tmpl_dir': tmpl_dir,
        'namespace': namespace,
        'ip_base': ip_base,
        'netmask': netmask,
        'ip_address': ip_address,
        'udp_port': udp_port
    }

    if ip_address is None:
        # we use DHCP
        procedure_args['ip_address'] = ''
        procedure_args['dhcp'] = ''
        procedure_args['static'] = ''
        procedure_args['use_ipop_hostname'] = ''
    else:
        # static address
        procedure_args['dhcp'] = 'false'
        procedure_args['static'] = 'true'
        procedure_args['use_ipop_hostname'] = 'true'
        
    for filename in wanted_params.keys():
        # Create config file 'filename' starting from its template and
        # replacing the required values
        template_file = os.path.join(tmpl_dir, filename + '.tmpl')
        values = {}
        for param in wanted_params[filename]:
            values[param] = procedure_args[param]

        template_contents = Template(open(template_file).read(), values)

        dest_file = os.path.join(IPOP_CONF_DIR, filename)
        open(dest_file, 'w').write(str(template_contents))

def restart_ipop():
    """Restart the IPOP service."""
    return run_cmd(cmd='/etc/init.d/groupvpn.sh restart', directory='/')

def get_ip_address():
    """Return the IPv4 address of this IPOP node and its routing prefix in CIDR
    notation. Empty string if it is not set.

    eg: get_ip_address() -> '192.168.12.42/24'
    """
    ip_cmd = "ip -f inet addr show dev tapipop | grep inet | awk '{ print $2 }'"
    return run_cmd(ip_cmd, '/')[0].rstrip('\n')

def configure_conpaas_node(config_parser):
    """IPOP will be configured on this node if IPOP_IP_ADDRESS has been
    specified."""
    logger = create_logger(__name__)

    if config_parser.has_section('manager'):
        section = 'manager'
    else:
        section = 'agent'

    # If IPOP has to be used
    if config_parser.has_option(section, 'IPOP_IP_ADDRESS'):
        ip_address = config_parser.get(section, 'IPOP_IP_ADDRESS')
    else:
        logger.info('Not starting a VPN: IPOP_IP_ADDRESS not found')
        return

    # Stop here if IPOP is not installed
    if not os.path.isdir(IPOP_CONF_DIR):
        logger.error('Not starting a VPN: ipop does not seem to be installed')
        return

    conpaas_home = config_parser.get(section, 'CONPAAS_HOME')

    ipop_tmpl_dir = os.path.join(conpaas_home, 'config', 'ipop')
    
    ipop_namespace = get_ipop_namespace(config_parser)
    ip_base = config_parser.get(section, 'IPOP_BASE_IP')
    netmask = config_parser.get(section, 'IPOP_NETMASK')

    msg = 'Starting IPOP. namespace=%s ip_base=%s netmask=%s ip_address=%s' % (
        ipop_namespace, ip_base, netmask, ip_address)

    logger.info(msg)

    configure_ipop(ipop_tmpl_dir, ipop_namespace, ip_base, netmask, ip_address)
    restart_ipop()

# -*- coding: utf-8 -*-

"""
    conpaas.core.ipop
    =================

    ConPaaS core: VPN support with IPOP.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import os
import urlparse
import hashlib
import string

from Cheetah.Template import Template

from conpaas.core.misc import run_cmd, list_lines
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


def _to_base32(binary, offset, length, pad):
    """
     Based on IPOP/Brunet C# source code ./Brunet/Util/Base32.cs
     @param binary Data to encode as base32
     @param pad if True, add padding characters to make output length a multiple of 8.
     @return the encoded ASCII string
    """
    padding = '='
    enc_length = 8 * (length / 5)
    pad_length = 0
    if length % 5 == 1:
        pad_length = 6
    elif length % 5 == 2:
        pad_length = 4
    elif length % 5 == 3:
        pad_length = 3
    elif length % 5 == 4:
        pad_length = 1
    else:
        pad_length = 0
    
    if pad_length > 0:
        if pad:
            #Add a full block
            enc_length += 8
        else:
            #Just add the chars we need :
            enc_length += (8 - pad_length)
      
    encoded = []
    for _i in range(enc_length):
        encoded.append('')
    #Here are all the full blocks :
    #This is the number of full blocks :
    blocks = length / 5
    for block in range(blocks):
        _encode_block(encoded, 8 * block, binary, offset + 5 * block, 5)
    #Here is one last partial block
    _encode_block(encoded, 8 * blocks, binary, offset + 5 * blocks, length % 5)
    #Add the padding at the end
    if pad:
        for i in range(pad_length):
            encoded[enc_length - i - 1] = padding
    return ''.join(encoded)

def _encode_block(ascii_out, ascii_off, binary, offset, block_length):
    """
     Based on IPOP/Brunet C# source code ./Brunet/Util/Base32.cs
    """
    alphabet = string.ascii_uppercase + string.digits[2:8]
    #The easiest thing is just to do this by hand :
    idx = 0
    if block_length >= 5:
        idx |= binary[offset + 4] & 0x1F
        ascii_out[ascii_off + 7] = alphabet[idx]
        idx = 0
        idx |= (binary[offset + 4] & 0xE0) >> 5
    if block_length >= 4:
        idx |= (binary[offset + 3] & 0x03) << 3
        ascii_out[ascii_off + 6] = alphabet[idx]
        idx = 0
        idx |= (binary[offset + 3] & 0x7C) >> 2
        ascii_out[ascii_off + 5] = alphabet[idx]
        idx = 0
        idx |= (binary[offset + 3] & 0x80) >> 7
    if block_length >= 3:
        idx |= (binary[offset + 2] & 0x0F) << 1
        ascii_out[ascii_off + 4] = alphabet[idx]
        idx = 0
        idx |= (binary[offset + 2] & 0xF0) >> 4
    if block_length >= 2:
        idx |= (binary[offset + 1] & 0x01) << 4
        ascii_out[ascii_off + 3] = alphabet[idx]
        idx = 0
        idx |= (binary[offset + 1] & 0x3E) >> 1
        ascii_out[ascii_off + 2] = alphabet[idx]
        idx = 0
        idx |= (binary[offset + 1] & 0xC0) >> 6
    if block_length >= 1:
        idx |= (binary[offset] & 0x7) << 2
        ascii_out[ascii_off + 1] = alphabet[idx]
        idx = 0
        idx |= binary[offset] >> 3
        ascii_out[ascii_off] = alphabet[idx]

def __get_node_hash(ref_str):
    """
    Return the IPOP internal address in the IPOP format for the given reference string.
    @param ref_str  reference string
    @return: a string representing the internal IPOP address for the given string
    """
    sha = hashlib.sha1()
    sha.update(ref_str)
    digest = sha.digest()
    hash_bytes = [ord(x) for x in digest]
    # set the first bit of the last byte to 0 to set the IPOP/Brunet P2P address class to unicast address AHAddress
    hash_bytes[len(hash_bytes) - 1] &= 0xFE
    return _to_base32(hash_bytes, 0, len(hash_bytes), True)
    
def configure_ipop(tmpl_dir, namespace, ip_base, netmask, ip_address=None, 
                   udp_port=0, bootstrap_nodes=None):
    """Create or re-write the configuration files required by IPOP.

    By omitting ip_address, the resulting IPOP configuration will be DHCP
    based. By omitting udp_port, a random port will be chosen. By omitting
    bootstrap_nodes, the default list of bootstrap nodes will be used.
    """
    wanted_params = {
        'bootstrap.config': ( 'bootstrap_nodes', ),
        'node.config': ( 'udp_port', 'bootstrap_nodes', 'node_address'),
        'ipop.config': ( 'namespace', ),
        'ipop.vpn.config': ( 'ip_address', 'netmask', 'dhcp', 
                             'static', 'use_ipop_hostname' ),
        'dhcp.config': ( 'ip_base', 'netmask', 'namespace', ),
    }
    
    if ip_address is None or namespace == '':
        node_address = ''
    else:
        node_address = __get_node_hash(namespace + ip_address)
    
    procedure_args = {
        'bootstrap_nodes' : bootstrap_nodes,
        'tmpl_dir': tmpl_dir,
        'namespace': namespace,
        'ip_base': ip_base,
        'netmask': netmask,
        'ip_address': ip_address,
        'udp_port': udp_port,
        'node_address': node_address
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

    if config_parser.has_option(section, 'IPOP_BOOTSTRAP_NODES'):
        bootstrap_nodes = list_lines(
            config_parser.get(section, 'IPOP_BOOTSTRAP_NODES'))
    else:
        bootstrap_nodes = None

    msg = 'Starting IPOP. namespace=%s ip_base=%s netmask=%s ip_address=%s' % (
        ipop_namespace, ip_base, netmask, ip_address)

    logger.info(msg)

    configure_ipop(ipop_tmpl_dir, ipop_namespace, ip_base, netmask, ip_address, bootstrap_nodes=bootstrap_nodes)
    restart_ipop()

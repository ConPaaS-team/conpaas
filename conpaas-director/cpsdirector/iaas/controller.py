from threading import Thread, Lock, Event

import os.path
import time
import json, httplib
import socket
import urlparse
import StringIO
from string import Template

import logging
from cpsdirector.common import config_parser, log
from conpaas.core.log import create_logger, init
from conpaas.core.misc import file_get_contents

from cpsdirector.user import _deduct_credit as deduct_credit

from cpsdirector.x509cert import generate_certificate
from cpsdirector.iaas import iaas #from conpaas.core import iaas

from conpaas.core import https
from ConfigParser import ConfigParser
from cpsdirector.common import config_parser as default_config_parser

class Controller(object):

    
    def __init__(self):
        

        https.client.conpaas_init_ssl_ctx('/etc/cpsdirector/certs', 'director') 

        init('/var/log/cpsdirector/debugging.log')
        self._logger = create_logger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self._force_terminate_lock = Lock()

        self._created_nodes = []
        self._partially_created_nodes = []

        self._available_clouds = []
        self._default_cloud = None
        self.role = ""
    
    def _setup(self):

        self._conpaas_user_id = self.config_parser.get('manager', 'USER_ID')
        self._conpaas_app_id = self.config_parser.get('manager', 'APP_ID')
        self._conpaas_name = self.config_parser.get('manager', 'DEPLOYMENT_NAME')

        # TODO (genc): The IPOP part is temporarily commented until we get it working with the new version
        
        # Set the CA URL as IPOP's base namespace
        # self._ipop_base_namespace = self._conpaas_caUrl

        # if config_parser.has_option('manager', 'IPOP_BASE_IP'):
        #     # Application-level network
        #     self._ipop_base_ip = config_parser.get('manager', 'IPOP_BASE_IP')
        # else:
        #     self._ipop_base_ip = None

        # if config_parser.has_option('manager', 'IPOP_NETMASK'):
        #     # Application-level netmask
        #     self._ipop_netmask = config_parser.get('manager', 'IPOP_NETMASK')
        # else:
        #     self._ipop_netmask = None

        # if config_parser.has_option('manager', 'IPOP_BOOTSTRAP_NODES'):
        #     # Application-level network's bootstrap nodes
        #     self._ipop_bootstrap_nodes = config_parser.get('manager', 'IPOP_BOOTSTRAP_NODES')
        # else:
        #     self._ipop_bootstrap_nodes = None

        # if config_parser.has_option('manager', 'IPOP_SUBNET'):
        #     # Only import from netaddr if IPOP has to be started
        #     from netaddr import IPNetwork

        #     # Subnet assigned to this service by the director
        #     self._ipop_subnet = IPNetwork(config_parser.get('manager', 'IPOP_SUBNET'))
        # else:
        #     self._ipop_subnet = None

        self._set_clouds()

    def setup_default(self):
        self.config_parser = default_config_parser
        self._set_clouds()

    def _set_clouds(self):
        if self.config_parser.has_option('iaas', 'DRIVER'):
            self._default_cloud = iaas.get_cloud_instance('iaas', self.config_parser.get('iaas', 'DRIVER').lower(), self.config_parser)
            self._available_clouds.append(self._default_cloud)

        if self.config_parser.has_option('iaas', 'OTHER_CLOUDS'):
            self._logger.debug("attempt iaas.get_clouds()")
            try:
                self._available_clouds.extend(iaas.get_clouds(self.config_parser))
            except Exception as e:
                self._logger.debug("failed iaas.get_clouds()")
                raise e
            self._logger.debug("succeeded iaas.get_clouds()")



    #=========================================================================#
    #               generate_context(self, service_name, replace, cloud)      #
    #=========================================================================#
    def generate_context(self, cloud_name=None, context_replacement={}, startup_script=None, ip_whitelist=None):
        """Generates the contextualization file for the default/given cloud.

            @param cloud (Optional) If specified, the context will be generated
                         for it, otherwise it will be generated for all the
                         available clouds

            @param service_name Used to know which config_files and scripts
                                to select
        """
        # COMMENT (genc): what is ip_whitelist?

        cloud = self.get_cloud_by_name(cloud_name)

        
        contxt = self._generate_context_file(cloud, context_replacement, startup_script)
        cloud.set_context(contxt)

    def generate_config_file(self, cloud_name):
        #TODO (genc) copy the config generation part of the method below here
        pass


    def get_cloud_by_name(self, cloud_name):
        """
            @param cloud_name
            @return The cloud object which name is the same as @param name
        """
        if cloud_name is None or cloud_name == 'default' or cloud_name == 'None':
            cloud_name = 'iaas'

        try:
            return [ cloud for cloud in self._available_clouds 
                if cloud.get_cloud_name() == cloud_name ][0]
        except IndexError:
            raise Exception("Unknown cloud: %s. Available clouds: %s" % (cloud_name, self._available_clouds))

    #=========================================================================#
    #               create_nodes(self, count, contextFile, test_agent)        #
    #=========================================================================#
    def create_nodes(self, nodes_info):
        self._logger.debug('[create_nodes]: %s' % nodes_info)
        ready = []
        poll = []
        iteration = 0
        count=len(nodes_info)
        if count == 0:
            return []
        clouds=list(set([n['cloud'] for n in nodes_info]))
        failed = nodes_info[:]
        while len(ready) < count:
            iteration += 1
            try:
                self._force_terminate_lock.acquire()
                if iteration == 1:
                    request_start = time.time()

                for c in clouds:
                    cloud = self._default_cloud
                    ninfo = failed
                    if c is not None or c!='':
                        cloud = self.get_cloud_by_name(c)
                        ninfo = filter(lambda n: n['cloud']==c, failed)

                    msg = '[create_nodes] iter %d: creating %d nodes on cloud %s' % (iteration, count - len(ready), cloud)
                    self._logger.debug(msg)

                    self._partially_created_nodes = self._create_nodes(ninfo,cloud)
                    self._logger.debug('[create_nodes] _partially_created_nodes: %s' % self._partially_created_nodes)

            except Exception as e:
                self._logger.exception('[create_nodes]: Failed to request new nodes')
                self.delete_nodes(ready)
                self._partially_created_nodes = []
                raise e
            finally:
                self._force_terminate_lock.release()

            poll, failed = self._wait_for_nodes(self._partially_created_nodes)
            ready += poll
            poll = []
            if failed:
                self._logger.debug('[create_nodes]: %d nodes '
                                    'failed to startup properly: %s'
                                    % (len(failed), str(failed)))
                self._partially_created_nodes = []
                self.delete_nodes(failed)

        self._force_terminate_lock.acquire()
        self._created_nodes += ready
        self._partially_created_nodes = []
        self._force_terminate_lock.release()

        return ready

    def _create_nodes(self, nodes_info, cloud):
        if self.role == 'manager':
            role_abbr = 'mgr'
            service_type = ''
            name = "%s-u%s-a%s-r%s" % (self._conpaas_name, self._conpaas_user_id, self._conpaas_app_id, role_abbr)
        else:
            role_abbr = 'agt'
            service_type = self.config_parser.get('manager', 'TYPE')
            name = "%s-u%s-a%s-s%s-t%s-r%s" % (self._conpaas_name, self._conpaas_user_id, self._conpaas_app_id, self._conpaas_service_id, service_type, role_abbr)
        for ni in nodes_info:
            ni['name']=name
        self._logger.debug("[create_nodes]: cloud.new_instances(%s)" % str(nodes_info) )
        return cloud.new_instances(nodes_info)


    # def create_nodes(self, count, cloud_name=None, inst_type=None):
    #     """
    #     Creates the VMs associated with the list of nodes. It also tests
    #     if the agents started correctly.

    #     @param count The number of nodes to be created

    #     @param port The port on which the agent will listen

    #     @param cloud (Optional) If specified, this function will start new
    #                     nodes inside cloud, otherwise it will start new nodes
    #                     inside the default cloud or wherever the controller
    #                     wants (for now only the default cloud is used)

    #     @return A list of nodes of type node.ServiceNode

    #     """
    #     self._logger.debug('[create_nodes]')
    #     ready = []
    #     poll = []
    #     iteration = 0

    #     if count == 0:
    #         return []

    #     cloud = self._default_cloud
    #     if cloud_name is not None:
    #         cloud = self.get_cloud_by_name(cloud_name)

    #     if not deduct_credit(count):
    #         raise Exception('Could not add nodes. Not enough credits.')

    #     while len(ready) < count:
    #         iteration += 1
    #         msg = '[create_nodes] iter %d: creating %d nodes on cloud %s' % (iteration, count - len(ready), cloud.cloud_name)

    #         if inst_type:
    #             msg += ' of type %s' % inst_type

    #         self._logger.debug(msg)

    #         try:
    #             self._force_terminate_lock.acquire()
    #             if iteration == 1:
    #                 request_start = time.time()
                
    #             if self.role == 'manager':
    #                 role_abbr = 'mgr'
    #                 service_type = ''
    #                 name = "%s-u%s-a%s-r%s" % (self._conpaas_name, self._conpaas_user_id, self._conpaas_app_id, role_abbr)
    #             else:
    #                 role_abbr = 'agt'
    #                 service_type = self.config_parser.get('manager', 'TYPE')
    #                 name = "%s-u%s-a%s-s%s-t%s-r%s" % (self._conpaas_name, self._conpaas_user_id, self._conpaas_app_id, self._conpaas_service_id, service_type, role_abbr)

    #             if service_type == 'galera':
    #                 service_type = 'mysql'
                
    #             if (service_type == 'htc'):
    #                 # If HTC is used we need to update here as well (as I see no way to do this elsewhere)
    #                 self.add_context_replacement({
    #                     # 'CLOUD_VMID': cloud.cloud_vmid,
    #                     'CLOUD_NAME': cloud.cloud_name,
    #                     'CLOUD_MACHINE_TYPE': self.config_parser.get(cloud.cloud_name, 'INST_TYPE') ,
    #                     'CLOUD_COST_PER_TIME': self.config_parser.get(cloud.cloud_name, 'COST_PER_TIME'),
    #                     'CLOUD_MAX_VMS_ALL_CLOUDS': self.config_parser.get('iaas', 'MAX_VMS_ALL_CLOUDS'),
    #                     'CLOUD_MAX_VMS': self.config_parser.get(cloud.cloud_name, 'MAX_VMS')
    #                     }, cloud)

    #             # TODO (genc): put this back when figured out what to do with IPOP
    #             if False:
    #             # if self._ipop_base_ip and self._ipop_netmask:
    #                 # If IPOP has to be used we need to update VMs
    #                 # contextualization data for each new instance
    #                 for _ in range(count - len(ready)):
    #                     vpn_ip = self.get_available_ipop_address()
    #                     self.add_context_replacement({ 'IPOP_IP_ADDRESS': vpn_ip }, cloud)
                        
    #                     for newinst in cloud.new_instances(1, name, inst_type):
    #                         # Set VPN IP
    #                         newinst.ip = vpn_ip

    #                         if newinst.private_ip == '':
    #                             # If private_ip is not set yet, use vpn_ip
    #                             newinst.private_ip = vpn_ip

    #                         self._partially_created_nodes.append(newinst)
    #             else:
    #                 self._logger.debug("[create_nodes]: cloud.new_instances(%d, %s, %s)" % ( count - len(ready), name, inst_type ) )
    #                 self._partially_created_nodes = cloud.new_instances(count - len(ready), name, inst_type)

    #             self._logger.debug("[create_nodes]: cloud.new_instances returned %s" %
    #                     self._partially_created_nodes)

    #         except Exception as e:
    #             self._logger.exception('[create_nodes]: Failed to request new nodes')
    #             self.delete_nodes(ready)
    #             self._partially_created_nodes = []
    #             raise e
    #         finally:
    #             self._force_terminate_lock.release()

    #         poll, failed = self._wait_for_nodes(self._partially_created_nodes)
    #         ready += poll

    #         poll = []
    #         if failed:
    #             self._logger.debug('[create_nodes]: %d nodes '
    #                                 'failed to startup properly: %s'
    #                                 % (len(failed), str(failed)))
    #             self._partially_created_nodes = []
    #             self.delete_nodes(failed)
    #     self._force_terminate_lock.acquire()
    #     self._created_nodes += ready
    #     self._partially_created_nodes = []
    #     self._force_terminate_lock.release()

    #     # for i in ready:
    #     #     self._reservation_map[i.id] = timer
    #     return ready

    def _wait_for_nodes(self, nodes, poll_interval=5):
        self._logger.debug('[_wait_for_nodes]: going to start polling for %d nodes' % len(nodes))

        done = []
        poll_cycles = 0

        while len(nodes) > 0:
            poll_cycles += 1

            # Add to 'done' the nodes on which an agent has been started
            # properly.
            done.extend([ node for node in nodes if self._check_node(node) ])

            # Put in 'nodes' only those who have not started yet.
            nodes = [ node for node in nodes if node not in done ]

            if len(nodes) == 0:
                # All the nodes are ready.
                break
            elif poll_cycles * poll_interval > 300:
                # We have waited for more than 5 mins of sleeping + poll time.
                # Let's return whatever we have.
                return (done, nodes)

            self._logger.debug('[_wait_for_nodes]: waiting %d secs for %d nodes' % (poll_interval, len(nodes)))
            time.sleep(poll_interval)

            # Check if some nodes still do not have an IP address.
            no_ip_nodes = [ node for node in nodes if node.ip == '' or node.private_ip == '' ]
            if no_ip_nodes:
                self._logger.debug('[_wait_for_nodes]: refreshing %d nodes' % len(no_ip_nodes))

                for node in no_ip_nodes:
                    refreshed_list = self.list_vms(self.get_cloud_by_name(node.cloud_name))

                    for refreshed_node in refreshed_list:
                        if refreshed_node.id == node.id:
                            node.ip = refreshed_node.ip
                            node.private_ip = refreshed_node.private_ip

        self._logger.debug('[_wait_for_nodes]: All nodes are ready %s'% str(done))
        return (done, [])

    def _check_node(self, node):
        """Return True if the given node has properly started an agent on the
        given port"""
        if node.ip == '' or node.private_ip == '':
            self._logger.debug('[_check_node]: node.ip = %s, node.private_ip = %s: return False' % (node.ip, node.private_ip))
            return False

        try:
            self._logger.debug('[_check_node]: test_agent(%s)' % (node.ip))

            self.check_process(node.ip)
            self._logger.debug('[_check_node]: node = %s' % node.__repr__())
            return True
        except socket.error, err:
            self._logger.debug('[_check_node]: %s' % err)

        return False

    #=========================================================================#
    #                    list_vms(self, cloud=None)                           #
    #=========================================================================#
    def list_vms(self, cloud=None):
        """Returns an array with the VMs running at the given/default(s) cloud.

            @param cloud (Optional) If specified, this method will return the
                         VMs already running at the given cloud
        """
        if cloud is None:
            cloud = self._default_cloud

        return cloud.list_vms()

    #=========================================================================#
    #                    delete_nodes(self, nodes)                            #
    #=========================================================================#
    def delete_nodes(self, nodes):
        """Kills the VMs associated with the list of nodes.

            @param nodes The list of nodes to be removed;
                            - a node must be of type ServiceNode
                              or a class that extends ServiceNode
        """
        for node in nodes:
            cloud = self.get_cloud_by_name(node.cloud_name)
            self._logger.debug('[delete_nodes]: killing ' + str(node.vmid))
            try:
            # node may not be in map if it failed to start
                # if node.id in self._reservation_map:
                #     timer = self._reservation_map.pop(node.id)
                #     if timer.remove_node(node.id) < 1:
                #         timer.stop()
                cloud.kill_instance(node)
            except:
                self._logger.exception('[delete_nodes]: Failed to kill node %s', node.vmid)

    def create_volume(self, size, name, vm_id, cloud=None):
        """Create a new volume with the given name and size (in MBs)."""
        cloud = self.get_cloud_by_name(cloud)

        if cloud.connected is False:
            cloud._connect()

        self._logger.debug("create_volume(cloud=%s, size=%s, name='%s')" % (cloud.cloud_name, size, name))

        return cloud.create_volume(size, name, vm_id)


    def attach_volume(self, vm_id, volume_id, device, cloud=None):
        cloud = self.get_cloud_by_name(cloud)
        if cloud.connected is False:
            cloud._connect()
       
        class volume:
            id = volume_id

        class node:
            id = vm_id

        self._logger.debug("attach_volume(node=%s, volume=%s, device=%s, cloud=%s)" % (node.id, volume.id, device, cloud))
        return cloud.attach_volume(node, volume, device)

    def detach_volume(self, volume_id, cloud=None):
        cloud = self.get_cloud_by_name(cloud)
        if cloud.connected is False:
            cloud._connect()
        class volume:
            id = volume_id
        self._logger.debug("detach_volume(volume=%s)" % volume.id)
        return cloud.detach_volume(volume)

    def destroy_volume(self, volume_id, cloud=None):
        cloud = self.get_cloud_by_name(cloud)
        if cloud.connected is False:
            cloud._connect()
        class volume:
            id = volume_id
        self._logger.debug("destroy_volume(volume=%s)" % volume.id)
        return cloud.driver.destroy_volume(volume)    


    def _create_manager_config(self, user_id, app_id, vpn=None):
        """Add manager configuration"""
        config_string = StringIO.StringIO()
        config_parser.write(config_string)
        config_string.seek(0)
        new_config_parser = ConfigParser()
        new_config_parser.readfp(config_string)

        if not new_config_parser.has_section("manager"):
            new_config_parser.add_section("manager")

        if new_config_parser.has_option('conpaas', 'DEPLOYMENT_NAME'):
            conpaas_deployment_name = new_config_parser.get('conpaas', 'DEPLOYMENT_NAME')
        else:
            conpaas_deployment_name = 'conpaas'

        new_config_parser.set("manager", "DEPLOYMENT_NAME", conpaas_deployment_name)
        new_config_parser.set("manager", "USER_ID", user_id)
        new_config_parser.set("manager", "APP_ID", app_id)

        # if vpn:
        #     config_parser.set("manager", "IPOP_SUBNET", vpn)

        return new_config_parser

    def _get_certificate(self, role, email, cn, org):
        user_id = self.config_parser.get("manager", "USER_ID")
        app_id = self.config_parser.get("manager", "APP_ID")
        cert_dir = self.config_parser.get('conpaas', 'CERT_DIR')
        return generate_certificate(cert_dir, user_id, app_id, role, email, cn, org)

    # the following two methods are the application manager client
    def _check(self, response):
        code, body = response
        if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
        data = json.loads(body)
        if data['error']: raise Exception(data['error']) 
        else : return data['result']

    def check_process(self, host):
        method = 'check_process'
        return self._check(https.client.jsonrpc_get(host, self.port, '/', method))

class AgentController(Controller):
    def __init__(self, user_id, app_id, service_id, service_type, manager_ip):
        Controller.__init__(self)
        self.config_parser = self._create_agent_config(str(user_id), str(app_id), service_id, service_type, manager_ip)
        self._conpaas_service_id = self.config_parser.get('manager', 'SERVICE_ID')
        self._conpaas_service_type = self.config_parser.get('manager', 'TYPE')
        self._setup()

        self.role = "agent"
        self.port = 5555

    def _create_agent_config(self, user_id, app_id, service_id, service_type, manager_ip, vpn=None):
        config_parser = self._create_manager_config(str(user_id), str(app_id))
        config_parser.set('manager', 'SERVICE_ID', service_id)
        config_parser.set('manager', 'TYPE', service_type)
        config_parser.set('manager', 'MANAGER_IP', manager_ip)
        return config_parser

    def _generate_context_file(self, cloud, context_replacement={}, startup_script=None):
        '''
        the context file runs the scripts necessary on each node created
        it's installing all the necessary dependencies for the service
        on the cloud you are installing

        '''

        cloud_type = cloud.get_cloud_type()
        # conpaas_home = self.config_parser.get('manager', 'CONPAAS_HOME')
        conpaas_home = self.config_parser.get('conpaas', 'CONF_DIR')
        
        cloud_scripts_dir = conpaas_home + '/scripts/cloud'
        agent_cfg_dir = conpaas_home + '/config/agent'
        agent_scripts_dir = conpaas_home + '/scripts/agent'

        # COMMENT (genc): the following line is temporarily commented, should be uncommented when we know how to reactivate ipop
        # bootstrap = self.config_parser.get('manager', 'BOOTSTRAP')
        # bootstrap = 'lesh'
        director = self.config_parser.get('director', 'DIRECTOR_URL')
        manager_ip = self.config_parser.get('manager', 'MANAGER_IP')


        # Get contextualization script for the corresponding cloud
        cloud_script_file = open(cloud_scripts_dir + '/' + cloud_type, 'r')
        cloud_script = cloud_script_file.read()

        # Get agent setup file
        agent_setup_file = open(agent_scripts_dir + '/agent-setup', 'r')
        
        agent_setup = Template(agent_setup_file.read()).safe_substitute(DIRECTOR=director)

        # Get agent config file - add to the default one the one specific
        # to the service if it exists
        default_agent_cfg_file = open(agent_cfg_dir + '/default-agent.cfg')
        agent_cfg = Template(default_agent_cfg_file.read()).safe_substitute(
            AGENT_TYPE=self._conpaas_service_type,
            MANAGER_IP=manager_ip,
            CONPAAS_USER_ID=self._conpaas_user_id,
            CONPAAS_SERVICE_ID=self._conpaas_service_id,
            CONPAAS_APP_ID=self._conpaas_app_id,
            CLOUD_TYPE=cloud_type,
            # IPOP_BASE_NAMESPACE=self._ipop_base_namespace
            )

        # Add IPOP_BASE_IP, IPOP_NETMASK and IPOP_IP_ADDRESS if necessary
        # if self._ipop_base_ip and self._ipop_netmask:
        #     agent_cfg += '\nIPOP_BASE_IP = %s' % self._ipop_base_ip
        #     agent_cfg += '\nIPOP_NETMASK = %s' % self._ipop_netmask
        #     agent_cfg += '\nIPOP_IP_ADDRESS = $IPOP_IP_ADDRESS'
        #     if self._ipop_bootstrap_nodes is not None:
        #         agent_cfg += '\nIPOP_BOOTSTRAP_NODES = %s' % self._ipop_bootstrap_nodes

        if os.path.isfile(agent_cfg_dir + '/' + self._conpaas_service_type + '-agent.cfg'):
            agent_cfg_file = open(agent_cfg_dir +'/' + self._conpaas_service_type + '-agent.cfg')
            # agent_cfg += '\n' + Template(agent_cfg_file.read()).safe_substitute(CLOUD_TYPE=cloud_type,)
            agent_cfg += '\n' + Template(agent_cfg_file.read()).safe_substitute(context_replacement)

        # Get agent start file - if none for this service, use the default one
        if os.path.isfile(agent_scripts_dir +'/' + self._conpaas_service_type + '-agent-start'):
            agent_start_file = open(agent_scripts_dir +'/' + self._conpaas_service_type + '-agent-start')
            agent_start = Template(agent_start_file.read()).safe_substitute(context_replacement)
        else:
            agent_start_file = open(agent_scripts_dir + '/default-agent-start')
            agent_start = agent_start_file.read()

        # Get key and a certificate from CA
        # agent_certs = self._get_certificate()
        agent_certs = self._get_certificate(role="agent",
                                            email="info@conpaas.eu",
                                            cn="ConPaaS",
                                            org="Contrail")

        # Concatenate the files
        context_file = (cloud_script + '\n\n'
                        + 'cat <<EOF > /tmp/cert.pem\n'
                        + agent_certs['cert'] + '\n' + 'EOF\n\n'
                        + 'cat <<EOF > /tmp/key.pem\n'
                        + agent_certs['key'] + '\n' + 'EOF\n\n'
                        + 'cat <<EOF > /tmp/ca_cert.pem\n'
                        + agent_certs['ca_cert'] + '\n' + 'EOF\n\n'
                        + agent_setup + '\n\n'
                        + 'cat <<EOF > $ROOT_DIR/config.cfg\n'
                        + agent_cfg + '\n' + 'EOF\n\n')

        # COMMENT (genc): the following code copies the start script from the menager to agents
        # i don't know if this can be possible at this point since we are at the director and agent
        # startup scritps are at the manager
        
        # # Get user-provided startup script's absolute path
        # basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        # startup_script = os.path.join(basedir, 'startup.sh')

        # # Append user-provided startup script (if any)
        # if os.path.isfile(startup_script):
        #     context_file += open(startup_script).read() + '\n'
        if startup_script:
            context_file += startup_script + '\n'

        # Finally, the agent startup script
        context_file += agent_start + '\n'

        return context_file


class ManagerController(Controller):

    def __init__(self, user_id, app_id, vpn):
        Controller.__init__(self)
        self.config_parser = self._create_manager_config(str(user_id), str(app_id), vpn)
        self._setup()
        self.role = "manager"
        self.port = 443

    def generate_config_file(self):
        tmpl_values = {}
        # cloud_name = cloud.get_cloud_name()
        conpaas_home = self.config_parser.get('conpaas', 'CONF_DIR')
        mngr_cfg_dir = os.path.join(conpaas_home, 'config', 'manager')
        
        if self.config_parser.has_option('conpaas', 'DEPLOYMENT_NAME'):
            conpaas_deployment_name = self.config_parser.get('conpaas', 'DEPLOYMENT_NAME')
        else:
            conpaas_deployment_name = 'conpaas'        

        cloud_sections = ['iaas']
        if self.config_parser.has_option('iaas', 'OTHER_CLOUDS'):
            cloud_sections.extend(
                [cld_name for cld_name
                 in self.config_parser.get('iaas', 'OTHER_CLOUDS').split(',')
                 if self.config_parser.has_section(cld_name)])

        
        def _extract_cloud_cfg(section_name):
            tmpl_values['cloud_cfg'] += "["+section_name+"]\n"
            for key, value in self.config_parser.items(section_name):
                tmpl_values['cloud_cfg'] += key.upper() + " = " + value + "\n"

        tmpl_values['cloud_cfg'] = ''
        for section_name in cloud_sections:
            _extract_cloud_cfg(section_name)

        # Get manager config file
        # mngr_cfg = file_get_contents(os.path.join(mngr_cfg_dir, 'default-manager.cfg')) 
        # TODO (genc): Don't forget about having two default manager files (delete one when done)
        mngr_cfg = file_get_contents(os.path.join(mngr_cfg_dir, 'default-manager-new.cfg')) 
       
        # Modify manager config file setting the required variables
        mngr_cfg = mngr_cfg.replace('%CONPAAS_DEPLOYMENT_NAME%', conpaas_deployment_name)
        
        # for option_name in 'SERVICE_ID', 'USER_ID', 'APP_ID':
        for option_name in 'USER_ID', 'APP_ID':
            mngr_cfg = mngr_cfg.replace('%CONPAAS_' + option_name + '%', self.config_parser.get("manager", option_name))


        # COMMENT (genc): this part is commented because it is being used only by htc, not useful for the moment 

        # mngr_cfg = mngr_cfg.replace('%CLOUD_NAME%', cloud_name);
        
        # # OpenNebula, EC2. etc
        # mngr_cfg = mngr_cfg.replace('%CLOUD_TYPE%', self.config_parser.get(cloud_name, 'DRIVER'))  

        # if self.config_parser.has_option(cloud_name, 'INST_TYPE'):
        #     mngr_cfg = mngr_cfg.replace('%CLOUD_MACHINE_TYPE%', self.config_parser.get(cloud_name, 'INST_TYPE'))

        # if self.config_parser.has_option(cloud_name, 'COST_PER_TIME'):
        #     mngr_cfg = mngr_cfg.replace('%CLOUD_COST_PER_TIME%', self.config_parser.get(cloud_name, 'COST_PER_TIME'))

        # if self.config_parser.has_option(cloud_name, 'MAX_VMS'):
        #     mngr_cfg = mngr_cfg.replace('%CLOUD_MAX_VMS%', self.config_parser.get(cloud_name, 'MAX_VMS'))

        # if self.config_parser.has_option('iaas', 'MAX_VMS_ALL_CLOUDS'):
        #     mngr_cfg = mngr_cfg.replace('%CLOUD_MAX_VMS_ALL_CLOUDS%', self.config_parser.get('iaas', 'MAX_VMS_ALL_CLOUDS'))
        # # mngr_cfg = mngr_cfg.replace('%CLOUD_COST_PER_TIME%', cloud_cost_per_time);

       

        # COMMENT (genc): the IPOP part is commented  until we have a working IPOP

        # # Check if we want to use IPOP. If so, add IPOP directives to manager
        # # config file
        # if self.config_parser.has_option('manager', 'IPOP_SUBNET'):
        #     ipop_subnet = self.config_parser.get('manager', 'IPOP_SUBNET')
        #     mngr_cfg += '\nIPOP_SUBNET = %s' % ipop_subnet

        #     ipop_network = IPNetwork(ipop_subnet).iter_hosts()

        #     # Skip the first IP address. IPOP uses it for internal purposes
        #     ipop_network.next()

        #     mngr_cfg += '\nIPOP_IP_ADDRESS = %s' % ipop_network.next()
        #     mngr_cfg += '\nIPOP_BASE_IP = %s' % self.config_parser.get('conpaas', 'VPN_BASE_NETWORK')
        #     mngr_cfg += '\nIPOP_NETMASK = %s' % self.config_parser.get('conpaas', 'VPN_NETMASK')

        #     if self.config_parser.has_option('conpaas', 'VPN_BOOTSTRAP_NODES'):
        #         mngr_cfg += '\nIPOP_BOOTSTRAP_NODES = %s' % self.config_parser.get('conpaas', 'VPN_BOOTSTRAP_NODES')

        tmpl_values['mngr_cfg'] = mngr_cfg
        return """
%(cloud_cfg)s
%(mngr_cfg)s
""" % tmpl_values

    def _generate_context_file(self, cloud, context_replacement={}, startup_script=None):
        """Override default _get_context_file. Here we generate the context
        file for managers rather than for agents."""

        cloud_type = cloud.get_cloud_type()
        conpaas_home = self.config_parser.get('conpaas', 'CONF_DIR')
        cloud_scripts_dir = os.path.join(conpaas_home, 'scripts', 'cloud')
        mngr_scripts_dir = os.path.join(conpaas_home, 'scripts', 'manager')

        director = self.config_parser.get('director', 'DIRECTOR_URL')

        # Values to be passed to the context file template
        tmpl_values = {}

        # Get contextualization script for the cloud
        try:
            tmpl_values['cloud_script'] = file_get_contents(os.path.join(cloud_scripts_dir, cloud_type))
        except IOError:
            tmpl_values['cloud_script'] = ''

        # Get manager setup file
        mngr_setup = file_get_contents(os.path.join(mngr_scripts_dir, 'manager-setup'))
        mngr_setup = mngr_setup.replace('%DIRECTOR_URL%',director)

        tmpl_values['mngr_setup'] = mngr_setup

        tmpl_values['config'] = self.generate_config_file() 
        # self.config
        
        # Add default manager startup script
        tmpl_values['mngr_start_script'] = file_get_contents(os.path.join(mngr_scripts_dir, 'default-manager-start'))
        tmpl_values['mngr_vars_script'] = file_get_contents(os.path.join(mngr_scripts_dir, 'default-manager-vars'))

        # Get key and a certificate from CA
        mngr_certs = self._get_certificate(role="manager",
                                            email="info@conpaas.eu",
                                            cn="ConPaaS",
                                            org="Contrail")

        tmpl_values['mngr_certs_cert'] = mngr_certs['cert']
        tmpl_values['mngr_certs_key'] = mngr_certs['key']
        tmpl_values['mngr_certs_ca_cert'] = mngr_certs['ca_cert']

        # Concatenate the files
        return """%(cloud_script)s

cat <<EOF > /tmp/cert.pem
%(mngr_certs_cert)s
EOF

cat <<EOF > /tmp/key.pem
%(mngr_certs_key)s
EOF

cat <<EOF > /tmp/ca_cert.pem
%(mngr_certs_ca_cert)s
EOF

%(mngr_setup)s

cat <<EOF > $ROOT_DIR/config.cfg
%(config)s
EOF


%(mngr_start_script)s

%(mngr_vars_script)s

""" % tmpl_values

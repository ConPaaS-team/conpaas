# -*- coding: utf-8 -*-

"""
    conpaas.core.controller
    =======================

    ConPaaS core: start/stop/list nodes.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread, Lock, Event

import os.path
import time
import json
import socket
import urlparse
from string import Template

from conpaas.core.log import create_logger
from conpaas.core import iaas
from conpaas.core import https

class Controller(object):
    """Implementation of the clouds controller. This class implements functions
       to easily work with the available cloud objects.

       So far, it provides the following functionalities/abstractions:
         - crediting system (also terminate service when user out of credits)
         - adding nodes (VMs)
         - removing nodes (VMs)
    """

    def __init__(self, config_parser, **kwargs):
        # Params for director callback
        self.__conpaas_creditUrl = config_parser.get('manager',
                                                'CREDIT_URL')
        self.__conpaas_terminateUrl = config_parser.get('manager',
                                                   'TERMINATE_URL')
        self.__conpaas_service_id = config_parser.get('manager',
                                                 'SERVICE_ID')
        self.__conpaas_user_id = config_parser.get('manager',
                                              'USER_ID')
        self.__conpaas_app_id = config_parser.get('manager',
                                              'APP_ID')
        self.__conpaas_caUrl = config_parser.get('manager',
                                            'CA_URL')

        # Set the CA URL as IPOP's base namespace
        self.__ipop_base_namespace = self.__conpaas_caUrl

        if config_parser.has_option('manager', 'IPOP_BASE_IP'):
            # Application-level network
            self.__ipop_base_ip = config_parser.get('manager', 'IPOP_BASE_IP')
        else:
            self.__ipop_base_ip = None

        if config_parser.has_option('manager', 'IPOP_NETMASK'):
            # Application-level netmask
            self.__ipop_netmask = config_parser.get('manager', 'IPOP_NETMASK')
        else:
            self.__ipop_netmask = None

        if config_parser.has_option('manager', 'IPOP_BOOTSTRAP_NODES'):
            # Application-level network's bootstrap nodes
            self.__ipop_bootstrap_nodes = config_parser.get('manager', 'IPOP_BOOTSTRAP_NODES')
        else:
            self.__ipop_bootstrap_nodes = None

        if config_parser.has_option('manager', 'IPOP_SUBNET'):
            # Only import from netaddr if IPOP has to be started
            from netaddr import IPNetwork

            # Subnet assigned to this service by the director
            self.__ipop_subnet = IPNetwork(
                config_parser.get('manager', 'IPOP_SUBNET'))
        else:
            self.__ipop_subnet = None

        # For crediting system
        self.__reservation_logger = create_logger('ReservationTimer')
        self.__reservation_map = {'manager': ReservationTimer(['manager'],
                                  55 * 60,  # 55mins
                                  self.__deduct_and_check_credit,
                                  self.__reservation_logger)}
        self.__reservation_map['manager'].start()
        self.__force_terminate_lock = Lock()

        self.config_parser = config_parser
        self.__created_nodes = []
        self.__partially_created_nodes = []
        self.__logger = create_logger(__name__)

        self.__available_clouds = []
        self.__default_cloud = None
        if config_parser.has_option('iaas', 'DRIVER'):
            self.__default_cloud = iaas.get_cloud_instance(
                'iaas',
                config_parser.get('iaas', 'DRIVER').lower(),
                config_parser)
            self.__available_clouds.append(self.__default_cloud)

        if config_parser.has_option('iaas', 'OTHER_CLOUDS'):
            self.__available_clouds.extend(iaas.get_clouds(config_parser))

        # Setting VM role
        self.role = 'agent'

    def get_available_ipop_address(self):
        """Return an unassigned IP address in this manager's VPN subnet"""
        # Network iterator
        network = self.__ipop_subnet.iter_hosts()
        
        # Currently running hosts
        running_hosts = [ str(node.ip) 
            for node in self.__created_nodes + self.__partially_created_nodes ] 

        self.__logger.debug("get_available_ipop_address: running nodes: %s" 
            % running_hosts)

        # The first address is used by IPOP internally
        network.next()
        # The second one is taken by manager 
        network.next()

        for host in network:
            host = str(host)

            if host not in running_hosts:
                self.__logger.debug("get_available_ipop_address: returning %s" 
                    % host)
                return host

    #=========================================================================#
    #               create_nodes(self, count, contextFile, test_agent)        #
    #=========================================================================#
    def create_nodes(self, count, test_agent, port, cloud=None, inst_type=None):
        """
        Creates the VMs associated with the list of nodes. It also tests
        if the agents started correctly.

        @param count The number of nodes to be created

        @param test_agent A callback function to test if the agent
                        started correctly in the newly created VM

        @param port The port on which the agent will listen

        @param cloud (Optional) If specified, this function will start new
                        nodes inside cloud, otherwise it will start new nodes
                        inside the default cloud or wherever the controller
                        wants (for now only the default cloud is used)

        @return A list of nodes of type node.ServiceNode

        """
        ready = []
        poll = []
        iteration = 0

        if cloud is None:
            cloud = self.__default_cloud

        if not self.deduct_credit(count):
            raise Exception('Could not add nodes. Not enough credits.')

        while len(ready) < count:
            iteration += 1
            msg = '[create_nodes] iter %d: creating %d nodes on cloud %s' % (
                iteration, count - len(ready), cloud.cloud_name)

            if inst_type:
                msg += ' of type %s' % inst_type

            self.__logger.debug(msg)

            try:
                self.__force_terminate_lock.acquire()
                if iteration == 1:
                    request_start = time.time()

                service_type = self.config_parser.get('manager', 'TYPE')

                # eg: conpaas-agent-php-u34-s316
                name = "conpaas-%s-%s-u%s-s%s" % (self.role, service_type,
                       self.__conpaas_user_id, self.__conpaas_service_id)

                if self.__ipop_base_ip and self.__ipop_netmask:
                    # If IPOP has to be used we need to update VMs
                    # contextualization data for each new instance
                    for _ in range(count - len(ready)):
                        vpn_ip = self.get_available_ipop_address()
                        self.add_context_replacement({ 'IPOP_IP_ADDRESS': vpn_ip }, cloud)
                        
                        for newinst in cloud.new_instances(1, name, inst_type):
                            # Set VPN IP
                            newinst.ip = vpn_ip

                            if newinst.private_ip == '':
                                # If private_ip is not set yet, use vpn_ip
                                newinst.private_ip = vpn_ip

                            self.__partially_created_nodes.append(newinst)

                        self.__logger.debug("cloud.new_instances: %s" % poll)
                else:
                    self.__partially_created_nodes = cloud.new_instances(
                        count - len(ready), name, inst_type)

            except Exception as e:
                self.__logger.exception(
                    '[_create_nodes]: Failed to request new nodes')
                self.delete_nodes(ready)
                self.__partially_created_nodes = []
                raise e
            finally:
                self.__force_terminate_lock.release()

            poll, failed = self.__wait_for_nodes(
                self.__partially_created_nodes, test_agent, port)
            ready += poll

            poll = []
            if failed:
                self.__logger.debug('[_create_nodes]: %d nodes '
                                    'failed to startup properly: %s'
                                    % (len(failed), str(failed)))
                self.__partially_created_nodes = []
                self.delete_nodes(failed)
        self.__force_terminate_lock.acquire()
        self.__created_nodes += ready
        self.__partially_created_nodes = []
        self.__force_terminate_lock.release()

        # start reservation timer with slack of 3 mins + time already wasted
        # this should be enough time to terminate instances before
        # hitting the following hour
        timer = ReservationTimer([i.id for i in ready],
                                 (55 * 60) - (time.time() - request_start),
                                 self.__deduct_and_check_credit,
                                 self.__reservation_logger)
        timer.start()
        # set mappings
        for i in ready:
            self.__reservation_map[i.id] = timer
        return ready

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
            self.__logger.debug('[delete_nodes]: killing ' + str(node.id))
            try:
            # node may not be in map if it failed to start
                if node.id in self.__reservation_map:
                    timer = self.__reservation_map.pop(node.id)
                    if timer.remove_node(node.id) < 1:
                        timer.stop()
                cloud.kill_instance(node)
            except:
                self.__logger.exception('[delete_nodes]: '
                                        'Failed to kill node %s', node.id)

    #=========================================================================#
    #                    list_vms(self, cloud=None)                           #
    #=========================================================================#
    def list_vms(self, cloud=None):
        """Returns an array with the VMs running at the given/default(s) cloud.

            @param cloud (Optional) If specified, this method will return the
                         VMs already running at the given cloud
        """
        if cloud is None:
            cloud = self.__default_cloud

        return cloud.list_vms()

    #=========================================================================#
    #               generate_context(self, service_name, replace, cloud)      #
    #=========================================================================#
    def generate_context(self, service_name,
                         cloud=None, ip_whitelist=None):
        """Generates the contextualization file for the default/given cloud.

            @param cloud (Optional) If specified, the context will be generated
                         for it, otherwise it will be generated for all the
                         available clouds

            @param service_name Used to know which config_files and scripts
                                to select
        """
        def __set_cloud_ctx(cloud):
            contxt = self._get_context_file(service_name,
                                            cloud.get_cloud_type())
            cloud.set_context(contxt)

        if cloud is None:
            for cloud in self.__available_clouds:
                __set_cloud_ctx(cloud)
        else:
            __set_cloud_ctx(cloud)


    def add_context_replacement(self, replace={}, cloud=None, strict=False):
        """Add a variable replacement to the variable replacements to apply to
           the context template for the default/given cloud.

            @param replace A dictionary that specifies which words shoud be
                           replaced with what. For example:
                           replace = dict(name='A', age='57')
                           context1 =  '$name , $age'
                           => new_context1 = 'A , 57'
                           context2 ='${name}na, ${age}'
                           => new_context2 = 'Ana, 57'

            @param cloud (Optional) If specified, the context will be generated
                         for it, otherwise it will be generated for the default
                         cloud
            
            @param strict  If true, then setting a replacement for an already
                           replaced variable will raise an exception.

        """
        if cloud is None:
            cloud = self.__default_cloud

        cloud.add_context_replacement(replace, strict)


    #=========================================================================#
    #               get_clouds(self)                                          #
    #=========================================================================#
    def get_clouds(self):
        """
            @return The list of cloud objects

        """
        return self.__available_clouds

    #=========================================================================#
    #               get_cloud_by_name(self)                                   #
    #=========================================================================#
    def get_cloud_by_name(self, cloud_name):
        """
            @param cloud_name

            @return The cloud object which name is the same as @param name

        """
        try:
            return [ cloud for cloud in self.__available_clouds 
                if cloud.get_cloud_name() == cloud_name ][0]
        except IndexError:
            raise Exception("Unknown cloud: %s. Available clouds: %s" % (
                cloud_name, self.__available_clouds))

    #=========================================================================#
    #               config_cloud(self, cloud, config_params)                  #
    #=========================================================================#
    def config_cloud(self, cloud, config_params):
        """Configures some parameters in the given cloud

            @param cloud The cloud to be configured

            @param config_params A dictionary containing the configuration
                                 parameters (are specific to the cloud)
        """
        cloud.config(config_params)

    #=========================================================================#
    #               config_clouds(self, config_params)                        #
    #=========================================================================#
    def config_clouds(self, config_params):
        """Same as config_cloud but for all available clouds

            @param config_params A dictionary containing the configuration
                                 parameters (are specific to the cloud)
        """
        for cloud in self.__available_clouds:
            cloud.config(config_params)

    def __check_node(self, node, test_agent, port):
        """Return True if the given node has properly started an agent on the
        given port"""
        if node.ip == '' or node.private_ip == '':
            return False

        try:
            self.__logger.debug('[__check_node]: test_agent(%s, %s)' % (
                node.ip, port))

            test_agent(node.ip, port)
            return True
        except socket.error, err:
            self.__logger.debug('[__check_node]: %s' % err)

        return False

    def __wait_for_nodes(self, nodes, test_agent, port, poll_interval=10):
        self.__logger.debug('[__wait_for_nodes]: going to start polling')

        done = []
        poll_cycles = 0

        while len(nodes) > 0:
            poll_cycles += 1

            # Add to 'done' the nodes on which an agent has been started
            # properly.
            done.extend([ node for node in nodes 
                if self.__check_node(node, test_agent, port) ])

            # Put in 'nodes' only those who have not started yet.
            nodes = [ node for node in nodes if node not in done ]

            if len(nodes) == 0:
                # All the nodes are ready.
                break
            elif poll_cycles * poll_interval > 300:
                # We have waited for more than 5 mins of sleeping + poll time.
                # Let's return whatever we have.
                return (done, nodes)

            self.__logger.debug('[__wait_for_nodes]: waiting %d secs for %d nodes'
                                % (poll_interval, len(nodes)))
            time.sleep(poll_interval)

            # Check if some nodes still do not have an IP address.
            no_ip_nodes = [ node for node in nodes
                           if node.ip == '' or node.private_ip == '' ]
            if no_ip_nodes:
                self.__logger.debug('[__wait_for_nodes]: refreshing %d nodes'
                                    % len(no_ip_nodes))

                for node in no_ip_nodes:
                    refreshed_list = self.list_vms(
                        self.get_cloud_by_name(node.cloud_name))

                    for refreshed_node in refreshed_list:
                        if refreshed_node.id == node.id:
                            node.ip = refreshed_node.ip
                            node.private_ip = refreshed_node.private_ip

        self.__logger.debug('[__wait_for_nodes]: All nodes are ready %s'
                            % str(done))
        return (done, [])

    def create_volume(self, size, name, cloud=None):
        """Create a new volume with the given name and size (in MBs)."""
        if cloud is None:
            cloud = self.__default_cloud

        if cloud.connected is False:
            cloud._connect()

        self.__logger.debug("create_volume(cloud=%s, size=%s, name='%s')" % 
                (cloud.cloud_name, size, name))

        return cloud.driver.create_volume(size=size, name=name)

    def attach_volume(self, node, volume, device, cloud=None):
        if cloud is None:
            cloud = self.__default_cloud

        self.__logger.debug("attach_volume(node=%s, volume=%s, device=%s)" % 
                (node, volume, device))
        return cloud.driver.attach_volume(node, volume, device)

    def detach_volume(self, volume, cloud=None):
        if cloud is None:
            cloud = self.__default_cloud

        self.__logger.debug("detach_volume(volume=%s)" % volume)
        return cloud.driver.detach_volume(volume)

    def destroy_volume(self, volume, cloud=None):
        if cloud is None:
            cloud = self.__default_cloud

        self.__logger.debug("destroy_volume(volume=%s)" % volume)
        return cloud.driver.destroy_volume(volume)

    def _get_context_file(self, service_name, cloud_type):
        '''
        the context file runs the scripts necessary on each node created
        it's installing all the necessary dependencies for the service
        on the cloud you are installing

        '''
        conpaas_home = self.config_parser.get('manager', 'CONPAAS_HOME')
        cloud_scripts_dir = conpaas_home + '/scripts/cloud'
        agent_cfg_dir = conpaas_home + '/config/agent'
        agent_scripts_dir = conpaas_home + '/scripts/agent'

        bootstrap = self.config_parser.get('manager', 'BOOTSTRAP')
        manager_ip = self.config_parser.get('manager', 'MY_IP')

        # Get contextualization script for the corresponding cloud
        cloud_script_file = open(cloud_scripts_dir + '/' + cloud_type, 'r')
        cloud_script = cloud_script_file.read()

        # Get agent setup file
        agent_setup_file = open(agent_scripts_dir + '/agent-setup', 'r')
        agent_setup = Template(agent_setup_file.read()).safe_substitute(
            SOURCE=bootstrap)

        # Get agent config file - add to the default one the one specific
        # to the service if it exists
        default_agent_cfg_file = open(agent_cfg_dir + '/default-agent.cfg')
        agent_cfg = Template(default_agent_cfg_file.read()).safe_substitute(
            AGENT_TYPE=service_name,
            MANAGER_IP=manager_ip,
            CONPAAS_USER_ID=self.__conpaas_user_id,
            CONPAAS_SERVICE_ID=self.__conpaas_service_id,
            CONPAAS_APP_ID=self.__conpaas_app_id,
            IPOP_BASE_NAMESPACE=self.__ipop_base_namespace)

        # Add IPOP_BASE_IP, IPOP_NETMASK and IPOP_IP_ADDRESS if necessary
        if self.__ipop_base_ip and self.__ipop_netmask:
            agent_cfg += '\nIPOP_BASE_IP = %s' % self.__ipop_base_ip
            agent_cfg += '\nIPOP_NETMASK = %s' % self.__ipop_netmask
            agent_cfg += '\nIPOP_IP_ADDRESS = $IPOP_IP_ADDRESS'
            if self.__ipop_bootstrap_nodes is not None:
                agent_cfg += '\nIPOP_BOOTSTRAP_NODES = %s' % self.__ipop_bootstrap_nodes

        if os.path.isfile(agent_cfg_dir + '/' + service_name + '-agent.cfg'):
            agent_cfg_file = open(agent_cfg_dir +
                                  '/' + service_name + '-agent.cfg')
            agent_cfg += '\n' + agent_cfg_file.read()

        # Get agent start file - if none for this service, use the default one
        if os.path.isfile(agent_scripts_dir +
                          '/' + service_name + '-agent-start'):
            agent_start_file = open(agent_scripts_dir +
                                    '/' + service_name + '-agent-start')
        else:
            agent_start_file = open(agent_scripts_dir + '/default-agent-start')
        agent_start = agent_start_file.read()

        # Get key and a certificate from CA
        agent_certs = self._get_certificate()

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

        # Get user-provided startup script's absolute path
        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        startup_script = os.path.join(basedir, 'startup.sh')

        # Append user-provided startup script (if any)
        if os.path.isfile(startup_script):
            context_file += open(startup_script).read() + '\n'

        # Finally, the agent startup script
        context_file += agent_start + '\n'

        return context_file

    def _get_certificate(self):
        '''
        Requests a certificate from the CA
        '''
        parsed_url = urlparse.urlparse(self.__conpaas_caUrl)

        req_key = https.x509.gen_rsa_keypair()

        x509_req = https.x509.create_x509_req(
            req_key,
            userId=self.__conpaas_user_id,
            serviceLocator=self.__conpaas_service_id,
            O='ConPaaS',
            emailAddress='info@conpaas.eu',
            CN='ConPaaS',
            role='agent'
        )

        x509_req_as_pem = https.x509.x509_req_as_pem(x509_req)
        _, cert = https.client.https_post(parsed_url.hostname,
                                          parsed_url.port or 443,
                                          parsed_url.path,
                                          files=[('csr', 'csr.pem',
                                                  x509_req_as_pem)])
        cert_dir = self.config_parser.get('manager', 'CERT_DIR')
        ca_cert_file = open(os.path.join(cert_dir, 'ca_cert.pem'), 'r')
        ca_cert = ca_cert_file.read()

        certs = {'ca_cert': ca_cert,
                 'key': https.x509.key_as_pem(req_key),
                 'cert': cert}

        return certs

    def __force_terminate_service(self):
        # DO NOT release lock after acquiring it
        # to prevent the creation of more nodes
        self.__force_terminate_lock.acquire()
        self.__logger.debug('OUT OF CREDIT, TERMINATING SERVICE')

        # kill all partially created nodes
        self.delete_nodes(self.__partially_created_nodes)

        # kill all created nodes
        self.delete_nodes(self.__created_nodes)

        # notify front-end, attempt 10 times until successful
        for _ in range(10):
            try:
                parsed_url = urlparse.urlparse(self.__conpaas_terminateUrl)
                _, body = https.client.https_post(parsed_url.hostname,
                                                  parsed_url.port or 443,
                                                  parsed_url.path,
                                                  {'sid':
                                                      self.__conpaas_service_id})
                obj = json.loads(body)
                if not obj['error']:
                    break
            except:
                self.__logger.exception('Failed to terminate service')

    def deduct_credit(self, value):
        try:
            parsed_url = urlparse.urlparse(self.__conpaas_creditUrl)
            _, body = https.client.https_post(parsed_url.hostname,
                                              parsed_url.port or 443,
                                              parsed_url.path,
                                              {'sid': self.__conpaas_service_id,
                                               'decrement': value})
            obj = json.loads(body)
            return not obj['error']
        except:
            self.__logger.exception('Failed to deduct credit')
            return False

    def __deduct_and_check_credit(self, value):
        if not self.deduct_credit(value):
            self.__force_terminate_service()


class ReservationTimer(Thread):
    def __init__(self, nodes, delay, callback,
                 reservation_logger, interval=3600):

        Thread.__init__(self)
        self.nodes = nodes
        self.event = Event()
        self.delay = delay
        self.interval = interval
        self.callback = callback
        self.lock = Lock()
        self.reservation_logger = reservation_logger
        self.reservation_logger.debug('RTIMER Creating timer for %s'
                                      % (str(self.nodes)))

    def remove_node(self, node_id):
        with self.lock:
            self.nodes.remove(node_id)
            self.reservation_logger.debug('RTIMER removed node %s, '
                                          'updated list %s'
                                          % (node_id, str(self.nodes)))
        return len(self.nodes)

    def run(self):
        self.event.wait(self.delay)
        while not self.event.is_set():
            with self.lock:
                list_size = len(self.nodes)
                self.reservation_logger.debug('RTIMER charging user credit '
                                              'for hour of %d instances %s'
                                              % (list_size, str(self.nodes)))
            Thread(target=self.callback, args=[list_size]).start()
            self.event.wait(self.interval)

    def stop(self):
        self.event.set()

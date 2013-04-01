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


Created on Feb 8, 2011

@package conpaas.core
@file

'''

from threading import Thread, Lock, Event

from netaddr import IPNetwork

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

        if config_parser.has_option('manager', 'IPOP_SUBNET'):
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

        self.available_clouds = []
        self.__default_cloud = None
        if config_parser.has_option('iaas', 'DRIVER'):
            self.__default_cloud = iaas.get_cloud_instance(
                'iaas',
                config_parser.get('iaas', 'DRIVER').lower(),
                config_parser)

        if config_parser.has_option('iaas', 'CLOUDS'):
            self.available_clouds = iaas.get_clouds(config_parser)
            # if there is no default cloud defined in 'iaas'
            if self.__default_cloud is None:
                self.__default_cloud = self.available_clouds.pop(0)

        # Setting VM role
        self.role = 'agent'

    def get_available_ipop_address(self):
        """Return an unassigned IP address in this manager's VPN subnet"""
        # Network iterator
        network = self.__ipop_subnet.iter_hosts()
        
        # Currently running hosts
        running_hosts = [ str(node.ip) for node in self.__created_nodes ] 

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
            msg = '[_create_nodes]: iteration %d: creating %d nodes' % (
                iteration, count - len(ready))

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
                        self.update_context({ 'IPOP_IP_ADDRESS': vpn_ip })
                        
                        for newinst in cloud.new_instances(1, name, inst_type):
                            newinst.ip = vpn_ip
                            poll.append(newinst)

                        self.__logger.debug("cloud.new_instances: %s" % poll)
                else:
                    poll = cloud.new_instances(count - len(ready), name, inst_type)

                try:
                    self.__partially_created_nodes += poll
                except TypeError:
                    self.__partially_created_nodes.append(poll)
            except Exception as e:
                self.__logger.exception(
                    '[_create_nodes]: Failed to request new nodes')
                self.__kill_nodes(ready)
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
                self.__kill_nodes(failed)
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
        self.__kill_nodes(nodes)

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
                         for it, otherwise it will be generated for the default
                         cloud

            @param service_name Used to know which config_files and scripts
                                to select
        """

        if cloud is None:
            cloud = self.__default_cloud

        contxt = self._get_context_file(service_name, cloud.get_cloud_type())
        cloud.set_context_template(contxt)

    #=========================================================================#
    #               update_context(self, replace, cloud)                      #
    #=========================================================================#
    def update_context(self, replace={}, cloud=None):
        """Updates the contextualization file for the default/given cloud.

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

        """
        if cloud is None:
            cloud = self.__default_cloud

        contxt = cloud.get_context_template()
        contxt = Template(contxt).safe_substitute(replace)
        cloud.config(context=contxt)

    #=========================================================================#
    #               get_clouds(self)                                          #
    #=========================================================================#
    def get_clouds(self):
        """
            @return The list of cloud objects

        """
        return [self.__default_cloud] + self.available_clouds

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

    def __kill_nodes(self, nodes, cloud=None):
        if cloud is None:
            cloud = self.__default_cloud

        for node in nodes:
            self.__logger.debug('[_kill_nodes]: killing ' + str(node.id))
            try:
            # node may not be in map if it failed to start
                if node.id in self.__reservation_map:
                    timer = self.__reservation_map.pop(node.id)
                    if timer.remove_node(node.id) < 1:
                        timer.stop()
                cloud.kill_instance(node)
            except:
                self.__logger.exception('[_kill_nodes]: '
                                        'Failed to kill node %s', node.id)

    def __wait_for_nodes(self, nodes, test_agent,
                         port, poll_interval=10, cloud=None):
        if cloud is None:
            cloud = self.__default_cloud

        self.__logger.debug('[__wait_for_nodes]: going to start polling')
        done = []
        poll_cycles = 0
        while len(nodes) > 0:
            poll_cycles += 1
            for node in nodes:
                up = True
                try:
                    if node.ip != '' and node.private_ip != '':
                        self.__logger.debug('[__wait_for_nodes]: test_agent(%s, %s)' % (node.ip, port))
                        test_agent(node.ip, port)
                    else:
                        up = False
                except socket.error, err:
                    self.__logger.debug('[__wait_for_nodes]: %s' % err)
                    up = False
                if up:
                    # On this node the agent started fine.
                    done.append(node)
            nodes = [i for i in nodes if i not in done]
            if len(nodes):
                if poll_cycles * poll_interval > 180:
                    # at least 3mins of sleeping + poll time
                    return (done, nodes)

            self.__logger.debug('[_wait_for_nodes]: waiting for %d nodes'
                                % len(nodes))
            time.sleep(poll_interval)
            no_ip_nodes = [node for node in nodes
                           if node.ip == '' or node.private_ip == '']
            if no_ip_nodes:
                self.__logger.debug('[_wait_for_nodes]: refreshing %d nodes'
                                    % len(no_ip_nodes))
                refreshed_list = cloud.list_vms()
                for node in no_ip_nodes:
                    for refreshed_node in refreshed_list:
                        if refreshed_node.id == node.id:
                            node.ip = refreshed_node.ip
                            node.private_ip = refreshed_node.private_ip

        self.__logger.debug('[_wait_for_nodes]: All nodes are ready %s'
                            % str(done))
        return (done, [])

    def _get_context_file(self, service_name, cloud):
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
        cloud_script_file = open(cloud_scripts_dir + '/' + cloud, 'r')
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
        self.__kill_nodes(self.__partially_created_nodes)

        # kill all created nodes
        self.__kill_nodes(self.__created_nodes)

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

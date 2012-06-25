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
@author ielhelw, aaasz
@file

'''

from threading import Thread, Lock, Timer, Event
import inspect, tempfile, os, os.path, tarfile, time, stat, json, urlparse
from string import Template

from conpaas.core.log import create_logger
from conpaas.core.http import HttpJsonResponse, HttpErrorResponse,\
                         HttpFileDownloadResponse, HttpRequest,\
                         FileUploadField, HttpError, _http_post

from conpaas.core.node import ServiceNode
from conpaas.core import iaas
from conpaas.core.misc import get_ip_address

class Controller(object):
    """Implementation of the clouds controller. This class implements functions
       to easily work with the available cloud objects.

       So far, it provides the following functionalities/abstractions:
         - crediting system (also terminate service when user out of credits)
         - adding nodes (VMs)    
         - removing nodes (VMs)
    """

    def __init__(self, config_parser, **kwargs):
        # Params for frontend callback
        self.__fe_creditUrl = config_parser.get('manager', \
                                                'FE_CREDIT_URL')
        self.__fe_terminateUrl = config_parser.get('manager', \
                                                   'FE_TERMINATE_URL')
        self.__fe_service_id = config_parser.get('manager', \
                                                 'FE_SERVICE_ID')

        # For crediting system
        self.__reservation_logger = create_logger('ReservationTimer')
        self.__reservation_map = {
                               'manager': ReservationTimer(['manager'],
                               55 * 60,# 55mins
                               self.__deduct_and_check_credit,
                               self.__reservation_logger)
        }
        self.__reservation_map['manager'].start()
        self.__force_terminate_lock = Lock()
        
        self.__config_parser = config_parser
        self.__created_nodes = []
        self.__partially_created_nodes = []
        self.__logger = create_logger(__name__)

        # TODO: for now, it receives only 1 cloud credentials - we will 
        # modify this in the near future
        drivername = config_parser.get('iaas', 'DRIVER').lower()
        self.__default_cloud = iaas.get_cloud_instance('iaas', \
                                               drivername,   \
                                               config_parser)

    #===========================================================================#
    #                create_nodes(self, count, contextFile, test_agent)         #
    #===========================================================================#
    #TODO: be able to select cloud
    def create_nodes(self, count, test_agent, port, cloud = None):
        """Creates the VMs associated with the list of nodes. It also tests
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
        iteration = 0

        if not self.__deduct_credit(count):
            raise Exception('Could not add nodes. Not enough credits.')
      
        while len(ready) < count:
            iteration += 1
            self.__logger.debug('[_create_nodes]: iteration %d: creating %d nodes' \
                          % (iteration, count - len(ready)))
            try:
                self.__force_terminate_lock.acquire()
                if iteration == 1:
                    request_start = time.time()
                poll = self.__default_cloud.new_instances(count - len(ready))
                self.__partially_created_nodes += poll
            except Exception as e:
                self.__logger.exception('[_create_nodes]: Failed to request new nodes')
                self.__kill_nodes(ready)
                self.__partially_created_nodes = []
                raise e
            finally:
                self.__force_terminate_lock.release()
            poll, failed = self.__wait_for_nodes(poll, test_agent, port)
            ready += poll
            poll = []
            if failed:
                self.__logger.debug('[_create_nodes]: %d nodes ' \
                                    'failed to startup properly: %s' \
                                    % (len(failed), str(failed)))
                self.__kill_nodes(failed)   

        additional_nodes = ready
        self.__force_terminate_lock.acquire()
        #self.__created_nodes += additional_nodes
        self.__created_nodes += ready
        self.__partially_created_nodes = []
        self.__force_terminate_lock.release()
    
        # start reservation timer with slack of 3 mins + time already wasted
        # this should be enough time to terminate instances before
        # hitting the following hour
        timer = ReservationTimer([ i.id for i in ready ],
                               (55 * 60) - (time.time() - request_start),
                               self.__deduct_and_check_credit,
                               self.__reservation_logger)
        timer.start()
        # set mappings
        for i in ready:
            self.__reservation_map[i.id] = timer
        return additional_nodes

    #===========================================================================#
    #                     delete_nodes(self, nodes)                             #
    #===========================================================================#
    def delete_nodes(self, nodes):
        """Kills the VMs associated with the list of nodes.
    
            @param nodes The list of nodes to be removed - a node must be of type 
                         ServiceNode or a class that extends ServiceNode
        """
      
        self.__kill_nodes(nodes)

    #===========================================================================#
    #                     list_vms(self, cloud=None)                            #
    #===========================================================================#
    def list_vms(self, cloud=None):
        """Returns an array with the VMs running at the given/default(s) cloud.
    
            @param cloud (Optional) If specified, this method will return the
                         VMs already running at the given cloud
        """    
        if cloud != None:
            c = cloud         
        else:
            c = self.__default_cloud

        #TODO: return ServiceNode(s)
        return c.list_vms()

    #===========================================================================#
    #                generate_context(self, service_name, replace, cloud)       #
    #===========================================================================#
    def generate_context(self, service_name, cloud = None, ip_whitelist = None):
        """Generates the contextualization file for the default/given cloud.
    
            @param cloud (Optional) If specified, the context will be generated
                         for it, otherwise it will be generated for the default
                         cloud

            @param service_name Used to know which config_files and scripts
                                to select      
        """
 
        if cloud != None:
            c = cloud         
        else:
            c = self.__default_cloud
        contxt = self._get_context_file(service_name, \
                                        c.get_cloud_type())
        c.set_context_template(contxt)

    #===========================================================================#
    #                update_context(self, replace, cloud)                       #
    #===========================================================================#
    def update_context(self, replace = {}, cloud = None):
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
 
        if cloud != None:
            c = cloud         
        else:
            c = self.__default_cloud
        contxt = c.get_context_template()
        contxt = Template(contxt).safe_substitute(replace)
        c.config(context=contxt)

    #===========================================================================#
    #                get_clouds(self)                                           #
    #===========================================================================#
    # TODO: For now we work on just one cloud
    def get_clouds(self):
        """
            @return The list of cloud objects
        
        """
        return [self.__default_cloud]


    #===========================================================================#
    #                config_cloud(self, cloud, config_params)                   #
    #===========================================================================#
    def config_cloud(self, cloud, config_params):
        """Configures some parameters in the given cloud
  
            @param cloud The cloud to be configured
            
            @param config_params A dictionary containing the configuration 
                                 parameters (are specific to the cloud)
        """
        cloud.config(config_params)

    #===========================================================================#

    def __kill_nodes(self, nodes):
    #TODO: send also the cloud
      for node in nodes:
        self.__logger.debug('[_kill_nodes]: killing ' + str(node.id))
        try:
          # node may not be in map if it failed to start
          if node.id in self.__reservation_map:
            timer = self.__reservation_map.pop(node.id)
            if timer.remove_node(node.id) < 1:
              timer.stop()
          self.__default_cloud.kill_instance(node)
        except: self.__logger.exception('[_kill_nodes]: ' \
                                      'Failed to kill node %s', node.id)
  
    def __wait_for_nodes(self, nodes, test_agent, port, poll_interval=10):
      self.__logger.debug('[__wait_for_nodes]: going to start polling')
      done = []
      poll_cycles = 0
      while len(nodes) > 0:
        poll_cycles += 1
        for node in nodes:
          up = True
          try:
            if node.ip != '' and node.private_ip != '':
              test_agent(node.ip, port)
            else:
              up = False
          except:
              up = False
          if up:
            # On this node the agent started fine.
            done.append(node)
        nodes = [ i for i in nodes if i not in done]
        if len(nodes):
          if poll_cycles * poll_interval > 180:
            # at least 3mins of sleeping + poll time
            return (done, nodes)

          self.__logger.debug('[_wait_for_nodes]: waiting for %d nodes' \
                            % len(nodes))
          time.sleep(poll_interval)
          no_ip_nodes = [ node for node in nodes if node.ip == '' or node.private_ip == '']
          if no_ip_nodes:
            self.__logger.debug('[_wait_for_nodes]: refreshing %d nodes' \
                              % len(no_ip_nodes))
            refreshed_list = self.__default_cloud.list_vms()
            for node in no_ip_nodes:
              node.ip = refreshed_list[node.id]['ip']
              node.private_ip = refreshed_list[node.id]['private_ip']

      self.__logger.debug('[_wait_for_nodes]: All nodes are ready %s' \
                        % str(done))
      return (done, [])

    def _get_context_file(self, service_name, cloud):
      conpaas_home = self.__config_parser.get('manager', 'CONPAAS_HOME')
      cloud_scripts_dir = conpaas_home + '/scripts/cloud'
      agent_cfg_dir = conpaas_home + '/config/agent'
      agent_scripts_dir = conpaas_home + '/scripts/agent'

      bootstrap = self.__config_parser.get('manager', 'BOOTSTRAP')
      manager_ip = self.__config_parser.get('manager', 'MY_IP')

      # Get contextualization script for the corresponding cloud
      cloud_script_file = open(cloud_scripts_dir + '/' + cloud, 'r')
      cloud_script = cloud_script_file.read()

      # Get agent setup file 
      agent_setup_file = open(agent_scripts_dir + '/agent-setup', 'r')
      agent_setup = Template(agent_setup_file.read()). \
                                     safe_substitute(SOURCE=bootstrap)

      # Get agent config file - add to the default one the one specific
      # to the service if it exists
      default_agent_cfg_file = open(agent_cfg_dir + '/default-agent.cfg')
      agent_cfg = Template(default_agent_cfg_file.read()). \
                           safe_substitute(AGENT_TYPE=service_name, \
                                           MANAGER_IP=manager_ip)

      if os.path.isfile(agent_cfg_dir + '/' + service_name + '-agent.cfg'):
          agent_cfg_file = open(agent_cfg_dir + '/'+ service_name + '-agent.cfg')
          agent_cfg += '\n' + agent_cfg_file.read()

      # Get agent start file - if none for this service, use the default one
      if os.path.isfile(agent_scripts_dir + '/' + service_name + '-agent-start'):
          agent_start_file = open(agent_scripts_dir + \
                                '/'+ service_name + '-agent-start')
      else:
          agent_start_file = open(agent_scripts_dir + '/default-agent-start')
      agent_start = agent_start_file.read()

      ## Concatenate the files
      context_file = cloud_script + '\n\n'
      context_file += agent_setup + '\n\n'
      context_file += 'cat <<EOF > $ROOT_DIR/config.cfg\n'
      context_file += agent_cfg + '\n' + 'EOF\n\n'
      context_file += agent_start + '\n'

      return context_file

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
          parsed_url = urlparse.urlparse(self.__fe_terminateUrl)
          _, body = _http_post(parsed_url.hostname, 
                               parsed_url.port or 80,
                               parsed_url.path, 
                               {'sid': self.__fe_service_id})
          obj = json.loads(body)
          if not obj['error']: break
        except:
          self.__logger.exception('Failed to terminate service')
  
    def __deduct_credit(self, value):
      try:
        parsed_url = urlparse.urlparse(self.__fe_creditUrl)
        _, body = _http_post(parsed_url.hostname, parsed_url.port or 80,
                             parsed_url.path, {'sid': self.__fe_service_id,
                                               'decrement': value})
        obj = json.loads(body)
        return not obj['error']
      except:
        self.__logger.exception('Failed to deduct credit')
        return False
  
    def __deduct_and_check_credit(self, value):
      if not self.__deduct_credit(value):
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
      self.reservation_logger.debug('RTIMER Creating timer for %s' \
                                    % (str(self.nodes)))

    def remove_node(self, node_id):
      with self.lock:
        self.nodes.remove(node_id)
        self.reservation_logger.debug('RTIMER removed node %s, ' \
                                      'updated list %s' \
                                      % (node_id, str(self.nodes)))
        return len(self.nodes)

    def run(self):
      self.event.wait(self.delay)
      while not self.event.is_set():
        with self.lock:
          list_size = len(self.nodes)
          self.reservation_logger.debug('RTIMER charging user credit for ' \
                                        'hour of %d instances %s' \
                                        % (list_size, str(self.nodes)))
        Thread(target=self.callback, args=[list_size]).start()
        self.event.wait(self.interval)

    def stop(self):
      self.event.set()
      

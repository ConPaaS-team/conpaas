import inspect, tempfile, os, os.path, tarfile, time, stat, json, urlparse
from string import Template

def _get_context_file(service_name, cloud):
      #conpaas_home = self.__config_parser.get('manager', 'CONPAAS_HOME')
      #self.__logger.debug('Conpaas_home = %s' % conpaas_home)
      conpaas_home = '/home/adriana/Desktop/contrail_v4/conpaas'
      cloud_scripts_dir = conpaas_home + '/scripts/cloud'
      #self.__logger.debug(cloud_scripts_dir + '/' + cloud)
      cloud_cfg_dir = conpaas_home + '/config/cloud'
      agent_cfg_dir = conpaas_home + '/config/agent'
      agent_scripts_dir = conpaas_home + '/scripts/agent'

      #self.__logger.debug(cloud_scripts_dir + '/' + cloud)
      bootstrap = 'bootstrap' #self.__config_parser.get('manager', 'BOOTSTRAP')
      #self.__logger.debug(bootstrap)


      # Get contextualization script for the cloud in which the manager resides
      #self.__logger.debug(cloud_scripts_dir + '/' + cloud)
      #try:  
      cloud_script_file = open(cloud_scripts_dir + '/' + cloud, 'r')
      #except:
      #  raise Exception('Could not read file')
 
      #self.__logger.debug('opened' + cloud_scripts_dir + '/' + cloud)
      cloud_script = cloud_script_file.read()
      #self.__logger.debug('Got contextualization script for the cloud')

      # Get agent setup file 
      agent_setup_file = open(agent_scripts_dir + '/agent-setup', 'r')
      #agent_setup = Template(agent_setup_file.read()).safe_substitute(SOURCE=bootstrap,
      #                                                                           MANAGER_IP=get_ip_address('eth0'))
      #self.__logger.debug('Got agent-setup file')

      # Get cloud config file
      cloud_cfg_file = open(cloud_cfg_dir + '/' + cloud + '.cfg', 'r')
      cloud_cfg = cloud_cfg_file.read()
      #self.__logger.debug('Got cloud config file')

      # Get agent config file - if none for this service, use the default one
      if os.path.isfile(agent_cfg_dir + '/' + service_name + '-agent.cfg'):
        agent_cfg_file = open(agent_cfg_dir + '/'+ service_name + '-agent.cfg')
      else:
        agent_cfg_file = open(agent_cfg_dir + '/default-agent.cfg')
      agent_cfg = Template(agent_cfg_file.read()). \
                           safe_substitute(AGENT_TYPE=service_name)

      # Get agent start file - if none for this service, use the default one
      if os.path.isfile(agent_scripts_dir + '/' + service_name + '-agent-start'):
        agent_start_file = open(agent_scripts_dir + '/'+ service_name + '-agent-start')
      else:
        agent_start_file = open(agent_scripts_dir + '/default-agent-start')
      agent_start = agent_start_file.read()

      ## Concatenate the files
      context_file = cloud_script + '\n\n'
      #context_file += agent_setup + '\n\n'
      context_file += 'cat <<EOF > $ROOT_DIR/config.cfg\n'
      context_file += cloud_cfg + '\n'
      context_file += agent_cfg + '\n' + 'EOF\n\n'
      context_file += agent_start + '\n'

      return context_file

if __name__ == "__main__":
  print _get_context_file('helloworld', 'opennebula')

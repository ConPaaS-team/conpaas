import inspect, tempfile, os, os.path, tarfile, time, stat, json, urlparse
from string import Template

import re
import unittest

from conpaas.core import git

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

class TestGit(unittest.TestCase):

  def setUp(self):
    git.AUTH_KEYS_FILENAME = "/tmp/conpaas_git_authorized_keys"
    open(git.AUTH_KEYS_FILENAME, 'w').write("")

  def test_01_empty_authorized_keys(self):
    # get_authorized_keys should return 0 with an empty file
    self.assertEquals(0, len(git.get_authorized_keys()))

  def test_02_add_authorized_keys(self):
    new_keys = [ "ssh-rsa test123 ema@uranus" ]

    # add_authorized_keys should return 1 on successful insertion
    self.assertEquals(1, git.add_authorized_keys(new_keys))

    # add_authorized_keys should return 0 if the key is already present
    self.assertEquals(0, git.add_authorized_keys(new_keys))

    # we should now have exactly 1 authorized key
    self.assertEquals(1, len(git.get_authorized_keys()))

    # adding a new one
    self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test ema@mars" ]))

    # we should now have exactly 2 authorized keys
    self.assertEquals(2, len(git.get_authorized_keys()))

  def test_03_remove_authorized_keys(self):
    # 0 keys left in a empty authorized_keys
    self.assertEquals(0, git.remove_authorized_keys([]))    

    # adding one key
    self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test ema@mars" ]))

    # we should now have exactly 1 authorized key
    self.assertEquals(1, len(git.get_authorized_keys()))

    # adding another key
    self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test2 ema@mars" ]))

    # we should now have exactly 2 authorized keys
    self.assertEquals(2, len(git.get_authorized_keys()))

    # adding another key
    self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test3 ema@mars" ]))

    # we should now have exactly 3 authorized keys
    self.assertEquals(3, len(git.get_authorized_keys()))

    # removing a single key should leave us with 2 keys
    self.assertEquals(2, git.remove_authorized_keys([ "ssh-rsa test2 ema@mars" ]))

    # we should now have exactly 2 authorized keys
    self.assertEquals(2, len(git.get_authorized_keys()))

    # removing the two remaining keys
    self.assertEquals(0, git.remove_authorized_keys(
        [ "ssh-rsa test ema@mars", "ssh-rsa test3 ema@mars" ]
    ))

    # we should now have no authorized_key left
    self.assertEquals(0, len(git.get_authorized_keys()))

  def test_05_git_code_version(self):
    repo = git.git_create_tmp_repo() 
    code_version = git.git_code_version(repo)

    # git_code_version should something like '68ed1b0'
    self.assertIsNot(None, re.match("^[a-z0-9]{7,7}$", code_version))

  def test_06_git_last_description(self):
    repo = git.git_create_tmp_repo() 
    self.assertEquals("Initial commit", git.git_last_description(repo))

  def test_07_git_enable_revision(self):
    target_dir = tempfile.mkdtemp()
    repo = git.git_create_tmp_repo()
    rev = git.git_code_version(repo) 

    dest_dir = git.git_enable_revision(target_dir, repo, rev)

    self.assertEquals(rev, os.path.basename(dest_dir))

if __name__ == "__main__":
  #print _get_context_file('helloworld', 'opennebula')
  unittest.main()

'''
Created on Jul 4, 2011

@author: ielhelw
'''
from os.path import exists
from conpaas.web.manager.server import DeploymentManager

if __name__ == '__main__':
  from optparse import OptionParser
  from ConfigParser import ConfigParser
  import sys
  
  parser = OptionParser()
  parser.add_option('-p', '--port', type='int', default=80, dest='port')
  parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
  parser.add_option('-c', '--config', type='string', default=None, dest='config')
  parser.add_option('-s', '--scalaris', type='string', default=None, dest='scalaris')
  options, args = parser.parse_args()
  
  if options.scalaris == None:
    print >>sys.stderr, 'Scalaris IP is required'
    sys.exit(1)
  
  if not options.config or not exists(options.config):
    print >>sys.stderr, 'Failed to find configuration file'
    sys.exit(1)
  
  config_parser = ConfigParser()
  try:
    config_parser.read(options.config)
  except:
    print >>sys.stderr, 'Failed to read configuration file'
    sys.exit(1)
  if not config_parser.has_section('manager')\
  or not config_parser.has_option('manager', 'TYPE')\
  or not config_parser.has_option('manager', 'MEMCACHE_ADDR')\
  or not config_parser.has_option('manager', 'CODE_REPO')\
  or not config_parser.has_option('manager', 'LOG_FILE')\
  or not config_parser.has_option('manager', 'BOOTSTRAP'):
    print >>sys.stderr, 'Missing configuration variables for section "manager"'
    sys.exit(1)
  
  print options.address, options.port
  d = DeploymentManager((options.address, options.port),
                        config_parser,
                        options.scalaris,
                        reset_config=True)
  d.serve_forever()

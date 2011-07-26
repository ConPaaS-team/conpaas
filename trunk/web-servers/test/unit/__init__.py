from ConfigParser import ConfigParser

# init logging
config_parser = ConfigParser()
config_parser.add_section('manager')
config_parser.set('manager', 'LOG_FILE', '/dev/null')
from conpaas import log
log.init(config_parser)

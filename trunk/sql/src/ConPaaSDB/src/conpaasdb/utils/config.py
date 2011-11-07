import os
import urlparse
import colander as cl
from ConfigParser import ConfigParser

from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

def is_url(node, url):
    parts = urlparse.urlsplit(url)
    if not parts.scheme in ('http', 'https') and parts.netloc:
        raise cl.Invalid(node, 'Invalid url "%s"' % url)

def path_exists(node, path):
    if not os.path.exists(path):
        raise cl.Invalid(node, 'Path "%s" does not exist' % path)

def is_port(node, val):
    cl.Range(0, 65535)(node, val)

class ConfigContainer(object):
    def __init__(self, node):
        for key, value in node.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigContainer(value))
            else:
                setattr(self, key, value)

@flog
def get_config(file, schema):
    if not os.path.exists(file):
        raise ValueError('Config file "%s" does not exist.' % file)
    
    if callable(schema):
        schema = schema()
    
    config_parser = ConfigParser()
    config_parser.read(file)
    
    original = {}
    
    for section, values in config_parser._sections.items():
        values.pop('__name__')
        original[section] = values
    
    valid = schema.deserialize(original)
    
    config = ConfigContainer(valid)
    
    return config

import os
import sys
from ConfigParser import ConfigParser

dirname = os.path.dirname(__file__)
CONFFILE = os.path.join(dirname, "director.cfg")

config = ConfigParser()
config.read(CONFFILE)

def extend_path():
    """Add ConPaaS src to the PYTHONPATH"""
    root_dir = config.get('conpaas', 'ROOT_DIR')
    sys.path.append(os.path.join(root_dir, "src"))
    sys.path.append(os.path.join(root_dir, "contrib"))

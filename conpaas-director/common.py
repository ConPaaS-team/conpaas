import os
from ConfigParser import ConfigParser

dirname = os.path.dirname(__file__)
CONFFILE = os.path.join(dirname, "director.cfg")

config = ConfigParser()
config.read(CONFFILE)

import os
import readline

from pwd import getpwnam
from grp import getgrnam

from ConfigParser import ConfigParser

CONFFILE = os.getenv('DIRECTOR_CFG')

if not CONFFILE:
    CONFFILE = "/etc/cpsdirector/director.cfg"

config_parser = ConfigParser()
config_parser.read(CONFFILE)

# Config values for unit testing
if os.getenv('DIRECTOR_TESTING'):
    # dummy cloud
    config_parser.set("iaas", "DRIVER", "dummy")
    config_parser.set("iaas", "USER", "dummy")

    # separate database
    config_parser.set("director", "DATABASE_URI", "sqlite:///director-test.db")
    config_parser.set("director", "DIRECTOR_URL", "")

def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try: 
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()

def chown(path, username, groupname):
    os.chown(path, getpwnam(username).pw_uid, getgrnam(groupname).gr_gid)

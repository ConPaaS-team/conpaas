import os
import readline

from pwd import getpwnam
from grp import getgrnam

from ConfigParser import ConfigParser

CONFFILE = "/etc/cpsdirector/director.cfg"

config = ConfigParser()
config.read(CONFFILE)

# Config values for unit testing
if os.getenv('DIRECTOR_TESTING'):
    # dummy cloud
    config.set("iaas", "DRIVER", "dummy")
    config.set("iaas", "USER", "dummy")

    # separate database
    config.set("director", "DATABASE_URI", "sqlite:///director-test.db")
    config.set("director", "DIRECTOR_URL", "")

def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try: 
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()

def chown(path, username, groupname):
    os.chown(path, getpwnam(username).pw_uid, getgrnam(groupname).gr_gid)

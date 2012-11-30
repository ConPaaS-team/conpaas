import os
import readline

from pwd import getpwnam
from grp import getgrnam

from ConfigParser import ConfigParser

CONFFILE = "/etc/cpsdirector/director.cfg"

config = ConfigParser()
config.read(CONFFILE)

def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try: 
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()

def chown(path, username, groupname):
    os.chown(path, getpwnam(username).pw_uid, getgrnam(groupname).gr_gid)

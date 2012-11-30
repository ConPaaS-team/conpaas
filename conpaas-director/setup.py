#!/usr/bin/env python

import os
import sys
import shutil
from pwd import getpwnam
from grp import getgrnam

from setuptools import setup
from pkg_resources import Requirement, resource_filename

CONFDIR = '/etc/cpsdirector'

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='cpsdirector',
      version='1.1.0',
      description='ConPaaS director',
      author='Emanuele Rocca',
      author_email='ema@linux.it',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=[ 'cpsdirector', ],
      include_package_data=True,
      zip_safe=False,
      package_data={ 'cpsdirector': [ 'ConPaaS.tar.gz', ] },
      data_files=[ ( CONFDIR, [ 'director.cfg.example', 'ConPaaS.tar.gz' ] ), ],
      scripts=[ 'cpsadduser.py', 'director.wsgi', 'cpsconf.py' ],
      install_requires=[ 'cpslib', 'flask-sqlalchemy', 'apache-libcloud==0.8.0' ],
      dependency_links=[ 'http://www.linux.it/~ema/conpaas/cpslib-1.1.0.tar.gz', ],)

if __name__ == "__main__" and sys.argv[1] == "install":
    # overwrite /etc/cpsdirector/{config,scripts}
    for what in 'config', 'scripts':
        targetdir = os.path.join(CONFDIR, what)
        if os.path.isdir(targetdir):
            shutil.rmtree(targetdir)

        shutil.copytree(os.path.join('conpaas', what), targetdir)

    if not os.path.exists(os.path.join(CONFDIR, "director.cfg")):
        # copy director.cfg.example under CONFDIR/director.cfg
        conffile = resource_filename(Requirement.parse("cpsdirector"), 
            "director.cfg.example")
        shutil.copyfile(conffile, os.path.join(CONFDIR, "director.cfg"))

    # create 'certs' dir
    if not os.path.exists(os.path.join(CONFDIR, "certs")):
        os.mkdir(os.path.join(CONFDIR, "certs"))

    # set www-data as the owner of CONFDIR
    os.chown(CONFDIR, getpwnam('www-data').pw_uid, getgrnam('www-data').gr_gid)
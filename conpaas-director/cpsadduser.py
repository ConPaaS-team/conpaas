#!/usr/bin/env python

"""utility script for ConPaaS director: add user"""

import sys
import getpass

import sqlalchemy

from cpsdirector import db, common
from cpsdirector.user import create_user

from conpaas.core.misc import rlinput

if __name__ == "__main__":
    db.create_all()
    try:
        email, username, password = sys.argv[1:]
    except ValueError:
        print "\nAdd new ConPaaS user"
        email = rlinput('E-mail: ')
        username = rlinput('Username: ')
        pprompt = lambda: (getpass.getpass(),
                           getpass.getpass('Retype password: '))

        password, p2 = pprompt()

        while password != p2:
            print('Passwords do not match. Try again')
            password, p2 = pprompt()

    try:
        create_user(username, "", "", email, "", password, 50)
    except sqlalchemy.exc.IntegrityError:
        print "User %s already present" % username

    common.chown(common.config_parser.get('director',
        'DATABASE_URI').replace('sqlite:///', ''), 'www-data', 'www-data')

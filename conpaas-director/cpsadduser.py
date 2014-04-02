#!/usr/bin/env python

"""utility script for ConPaaS director: add user"""

import sys
import getpass

import sqlalchemy
import json

from cpsdirector import db, common
from cpsdirector.user import create_user

from conpaas.core.misc import rlinput

if __name__ == "__main__":
    db.create_all()
    credit = 50
    try:
        args = sys.argv[1:]
        if '-h' in args or '--help' in args:
            print "Usage: %s email username password [credit=%s]" % (sys.argv[0], credit)
            exit(0)
        if len(args) == 3:
            email, username, password = args
        else:
            email, username, password, credit = args
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
        create_user(username, "", "", email, "", password, credit, "")
         # here we don't fill in: fname, lname, affiliation, uuid
    except sqlalchemy.exc.IntegrityError as e:
        print "User %s already present" % username
        print "Statement: %s" % e.statement
        print "Orig: %s" % e.orig
        print "Params: %s" % json.dumps(e.params)

    common.chown(common.config_parser.get('director',
        'DATABASE_URI').replace('sqlite:///', ''), 'www-data', 'www-data')

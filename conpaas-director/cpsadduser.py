#!/usr/bin/env python

"""ConPaaS director: add user"""

import sys
import getpass

import sqlalchemy

from cpsdirector import db, common, create_user

if __name__ == "__main__":
    db.create_all()
    try:
        email, username, password = sys.argv[1:]

    except ValueError:
        print "\nAdd new ConPaaS user"
        email    = common.rlinput('E-mail: ')
        username = common.rlinput('Username: ')
        pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

        password, p2 = pprompt()

        while password != p2:
            print('Passwords do not match. Try again')
            password, p2 = pprompt()


    try:
        create_user(username, "", "", email, "", password, 120)
    except sqlalchemy.exc.IntegrityError:
        print "User %s already present" % username

    common.chown(common.config.get('director',
        'DATABASE_URI').replace('sqlite:///', ''), 'www-data', 'www-data')

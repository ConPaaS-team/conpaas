#!/usr/bin/env python

"""ConPaaS director: add user"""

import sys
import getpass

from cpsdirector import db, common, create_user

if __name__ == "__main__":
    db.create_all()
    try:
        email, username, password = sys.argv[1:]
        create_user(username, "", "", email, "", password, 120)

    except ValueError:
        print "\nAdd new ConPaaS user"
        email    = common.rlinput('E-mail: ')
        username = common.rlinput('Username: ')
        pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

        p1, p2 = pprompt()

        while p1 != p2:
            print('Passwords do not match. Try again')
            p1, p2 = pprompt()

        create_user(username, "", "", email, "", p1, 120)

    common.chown(common.config.get('director',
        'DATABASE_URI').replace('sqlite:///', ''), 'www-data', 'www-data')

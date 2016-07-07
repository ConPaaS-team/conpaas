
import argcomplete
import getpass
import logging
import StringIO
import sys
import traceback
import zipfile

from .base import BaseClient
from .config import config

from conpaas.core import https


## TODO: should be configurable in cps-tools.conf
DEFAULT_CREDIT = 50


try:
    import sqlalchemy
    import cpsdirector
    HAS_LOCAL_DIRECTOR = True
except ImportError:
    HAS_LOCAL_DIRECTOR = False


class UserCmd:

    def __init__(self, user_parser, client):
        self.client = client

        self.subparsers = user_parser.add_subparsers(help=None, title=None,
                                                     metavar="<sub-command>",
                                                     description=None)
        self._add_create()
        self._add_create_free()
        self._add_get_certificate()
        self._add_get_config()
        self._add_get_credit()
        self._add_add_credit()
        self._add_list()
        self._add_help(user_parser)

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)

    def _check_director(self):
        if not HAS_LOCAL_DIRECTOR:
            raise Exception("Cannot find a ConPaaS director on this machine.")

    # ========== help
    def _add_help(self, user_parser):
        help_parser = self.add_parser('help', help="show help")
        help_parser.set_defaults(run_cmd=self.user_help, parser=user_parser)

    def user_help(self, args):
        args.parser.print_help()

    # ========== create_free
    def _add_create_free(self):
        subparser = self.add_parser('create_free',
                                    help="create a new user for free with limited credit")
        subparser.add_argument('username', help="User's username")
        subparser.add_argument('--email', help="User's email")
        subparser.add_argument('--fname', help="User's first name")
        subparser.add_argument('--lname', help="User's last name")
        subparser.add_argument('--affiliation', help="User's affiliation")
        subparser.add_argument('--password', help="User's password")
        subparser.add_argument('--credit', metavar='CRED', type=int,
                               default=DEFAULT_CREDIT, help="Initial credit")
        subparser.set_defaults(run_cmd=self.create_user, arser=subparser)

    def create_user(self, args):
        """Create a new user calling the Director's REST API."""
        username, fname, lname, email, affiliation, password, credit = \
            self._get_new_user_args(args)
        arguments = {'username': username,
                     'fname': fname,
                     'lname': lname,
                     'email': email,
                     'affiliation': affiliation,
                     'password': password,
                     'credit': credit, }
        self.client.call_director_post('new_user', arguments)

        print("User %s created." % username)

    # ========== create
    def _add_create(self):
        subparser = self.add_parser('create', help="create a new user (on director's machine only)")
        subparser.add_argument('username', help="User's username")
        subparser.add_argument('--email', help="User's email")
        subparser.add_argument('--fname', help="User's first name")
        subparser.add_argument('--lname', help="User's last name")
        subparser.add_argument('--affiliation', help="User's affiliation")
        subparser.add_argument('--password', help="User's password")
        subparser.add_argument('--credit', metavar='CRED', type=int,
                               default=DEFAULT_CREDIT, help="Initial credit")

        # VERSION 1: calling director through an HTTP call
#         create_parser.set_defaults(run_cmd=self.create_user,
#                                    parser=create_parser)
        # VERSION 2: calling director locally, assuming this machine is running
        #            the director
        subparser.set_defaults(run_cmd=self.create_user_local, arser=subparser)

    def create_user_local(self, args):
        """Create a new user calling directly the local director."""
        self._check_director()
        username, fname, lname, email, affiliation, password, credit = \
            self._get_new_user_args(args)
        cpsdirector.user.create_user(username, fname, lname, email,
                                     affiliation, password, credit)

    def _get_new_user_args(self, args):
        if args.username is not None or len(args.username) > 0:
            username = args.username
        else:
            raise Exception("Missing user's username.")

        if args.fname is not None:
            fname = args.fname
        else:
            fname = ""

        if args.lname is not None:
            lname = args.lname
        else:
            lname = ""

        if args.affiliation is not None:
            affiliation = args.affiliation
        else:
            affiliation = ""

        if args.email is not None and len(args.email) > 0:
            email = args.email
        else:
            email = ""
            while len(email) == 0:
                email = raw_input('Enter user email address: ')

        if args.password is not None:
            password = args.password
        else:
            pprompt = lambda: (getpass.getpass(),
                               getpass.getpass('Retype password: '))
            password, p2 = pprompt()

            while password != p2:
                print('Passwords do not match. Try again')
                password, p2 = pprompt()

        if args.credit is not None:
            credit = args.credit
        else:
            credit = DEFAULT_CREDIT
        if credit <= 0:
            raise Exception("Cannot create a user with %s credits." % credit)

        return username, fname, lname, email, affiliation, password, credit

    # ========== list
    def _add_list(self):
        subparser = self.add_parser('list', help="list users (on director's machine only)")
        subparser.set_defaults(run_cmd=self.list_users, parser=subparser)
        subparser.add_argument('--credit', action='store_true',
                               help="display their credit")

    def list_users(self, args):
        self._check_director()
        users = cpsdirector.user.list_users()
        users = sorted(users, key=lambda user: user.username)
        if args.credit:
            for user in users:
                print("%s\t%s" % (user.username, user.credit))
        else:
            for user in users:
                print("%s" % user.username)

    # ========== get_certificate
    def _add_get_certificate(self):
        subparser = self.add_parser('get_certificate',
                                    help="get the user's certificate")
        subparser.set_defaults(run_cmd=self.get_certificate, parser=subparser)

    def get_certificate(self, args):
        res = self.client.call_director_post("getcerts", {}, use_certs=False)

        zipdata = zipfile.ZipFile(StringIO.StringIO(res))
        zipdata.extractall(path=self.client.confdir)
        https.client.conpaas_init_ssl_ctx(self.client.confdir, 'user')

        print "User certificates installed successfully."

    # ========== get_config
    def _add_get_config(self):
        subparser = self.add_parser('get_config', help="get user configuration")
        subparser.set_defaults(run_cmd=self.get_config, parser=subparser)

    def get_config(self, args):
        res = self.client.call_director_get("user_config")
        if not res:
            raise Exception("failed to authenticate user with user certificate.")
        else:
            for key, value in res.items():
                print "%s: %s" % (key, value)

    # ========== get_credit
    def _add_get_credit(self):
        subparser = self.add_parser('get_credit', help="get user current credit")
        subparser.set_defaults(run_cmd=self.get_credit, parser=subparser)

    def get_credit(self, args):
        res = self.client.call_director_get("user_credit")
        if not res:
            raise Exception("failed to authenticate user with user certificate.")
        print "%s" % res

    # ========== get_credit
    def _add_add_credit(self):
        subparser = self.add_parser('add_credit', help="add credit to user")
        subparser.set_defaults(run_cmd=self.add_credit, parser=subparser)
        subparser.add_argument('username', help="User's username")
        subparser.add_argument('credit', type=int, help="Credit to add (positive or negative integer)")

    def add_credit(self, args):
        """Create a new user calling directly the local director."""
        self._check_director()
        cpsdirector.user.add_credit(args.username, args.credit)


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS users.', logger)

    _user_cmd = UserCmd(parser, cmd_client)

    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    cmd_client.set_config(args.director_url, args.username, args.password,
                          args.debug)
    try:
        args.run_cmd(args)
    except Exception:
        if args.debug:
            traceback.print_exc()
        else:
            ex = sys.exc_info()[1]
            if str(ex).startswith("ERROR"):
                sys.stderr.write("%s\n" % ex)
            else:
                sys.stderr.write("ERROR: %s\n" % ex)
        sys.exit(1)


if __name__ == '__main__':
    main()

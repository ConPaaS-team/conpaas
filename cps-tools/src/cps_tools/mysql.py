
import traceback
import argcomplete
import getpass
import logging
import sys

from .base import BaseClient
from .config import config
from .service import ServiceCmd


class MySQLCmd(ServiceCmd):

    def __init__(self, mysql_parser, client):
        ServiceCmd.__init__(self, mysql_parser, client, "mysql",
                            [('mysql', 1), ('glb', 0)], # (role name, default number)
                            "MySQL service sub-commands help")
        self._add_change_pwd()
        # self._add_migrate_nodes()
        self._add_dump()
        self._add_load_dump()
        self._add_help(mysql_parser) # defined in base class (ServiceCmd)

    # ========== change_password
    def _add_change_pwd(self):
        subparser = self.add_parser('set_password',
                                    help="change the password of the MySQL database")
        subparser.set_defaults(run_cmd=self.change_pwd, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('-p', '--password', metavar='PASS',
                               default=None, help="New password (interactively queried if not specified)")

    def change_pwd(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        if args.password:
            pwd1 = args.password
        else:
            pprompt = lambda: (getpass.getpass(),
                               getpass.getpass('Retype password: '))
            pwd1, pwd2 = pprompt()
            while pwd1 != pwd2:
                print('Passwords do not match. Try again')
                pwd1, pwd2 = pprompt()

        user = 'mysqldb'
        data = { 'user': user, 'password': pwd1 }
        self.client.call_manager_post(app_id, service_id, "set_password", data)

        print("MySQL password successfully updated for user '%s'." % user)

    # ========== migrate_nodes
    def _add_migrate_nodes(self):
        subparser = self.add_parser('migrate_nodes', help="migrate nodes in MySQL service")
        subparser.set_defaults(run_cmd=self.migrate_nodes, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('nodes', metavar='c1:n:c2[,c1:n:c2]*',
                               help="Nodes to migrate: node n from cloud c1 to cloud c2")
        subparser.add_argument('-d', '--delay', metavar='SECONDS', type=int, default=0,
                               help="Delay in seconds before removing the original nodes")

    def migrate_nodes(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        if args.delay < 0:
            raise Exception("Cannot delay %s seconds." % args.delay)

        try:
            migr_all = args.nodes.split(',')
            nodes = []
            for migr in migr_all:
                from_cloud, vmid, to_cloud = migr.split(':')
                migr_dict = {'from_cloud': from_cloud,
                             'vmid': vmid,
                             'to_cloud': to_cloud}
                nodes.append(migr_dict)
        except:
            raise Exception('Argument "nodes" does not match format c1:n:c2[,c1:n:c2]*: %s' % args.nodes)

        data = {'nodes': nodes, 'delay': args.delay}
        self.client.call_manager_post(app_id, service_id, "migrate_nodes", data)

        if args.delay == 0:
            print("Migration of nodes %s has been successfully started"
                  " for MySQL service %s." % (args.nodes, service_id))
        else:
            print("Migration of nodes %s has been successfully started"
                  " for MySQL service %s with a delay of %s seconds."
                  % (args.nodes, service_id, args.delay))

    # ========== dump
    def _add_dump(self):
        subparser = self.add_parser('dump', help="dump the MySQL database")
        subparser.set_defaults(run_cmd=self.dump, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def dump(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "sqldump")

        print res

    # ========== load_dump
    def _add_load_dump(self):
        subparser = self.add_parser('load_dump', help="load a dump to the MySQL database")
        subparser.set_defaults(run_cmd=self.load_dump, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="Name of file that contains the dump")

    def load_dump(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        with open(args.filename) as dump_file:
            contents = dump_file.read()
        params = { 'service_id': service_id,
                   'method': "load_dump" }
        files = [('mysqldump_file', args.filename, contents)]

        self.client.call_manager_post(app_id, service_id, "/", params, files)

        print "MySQL dump '%s' loaded successfully." % args.filename

def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS MySQL services.', logger)

    _serv_cmd = MySQLCmd(parser, cmd_client)

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

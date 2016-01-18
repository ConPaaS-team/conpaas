import argcomplete
import getpass
import logging
import sys

from .base import BaseClient
from .config import config
from .service import ServiceCmd


class MySQLCmd(ServiceCmd):

    def __init__(self, mysql_parser, client):
        ServiceCmd.__init__(self, mysql_parser, client, "mysql", ['nodes', 'glb_nodes'],
                            "MySQL service sub-commands help")
        self._add_change_pwd()
        self._add_migrate_nodes()
        self._add_dump()
        self._add_load_dump()

    # ========== change_password
    def _add_change_pwd(self):
        subparser = self.add_parser('set_password',
                                    help="change the password of the MySQL database")
        subparser.set_defaults(run_cmd=self.change_pwd, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('--password', metavar='new_password',
                               default=None, help="New password (interactively queried if not specified)")

    def change_pwd(self, args):
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)

        if args.password:
            pwd1 = args.password
        else:
            pprompt = lambda: (getpass.getpass(),
                               getpass.getpass('Retype password: '))
            pwd1, pwd2 = pprompt()
            while pwd1 != pwd2:
                print('Passwords do not match. Try again')
                pwd1, pwd2 = pprompt()

        data = {'user': 'mysqldb', 'password': pwd1}
        res = self.client.call_manager(app_id, service_id, "set_password", True, data)
        if 'error' in res:
            self.client.error("Could not update MySQL password for service %d: %s"
                              % (service_id, res['error']))
        else:
            print("MySQL password updated successfully.")

    
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
        subparser.add_argument('--delay', '-d', metavar='SECONDS', type=int, default=0,
                               help="Delay in seconds before removing the original nodes")

    def migrate_nodes(self, args):
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        if args.delay < 0:
            self.client.error("Cannot delay %s seconds." % args.delay)
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
            self.client.error('Argument "nodes" does not match format c1:n:c2[,c1:n:c2]*: %s' % args.nodes)

        data = {'nodes': nodes, 'delay': args.delay}
        res = self.client.call_manager_post(app_id, service_id, "migrate_nodes", data)
        if 'error' in res:
            self.client.error("Could not migrate nodes in MySQL service %s: %s"
                              % (service_id, res['error']))
        else:
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
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        res = self.client.call_manager_get(app_id, service_id, "sqldump")
        if type('error') is dict and 'error' in res:
            self.client.error("Could not dump MySQL database: %s." % res['error'])
        else:
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
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        with open(args.filename) as dump_file:
            contents = dump_file.read()
        params = { 'service_id': service_id,
                   'method': "load_dump" }
        files = [('mysqldump_file', args.filename, contents)]
        res = self.client.call_manager_post(app_id, service_id, "/", params, files)
        if 'error' in res:
            self.client.error(res['error'])


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS PHP services.', logger)

    _serv_cmd = MySqlCmd(parser, cmd_client)

    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    cmd_client.set_config(args.director_url, args.username, args.password,
                          args.debug)
    try:
        args.run_cmd(args)
    except:
        e = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s\n" % e)
        sys.exit(1)

if __name__ == '__main__':
    main()

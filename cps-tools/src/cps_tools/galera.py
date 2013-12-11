
import getpass

from .service import ServiceCmd


class GaleraCmd(ServiceCmd):

    def __init__(self, mysql_parser, client):
        ServiceCmd.__init__(self, mysql_parser, client, "galera", ['nodes', 'glb_nodes'],
                            "MySQL Galera service sub-commands help")
        self._add_change_pwd()
        self._add_migrate_nodes()
        self._add_dump()
        self._add_load_dump()

    # ========== change_password
    def _add_change_pwd(self):
        subparser = self.add_parser('set_password',
                                    help="change the password of the MySQL Galera database")
        subparser.set_defaults(run_cmd=self.change_pwd, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('--password', metavar='new_password',
                               default=None, help="New password (interactively queried if not specified)")

    def change_pwd(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
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
        res = self.client.call_manager(service_id, "set_password", True, data)
        if 'error' in res:
            self.client.error("Could not update MySQL Galera password for service %d: %s"
                              % (service_id, res['error']))
        else:
            print("MySQL Galera password updated successfully.")

    # ========== migrate_nodes
    def _add_migrate_nodes(self):
        subparser = self.add_parser('migrate_nodes', help="migrate nodes in Galera service")
        subparser.set_defaults(run_cmd=self.migrate_nodes, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('nodes', metavar='c1:n:c2[,c1:n:c2]*',
                               help="Nodes to migrate: node n from cloud c1 to cloud c2")
        subparser.add_argument('--delay', '-d', metavar='SECONDS', type=int, default=0,
                               help="Delay in seconds before removing the original nodes")

    def migrate_nodes(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
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
        res = self.client.call_manager_post(service_id, "migrate_nodes", data)
        if 'error' in res:
            self.client.error("Could not migrate nodes in MySQL Galera service %s: %s"
                              % (service_id, res['error']))
        else:
            if args.delay == 0:
                print("Migration of nodes %s has been successfully started"
                      " for MySQL Galera service %s." % (args.nodes, service_id))
            else:
                print("Migration of nodes %s has been successfully started"
                      " for MySQL Galera service %s with a delay of %s seconds."
                      % (args.nodes, service_id, args.delay))

    # ========== dump
    def _add_dump(self):
        subparser = self.add_parser('dump', help="dump the MySQL database")
        subparser.set_defaults(run_cmd=self.dump, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def dump(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        res = self.client.call_manager_get(service_id, "sqldump")
        if type('error') is dict and 'error' in res:
            self.client.error("Could not dump MySQL database: %s." % res['error'])
        else:
            print res

    # ========== load_dump
    def _add_load_dump(self):
        subparser = self.add_parser('load_dump', help="load a dump to the MySQL database")
        subparser.set_defaults(run_cmd=self.load_dump, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="Name of file that contains the dump")

    def load_dump(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        with open(args.filename) as dump_file:
            contents = dump_file.read()
        files = [('mysqldump_file', args.filename, contents)]
        res = self.client.call_manager_post(service_id, "/", {'method': "load_dump", }, files)
        if 'error' in res:
            print res['error']

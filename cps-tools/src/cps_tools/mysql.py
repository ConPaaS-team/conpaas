
import getpass

from .service import ServiceCmd


class MySQLCmd(ServiceCmd):

    def __init__(self, mysql_parser, client):
        ServiceCmd.__init__(self, mysql_parser, client, "mysql", ['slaves'],
                            "MySQL service sub-commands help")
        self._add_change_pwd()
        self._add_dump()

    # ========== change_password
    def _add_change_pwd(self):
        subparser = self.add_parser('change_password',
                                    help="change the password of the MySQL database")
        subparser.set_defaults(run_cmd=self.change_pwd, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('--password', metavar='new_password',
                               default=None, help="New password")

    def change_pwd(self, args):
        service_id = self.client.get_service_id(args.serv_name_or_id)
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
            self.client.error("Could not update MySQL password for service %d: %s"
                              % (service_id, res['error']))
        else:
            print("MySQL password updated successfully.")

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

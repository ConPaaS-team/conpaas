
import argcomplete
import logging
import sys

from .base import BaseClient
from .config import config


def check_appl_name(client, appl_name_or_id):
    """
    Check if a given application name is a valid name or a valid
    application identifier.

    :return  a pair (application_identifier, application_name) if correct,
             raise an exception otherwise.
    """

    apps = client.call_director_get("listapp")
    app_ids = [appl['aid'] for appl in apps]

    if not apps:
        raise Exception('No existing applications')

    if appl_name_or_id is None:
        return (None, None)

    try:
        appl_id = int(appl_name_or_id)
    except ValueError:
        app_ids = [appl['aid'] for appl in apps if appl['name'] == appl_name_or_id]
        if len(app_ids) == 0:
            client.error('Unknown application \'%s\'' % appl_name_or_id)
        elif len(app_ids) > 1:
            raise Exception('%s applications match the application name \'%s\''
                            % (len(app_ids), appl_name_or_id))
        else:
            appl_id = app_ids[0]

    if not appl_id in app_ids:
        raise Exception('Unknown application identifier \'%s\'' % appl_id)

    appl_name = [appl['name'] for appl in apps if appl['aid'] == appl_id][0]

    return appl_id, appl_name


class ApplicationCmd:

    def __init__(self, parser, client):
        self.client = client

        self.subparsers = parser.add_subparsers(help=None, title=None,
                                                description=None,
                                                metavar="<sub-command>")
        self._add_list()
        self._add_create()
        self._add_start()
        self._add_get_log()
        self._add_get_info()
        self._add_rename()
        self._add_stop()
        self._add_delete()
        

        self._add_help(parser)

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)

    # ========== help
    def _add_help(self, parser):
        subparser = self.add_parser('help', help="show help")
        subparser.set_defaults(run_cmd=self.help, parser=parser)

    def help(self, args):
        args.parser.print_help()

    # ========== create
    def _add_create(self):
        subparser = self.add_parser('create', help="create a new application")
        subparser.set_defaults(run_cmd=self.create_appl, parser=subparser)
        subparser.add_argument('appl_name',
                               help="Name of the new application")

    def create_appl(self, args):
        if self.client.call_director_post("createapp",
                                          {'name': args.appl_name}):
            print("Application \'%s\' created." % args.appl_name)
        else:
            self.client.error("Failed to create application \'%s\'."
                              % args.appl_name)

    # ========== list
    def _add_list(self):
        subparser = self.add_parser('list', help="list applications")
        subparser.set_defaults(run_cmd=self.list_appl, parser=subparser)

    def list_appl(self, _args):
        apps = self.client.call_director_get("listapp")
        
        if apps:
            print(self.client.prettytable(('aid', 'name', 'manager'), apps))
        else:
            print "No existing applications"

    # ========== rename
    def _add_rename(self):
        subparser = self.add_parser('rename', help="rename an application")
        subparser.set_defaults(run_cmd=self.rename_appl, parser=subparser)
        subparser.add_argument('appl_name_or_id',
                               help="Name or identifier of the application to rename")
        subparser.add_argument('new_name', help="New name for the application")

    def rename_appl(self, args):
        try:
            app_id, app_name = check_appl_name(self.client, args.appl_name_or_id)
        except:
            ex = sys.exc_info()[1]
            self.client.error("%s" % ex)

        res = self.client.call_director_post("renameapp/%d" % app_id,
                                             {'name': args.new_name})
        if res:
            print("Application with id %d has been renamed from '\%s\' to \'%s\'."
                  % (app_id, app_name, args.new_name))
        else:
            self.client.error("Failed to rename application \'%s\' (id %s)."
                              % (app_name, app_id))

    # ========== delete
    def _add_delete(self):
        subparser = self.add_parser('delete', help="delete an application")
        subparser.set_defaults(run_cmd=self.delete_appl, parser=subparser)
        subparser.add_argument('appl_name_or_id',
                               help="Name or identifier of the application to delete")

    def delete_appl(self, args):
        try:
            app_id, app_name = check_appl_name(self.client, args.appl_name_or_id)
        except:
            ex = sys.exc_info()[1]
            self.client.error("%s" % ex)

        res = self.client.call_director_post("deleteapp/%d" % app_id)
        if res:
            print("Application \'%s\' with id %s has been deleted." % (app_name, app_id))
        else:
            self.client.error('Failed to delete application \'%s\' (id %s).'
                              % (app_name, app_id))

    # ========== start
    def _add_start(self):
        subparser = self.add_parser('start', help="start an application")
        subparser.set_defaults(run_cmd=self.start_appl, parser=subparser)
        subparser.add_argument('appl_id',
                               help="Identifier of the application to start")

    def start_appl(self, args):
        try:
            app_id, app_name = check_appl_name(self.client, args.appl_id)
        except:
            ex = sys.exc_info()[1]
            self.client.error("%s" % ex)

        res = self.client.call_director_post("startapp/%d" % app_id)
        if res:
            print("Application \'%s\' with id %s has started." % (app_name, app_id))
        else:
            self.client.error('Failed to start application \'%s\' (id %s).'
                              % (app_name, app_id))

    # ========== stop
    def _add_stop(self):
        subparser = self.add_parser('stop', help="stop an application")
        subparser.set_defaults(run_cmd=self.stop_appl, parser=subparser)
        subparser.add_argument('appl_id',
                               help="Identifier of the application to start")

    def stop_appl(self, args):
        try:
            app_id, app_name = check_appl_name(self.client, args.appl_id)
        except:
            ex = sys.exc_info()[1]
            self.client.error("%s" % ex)

        res = self.client.call_director_post("stopapp/%d" % app_id)
        if res:
            print("Application \'%s\' with id %s was stopped." % (app_name, app_id))
        else:
            self.client.error('Failed to stop application \'%s\' (id %s).'
                              % (app_name, app_id))

    # ========== get_log
    def _add_get_log(self):
        subparser = self.add_parser('get_log', help="get application log")
        subparser.set_defaults(run_cmd=self.get_log, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        
    def get_log(self, args):
        try:
            app_id, app_name = check_appl_name(self.client, args.app_name_or_id)
        except:
            ex = sys.exc_info()[1]
            self.client.error("%s" % ex)

        res = self.client.call_manager_get(app_id, 0, "getLog")
        if res:
            print("%s" % res['log'])
        else:
            self.client.error("Failed to get logs for application %s: %s" % (app_id, res['error']))

    # ========== get_info
    def _add_get_info(self):
        subparser = self.add_parser('get_info', help="get information about the application")
        subparser.set_defaults(run_cmd=self.get_info, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        
    def get_info(self, args):
        try:
            app_id, app_name = check_appl_name(self.client, args.app_name_or_id)
        except:
            ex = sys.exc_info()[1]
            self.client.error("%s" % ex)

        res = self.client.call_manager_get(app_id, 0, "infoapp")
        if res:
            # print("%s" % res['log'])
            print res
        else:
            self.client.error("Failed to get info for application %s: %s" % (app_id, res['error']))

def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS applications.', logger)

    _appl_cmd = ApplicationCmd(parser, cmd_client)

    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    cmd_client.set_config(args.director_url, args.username, args.password,
                          args.debug)
    try:
        args.run_cmd(args)
    except:
        ex = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s\n" % ex)
        sys.exit(1)

if __name__ == '__main__':
    main()

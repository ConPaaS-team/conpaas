
import argcomplete
import logging, simplejson
import sys, os.path

from .base import BaseClient
from .config import config
from .cloud import check_cloud


def check_application(client, appl_name_or_id):
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
            raise Exception("Unknown application name '%s'" % appl_name_or_id)
        elif len(app_ids) > 1:
            raise Exception("%s applications match the application name '%s'"
                            % (len(app_ids), appl_name_or_id))
        else:
            appl_id = app_ids[0]

    if not appl_id in app_ids:
        raise Exception("Unknown application id %s" % appl_id)

    appl_name = [appl['name'] for appl in apps if appl['aid'] == appl_id][0]

    return appl_id, appl_name


class ApplicationCmd:

    def __init__(self, parser, client):
        self.client = client

        self.subparsers = parser.add_subparsers(help=None, title=None,
                                                description=None,
                                                metavar="<sub-command>")
        self._add_create()
        self._add_delete()
        self._add_list()
        self._add_rename()
        self._add_start()
        self._add_stop()
        self._add_get_log()
        self._add_get_info()
        self._add_manifest()
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
        res = self.client.call_director_post("createapp",
                                            {'name': args.appl_name})

        print("Application '%s' created with id %s." % (res['name'], res['aid']))

    # ========== list
    def _add_list(self):
        subparser = self.add_parser('list', help="list applications")
        subparser.set_defaults(run_cmd=self.list_appl, parser=subparser)

    def list_appl(self, _args):
        apps = self.client.call_director_get("listapp")

        for app in apps:
            if app['cloud'] == 'iaas':
                app['cloud'] = 'default'

        if apps:
            print(self.client.prettytable(('aid', 'name', 'manager', 'cloud', 'status'), apps))
        else:
            print "No existing applications"

    # ========== rename
    def _add_rename(self):
        subparser = self.add_parser('rename', help="rename an application")
        subparser.set_defaults(run_cmd=self.rename_appl, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of the application to rename")
        subparser.add_argument('new_name', help="New name for the application")

    def rename_appl(self, args):
        app_id, app_name = check_application(self.client, args.app_name_or_id)

        self.client.call_director_post("renameapp/%d" % app_id,
                                             {'name': args.new_name})

        print("Application with id %d has been renamed from '%s' to '%s'."
              % (app_id, app_name, args.new_name))

    # ========== delete
    def _add_delete(self):
        subparser = self.add_parser('delete', help="delete an application")
        subparser.set_defaults(run_cmd=self.delete_appl, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of the application to delete")

    def delete_appl(self, args):
        app_id, app_name = check_application(self.client, args.app_name_or_id)

        self.client.call_director_post("deleteapp/%d" % app_id)

        print("Application '%s' with id %s has been deleted." % (app_name, app_id))

    # ========== start
    def _add_start(self):
        subparser = self.add_parser('start', help="start an application")
        subparser.set_defaults(run_cmd=self.start_appl, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('-c', '--cloud', metavar='NAME', default=None,
                               help="Cloud where the application manager will be created")

    def start_appl(self, args):
        app_id, app_name = check_application(self.client, args.app_name_or_id)

        if args.cloud is None:
            self.client.call_director_post("startapp/%d" % app_id)
        else:
            check_cloud(self.client, args.cloud)
            self.client.call_director_post("startapp/%d/%s" % (app_id, args.cloud))

        print "Application '%s' with id %s is starting... " % (app_name, app_id),
        sys.stdout.flush()

        state = self.client.wait_for_app_state(app_id, ['RUNNING', 'ERROR'])
        if state == 'RUNNING':
            print "done."
        else:
            print "FAILED!"

    # ========== stop
    def _add_stop(self):
        subparser = self.add_parser('stop', help="stop an application")
        subparser.set_defaults(run_cmd=self.stop_appl, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")

    def stop_appl(self, args):
        app_id, app_name = check_application(self.client, args.app_name_or_id)

        self.client.call_director_post("stopapp/%d" % app_id)

        print("Application '%s' with id %s was stopped." % (app_name, app_id))

    # ========== manifest
    def _add_manifest(self):
        subparser = self.add_parser('manifest', help="upload a manifest")
        subparser.set_defaults(run_cmd=self.manifest, parser=subparser)
        subparser.add_argument('man_path',
                               help="The manifest file")

    def manifest(self, args):
        man = args.man_path
        json = self.check_manifest(man)

        self.client.call_director_post("upload_manifest",
                { 'manifest': json, 'thread': True })

        print "The application is being created based on the specified manifest."

    def check_manifest(self, json):
        if not os.path.isfile(json):
            raise Exception('The specified path does not contain a file')

        try:
            json = open(json, 'r').read()
            parse = simplejson.loads(json)
        except:
            raise Exception('The uploaded manifest is not valid json')

        for service in parse.get('Services'):
            if not service.get('Type'):
                raise Exception('The "Type" field is mandatory')

        return json

    # ========== get_log
    def _add_get_log(self):
        subparser = self.add_parser('get_log', help="get the application manager's log file")
        subparser.set_defaults(run_cmd=self.get_log, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")

    def get_log(self, args):
        app_id, app_name = check_application(self.client, args.app_name_or_id)

        res = self.client.call_manager_get(app_id, 0, "get_manager_log")

        print("%s" % res['log'])

    # ========== get_info
    def _add_get_info(self):
        subparser = self.add_parser('get_info', help="get information about the application")
        subparser.set_defaults(run_cmd=self.get_info, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")

    def get_info(self, args):
        app_id, app_name = check_application(self.client, args.app_name_or_id)

        res = self.client.call_manager_get(app_id, 0, "get_app_info")

        print "Application name: %s" % app_name
        print "Application id: %s" % app_id

        print "Manager states:"
        print "\tApplication manager: %s" % res['states']['0']
        for sid in res['states']:
            if sid != '0':
                print "\tService manager %s: %s" % (sid, res['states'][sid])

        print "Nodes:"
        for node in res['nodes']:
            print "\t%s" % node

        print "Volumes:"
        for vol in res['volumes']:
            print "\t%s" % vol

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


import traceback
import argcomplete
import logging
import sys
import time

from .base import BaseClient
from .config import config
from .application import check_application
from .cloud import check_cloud


class ServiceCmd(object):

    def __init__(self, serv_parser, client, service_type=None, roles=None,
                 cmd_help="service sub-commands help"):
        self.client = client
        self.services = None  # cache for service list
        self.type = service_type
        if roles is None:
            self.roles = [('count', 1)] # (role name, default number)
        else:
            self.roles = roles
        self.initial_expected_state = 'INIT'

        self.subparsers = serv_parser.add_subparsers(help=None, title=None,
                                                     description=None,
                                                     metavar="<sub-command>")
        if service_type is not None:
            serv_parser.set_defaults(service_type=service_type)
        if not self.type:
            self._add_get_types()
        self._add_add()
        self._add_remove()
        self._add_list()
        self._add_rename()
        self._add_start()
        self._add_stop()
#        self._add_get_config()
        self._add_get_state()
        self._add_get_script()
        self._add_set_script()
        self._add_get_log()
        self._add_get_agent_log()
        self._add_get_history()
        self._add_add_nodes()
        self._add_remove_nodes()
        self._add_list_nodes()
        if not self.type:
            self._add_help(serv_parser)

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)

    def check_service(self, app_name_or_id, service_name_or_id):
        """
        Check if a given service name is a valid name or a valid
        service identifier.

        :return  a pair (application_identifier, service_identifier) if correct,
                 raise an exception otherwise.
        """

        app_id, _app_name = check_application(self.client, app_name_or_id)
        services = self.client.get_services(app_id, self.type)

        try:
            # string may be a service identifier
            service_id = int(service_name_or_id)
        except ValueError:
            # then, string may be a service name
            service_names = [service for service in services
                             if service['service']['name'] == service_name_or_id]
            if service_names == []:
                err_msg = "Unknown service name '%s' in application %s"\
                        % (service_name_or_id, app_id)
                if self.type is not None:
                    err_msg = err_msg + (" of type %s." % self.type)
                raise Exception(err_msg)
            else:
                service_id = service_names[0]['service']['sid']
        else:
            service_ids = [service for service in services
                           if service['service']['sid'] == service_id]
            if service_ids == []:
                err_msg = "Unknown service id %s in application %s"\
                        % (service_id, app_id)
                if self.type is not None:
                    err_msg = err_msg + (" of type %s." % self.type)
                raise Exception(err_msg)
        return app_id, service_id

    # ========== help
    def _add_help(self, serv_parser):
        help_parser = self.add_parser('help', help="show help")
        help_parser.set_defaults(run_cmd=self.user_help, parser=serv_parser)

    def user_help(self, args):
        args.parser.print_help()

    # ========== add
    def _add_add(self):
        subparser = self.add_parser('add', help="add a new service")
        subparser.set_defaults(run_cmd=self.add_serv, parser=subparser)
        if self.type is None:
            subparser.add_argument('service_type',
                                   help="Type of the new service")
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")

    def add_serv(self, args):
        app_id, _app_name = check_application(self.client, args.app_name_or_id)

        data = {}
        if app_id is not None:
            data['appid'] = app_id
        if self.type is not None:
            stype = self.type
        else:
            stype = args.service_type

        res = self.client.call_director_post("add/" + stype, data)

        print "Service %s successfully added to application %s with id %s."\
              % (stype, app_id, res['service']['sid'])

    # ========== list
    def _add_list(self):
        subparser = self.add_parser('list', help="list services")
        subparser.set_defaults(run_cmd=self.list_serv, parser=subparser)
        subparser.add_argument('-a', '--application', metavar='ID_OR_NAME',
                               default=None, help="Name or identifier of an application")

    def list_serv(self, args):
        if args.application is not None:
            app_id, _app_name = check_application(self.client, args.application)
        else:
            app_id = None

        services = self.client.get_services(app_id, self.type)

        # update service states with information from the application manager(s)
        service_states = {}
        app_ids = set(map(lambda s: s['service']['application_id'], services))
        for aid in app_ids:
            service_states[aid] = {}
            try:
                appinfo = self.client.call_manager_get(aid, 0, "get_app_info")
                for sid in appinfo['states']:
                    service_states[aid][int(sid)] = appinfo['states'][sid]
            except:
                pass # do not stop if a call to the app manager fails

        sorted_serv = []
        for row in services:
            aid = row['service']['application_id']
            sid = row['service']['sid']

            row['service']['aid'] = aid
            row['service']['status'] = service_states[aid].get(sid, 'N/A')
            sorted_serv.append(row['service'])

        # secondary sort per service id
        sorted_serv = sorted(sorted_serv, key=lambda k: k['sid'])
        # primary sort per application
        sorted_serv = sorted(sorted_serv, key=lambda k: k['aid'])

        table = self.client.prettytable(('aid', 'sid', 'type', 'name', 'status'),
                                        sorted_serv)
        if table:
            print "%s" % table
        else:
            print "No existing services."

    # ========== start
    def _add_start(self):
        subparser = self.add_parser('start', help="start a service")
        subparser.set_defaults(run_cmd=self.start_serv, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('-c', '--cloud', metavar='NAME', default='default',
                               help="Cloud where the service will be started")

    def start_serv(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
        check_cloud(self.client, args.cloud)

        data = { 'cloud': args.cloud, 'service_id': service_id }

        self.client.call_manager_post(app_id, 0, "start_service", data)

        print "Service %s of application %s is starting... " % (service_id, app_id),
        sys.stdout.flush()

        state = self.client.wait_for_service_state(app_id, service_id, ['RUNNING', 'ERROR'])
        if state == 'RUNNING':
            print "done."
        else:
            print "FAILED!"

    # ========== stop
    def _add_stop(self):
        subparser = self.add_parser('stop', help="stop a service")
        subparser.set_defaults(run_cmd=self.stop_serv, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def stop_serv(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        data = { 'service_id': service_id }
        self.client.call_manager_post(app_id, 0, "stop_service", data)

        print "Service %s of application %s is stopping... " % (service_id, app_id),
        sys.stdout.flush()

        state = self.client.wait_for_service_state(app_id, service_id, ['STOPPED', 'ERROR'])
        if state == 'STOPPED':
            print "done."
        else:
            print "FAILED!"

#    # ========== get_config
#    def _add_get_config(self):
#        subparser = self.add_parser('get_config', help='get configuration of a service')
#        subparser.set_defaults(run_cmd=self.get_config, parser=subparser)
#        subparser.add_argument('app_name_or_id',
#                               help="Name or identifier of an application")
#        subparser.add_argument('serv_name_or_id',
#                               help="Name or identifier of a service")
#
#    def get_config(self, args):
#        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
#        res = self.client.service_dict(app_id, service_id)
#        service = res['service']
#        print "Director info:"
#        for key, value in service.items():
#            print "%s: %s" % (key, value)

    # ========== get_state
    def _add_get_state(self):
        subparser = self.add_parser('get_state', help="display a service's state")
        subparser.set_defaults(run_cmd=self.get_state, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_state(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "get_service_info")

        for key, value in res.items():
            print "%s: %s" % (key, value)

    # ========== get_log
    def _add_get_log(self):
        subparser = self.add_parser('get_log', help="get the service manager's log file")
        subparser.set_defaults(run_cmd=self.get_log, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_log(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "get_manager_log")

        print("%s" % res['log'])

    # ========== get_history
    def _add_get_history(self):
        subparser = self.add_parser('get_history', help="display the service's history")
        subparser.set_defaults(run_cmd=self.get_history, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_history(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        res = self.client.call_manager_get(app_id, service_id, "get_service_history")

        for entry in res['state_log']:
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(entry['time'])))
            print "%s %s %s" % (time_str, entry['state'], entry['reason'])

    # ========== rename
    def _add_rename(self):
        subparser = self.add_parser('rename', help="rename a service")
        subparser.set_defaults(run_cmd=self.rename_serv, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('new_name',
                               help="New name for the service")

    def rename_serv(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        self.client.call_director_post("rename",
                { 'app_id': app_id,'service_id':service_id, 'name': args.new_name })

        print("Service %s of application %s has been renamed to '%s'."
              % (service_id, app_id, args.new_name))

    # ========== remove
    def _add_remove(self):
        subparser = self.add_parser('remove', help="remove a service")
        subparser.set_defaults(run_cmd=self.remove_serv, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def remove_serv(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        self.client.call_director_post("remove", {'app_id': app_id, 'service_id': service_id})

        print "Service %s of application %s has been successfully removed."\
              % (service_id, app_id)

    # ========== get_types
    def _add_get_types(self):
        subparser = self.add_parser('get_types',
                                    help="get available service types")
        subparser.set_defaults(run_cmd=self.get_types, parser=subparser)

    def get_types(self, args):
        if self.type:
            print "%s" % self.type
        else:
            res = self.client.call_director_get("available_services")

            for serv_type in res:
                print "%s" % serv_type

    # ========== list_nodes
    def _add_list_nodes(self):
        subparser = self.add_parser('list_nodes',
                                    help="list the nodes of a service")
        subparser.set_defaults(run_cmd=self.list_nodes, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_nodes(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        nodes = self.client.call_manager_get(app_id, service_id, "list_nodes")

        sorted_nodes = []
        for role, role_nodes in nodes.items():
            for node in role_nodes:
                try:
                    params = { 'serviceNodeId': node }
                    details = self.client.call_manager_get(app_id, service_id, "get_node_info", params)
                except Exception:
                    print "WARNING: got node identifier from list_nodes but failed on get_node_info",
                    if type(details) is dict and 'error' in details:
                        print ": %s" % details['error']
                    else:
                        print "."
                    row = {
                        'aid': app_id,
                        'sid': service_id,
                        'role': role,
                        'ip': 'N/A',
                        'cloud': 'N/A',
                        'agent_id': node
                    }
                else:
                    row = details['serviceNode']
                    row['aid'] = app_id
                    row['sid'] = service_id
                    row['role'] = role
                    row['agent_id'] = node
                    if row['cloud'] == 'iaas':
                        row['cloud'] = 'default'
                sorted_nodes.append(row)

        if sorted_nodes:
            # secondary sort per ip
            sorted_nodes = sorted(sorted_nodes, key=lambda k: k['ip'])
            # primary sort service id
            sorted_nodes = sorted(sorted_nodes, key=lambda k: k['sid'])

            print(self.client.prettytable(('aid', 'sid', 'role', 'ip', 'agent_id', 'cloud'), sorted_nodes))
        else:
            print "No existing nodes."

    def _get_roles_nb(self, args=None): # if args is None we use the defaults
        total_nodes = 0
        data = {}
        for role, count in self.roles:
            if args:
                node_nb = getattr(args, role)
                if node_nb < 0:
                    raise Exception("Invalid number of nodes %s." % node_nb)
            else:
                node_nb = count
            total_nodes += node_nb
            data[role] = node_nb
        return total_nodes, data

    # ========== add_nodes
    def _add_add_nodes(self):
        subparser = self.add_parser('add_nodes', help="add nodes to a service")
        subparser.set_defaults(run_cmd=self.add_nodes, parser=subparser)
        subparser.add_argument('app_name_or_id', help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id', help="Name or identifier of a service")
        for role, count in self.roles:
            name = 'nodes' if role == 'count' else role + ' nodes'
            subparser.add_argument('--%s' % role, metavar='COUNT', type=int, default=0,
                                   help="Number of %s to add (default %s)" % (name, count))
        subparser.add_argument('-c', '--cloud', metavar='CLOUD_NAME', default='default',
                               help="Name of the cloud where to add nodes")

    def add_nodes(self, args):
        total_nodes, nodes = self._get_roles_nb(args)
        if total_nodes == 0:
            if args.debug:
                self.client.logger.info("No node was specified, using the default number of nodes")
            total_nodes, nodes = self._get_roles_nb()

        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)
        check_cloud(self.client, args.cloud)

        data={}
        data['nodes'] = nodes
        data['service_id'] = service_id
        data['cloud'] = args.cloud
        self.client.call_manager_post(app_id, 0, "add_nodes", data)

        print "Starting %s new nodes for service %s of application %s... "\
              % (total_nodes, service_id, app_id),
        sys.stdout.flush()

        state = self.client.wait_for_service_state(app_id, service_id, ['RUNNING', 'ERROR'])
        if state == 'RUNNING':
            print "done."
        else:
            print "FAILED!"

    # ========== remove_nodes
    def _add_remove_nodes(self):
        subparser = self.add_parser('remove_nodes',
                                    help="remove nodes from a service")
        subparser.set_defaults(run_cmd=self.remove_nodes, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        for role, count in self.roles:
            name = 'nodes' if role == 'count' else role + ' nodes'
            subparser.add_argument('--%s' % role, metavar='COUNT', type=int, default=0,
                                   help="Number of %s to remove (default %s)"
                                        % (name, count))

    def remove_nodes(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        total_nodes, nodes = self._get_roles_nb(args)
        if total_nodes == 0:
            if args.debug:
                self.client.logger.info("No node was specified, using the default number of nodes")
            total_nodes, nodes = self._get_roles_nb()

        data = {
            'nodes': nodes,
            'service_id': service_id
        }
        self.client.call_manager_post(app_id, 0, "remove_nodes", data)

        print "Removing %s nodes for service %s of application %s... "\
              % (total_nodes, service_id, app_id),
        sys.stdout.flush()

        state = self.client.wait_for_service_state(app_id, service_id, ['RUNNING', 'STOPPED', 'ERROR'])
        if state in ['STOPPED', 'RUNNING']:
            print "done."
        else:
            print "FAILED!"

    # ========== create_volume
    def _add_create_volume(self):
        subparser = self.add_parser('create_volume', help="create a storage volume")
        subparser.set_defaults(run_cmd=self.create_volume, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('vol_name', help="Name of the storage volume")
        subparser.add_argument('vol_size', type=int, help="Size of the storage volume (MB)")
        subparser.add_argument('agent_id', help="Id of the agent to attach the volume to "
                                             "(use list_nodes to find it)")

    def create_volume(self, args):
        app_id, _app_name = check_application(self.client, args.app_name_or_id)

        data = {
            'volumeName': args.vol_name,
            'volumeSize': args.vol_size,
            'agentId': args.agent_id
        }
        res = self.client.call_manager_post(app_id, 0, "create_volume", data)

        print "Creating volume '%s' and attaching it to node '%s'... "\
                % (args.vol_name, args.agent_id),
        sys.stdout.flush()

        service_id = res['service_id']
        state = self.client.wait_for_service_state(app_id, service_id, ['RUNNING', 'ERROR'])
        if state == 'RUNNING':
            print "done."
        else:
            print "FAILED!"

    # ========== list_volume
    def _add_list_volumes(self):
        subparser = self.add_parser('list_volumes', help="list storage volumes")
        subparser.set_defaults(run_cmd=self.list_volumes, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def list_volumes(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        data = { 'service_id': service_id }
        res = self.client.call_manager_post(app_id, 0, "list_volumes", data)

        if res['volumes']:

            sorted_vols = []
            for row in res['volumes']:
                row['aid'] = app_id
                row['sid'] = row['service_id']
                row['agent_id'] = row['vm_id']
                if row['cloud'] == 'iaas':
                    row['cloud'] = 'default'
                sorted_vols.append(row)

            # secondary sort per volume name
            sorted_vols = sorted(sorted_vols, key=lambda k: k['vol_name'])
            # primary sort service id
            sorted_vols = sorted(sorted_vols, key=lambda k: k['sid'])

            print(self.client.prettytable(('aid', 'sid', 'vol_name', 'vol_size', 'agent_id', 'cloud'), sorted_vols))
        else:
            print "No existing storage volumes."

    # ========== delete_volume
    def _add_delete_volume(self):
        subparser = self.add_parser('delete_volume', help="delete a storage volume")
        subparser.set_defaults(run_cmd=self.delete_volume, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('vol_name', help="Name of the storage volume")

    def delete_volume(self, args):
        app_id, _app_name = check_application(self.client, args.app_name_or_id)

        data = { 'volumeName': args.vol_name }
        res = self.client.call_manager_post(app_id, 0, "delete_volume", data)

        print "Detaching volume '%s' and deleting it... " % args.vol_name,
        sys.stdout.flush()

        service_id = res['service_id']
        state = self.client.wait_for_service_state(app_id, service_id, ['RUNNING', 'ERROR'])
        if state == 'RUNNING':
            print "done."
        else:
            print "FAILED!"

    # ========== get_agent_log
    def _add_get_agent_log(self):
        subparser = self.add_parser('get_agent_log',
                                    help="get the service agent's log files")
        subparser.set_defaults(run_cmd=self.get_agent_log, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('agent_id',
                               help="Id of the agent (use list_nodes to find it)")
        subparser.add_argument('-f', '--filename', metavar='FILENAME',
                               default=None, help="log file name")

    def get_agent_log(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        params = { 'agentId': args.agent_id }
        if args.filename:
            params['filename'] = args.filename
        res = self.client.call_manager_get(app_id, 0, "get_agent_log", params)

        print res['log']

    # ========== get_script
    def _add_get_script(self):
        subparser = self.add_parser('get_script', help="get the service's startup script")
        subparser.set_defaults(run_cmd=self.get_script, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_script(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        data = { 'sid': service_id }
        res = self.client.call_manager_get(app_id, 0, "get_startup_script", data)

        print res

    # ========== set_script
    def _add_set_script(self):
        subparser = self.add_parser('set_script', help="set the service's startup script")
        subparser.set_defaults(run_cmd=self.set_script, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('filename',
                               help="File containing the script")

    def set_script(self, args):
        app_id, service_id = self.check_service(args.app_name_or_id, args.serv_name_or_id)

        data = {
            'sid': service_id,
            'method': 'upload_startup_script'
        }
        contents = open(args.filename).read()
        files = [ ( 'script', args.filename, contents ) ]

        self.client.call_manager_post(app_id, 0, "/", data, files)

        print "Startup script uploaded successfully."


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS services.', logger)

    _serv_cmd = ServiceCmd(parser, cmd_client)

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

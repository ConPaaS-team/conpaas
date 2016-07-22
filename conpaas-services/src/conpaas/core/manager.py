# -*- coding: utf-8 -*-

"""
    conpaas.core.manager
    ====================

    ConPaaS core: service-independent manager code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread
import StringIO, ConfigParser
import time, copy
import os.path
import os
import subprocess
import re
import logging
import json, httplib

from conpaas.core import git
from conpaas.core import https
from conpaas.core.log import create_logger, create_standalone_logger
from conpaas.core.expose import expose
from conpaas.core.callbacker import DirectorCallbacker
from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import FileUploadField
from conpaas.core.node import ServiceNode
from conpaas.core.https.server import ConpaasRequestHandlerComponent

from conpaas.core.misc import file_get_contents, file_write_contents
from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

from conpaas.core import ipop
from conpaas.core.ganglia import ManagerGanglia

from conpaas.core.services import manager_services

class BaseManager(ConpaasRequestHandlerComponent):

   # Manager states
    S_INIT     = 'INIT'     # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING  = 'RUNNING'  # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient state - frontend will
                            # keep polling until manager out of transient state
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED  = 'STOPPED'  # manager stopped
    S_ERROR    = 'ERROR'    # manager is in error state

    # Node types
    ROLE_DEFAULT = 'count'  # default node type used by cps-tools when the
                            # service type is not specified; will be replaced
                            # in check_node_roles() with the default role
                            # for the service
    ROLE_REGULAR = 'node'   # nondescript node role

    # String template for error messages returned when performing actions in
    # the wrong state
    WRONG_STATE_MSG = "ERROR: cannot perform %(action)s in state %(curstate)s"

    # String template for error messages returned when a required argument is
    # missing
    REQUIRED_ARG_MSG = "ERROR: %(arg)s is a required argument"

    # String template for debugging messages logged on nodes creation
    ACTION_REQUESTING_NODES = "requesting %(count)s nodes in %(action)s"

    AGENT_PORT = 5555

    def __init__(self, config_parser):
        ConpaasRequestHandlerComponent.__init__(self)

        logger_name = __name__
        self.logfile = config_parser.get('manager', 'LOG_FILE')
        if config_parser.has_option('manager', 'SERVICE_ID'):
            service_id = config_parser.get('manager', 'SERVICE_ID')
            logger_name = logger_name.replace('manager', 'manager%s' % service_id)
            self.logger = create_standalone_logger(logger_name, self.logfile)
        else:
            self.logger = create_logger(logger_name)

        self.config_parser = config_parser
        self.state_log = []
        self.state_set(self.S_INIT)

        self.volumes = {}
        self.nodes = []

    def state_get(self):
        return self.state

    def state_set(self, target_state, msg=''):
        self.state = target_state
        self.state_log.append({'time': time.time(),
                               'state': target_state,
                               'reason': msg})
        self.logger.debug('STATE %s: %s' % (target_state, msg))

    def check_state(self, expected_states):
        state = self.state_get()
        if state not in expected_states:
            raise Exception("Wrong service state: was expecting one of %s"\
                            " but current state is '%s'" \
                            % (expected_states, state))

    def check_node_roles(self, node_roles):
        if sum(node_roles.values()) == 0:
            raise Exception("Need a positive value for at least one role")

        valid_roles = self.get_node_roles()
        default_role = self.get_default_role()

        for role, count in node_roles.items():
            if count < 0:
                raise Exception("Invalid number of nodes %s" % count)

            if role in valid_roles:
                # we received a valid role, nothing to do
                pass
            elif role == self.ROLE_DEFAULT:
                # the role was not specified in cps-tools, let's replace
                # it with the default role for this service
                del node_roles[role]
                node_roles[default_role] = count
            else:
                # invalid role, raise an exception
                raise Exception("Wrong node type '%s' for service type '%s'."
                                % (role, self.get_service_type()))

    def check_credits(self):
        credit = self.callbacker.get_credit()
        if credit['credit'] <= 0:
            raise Exception('Insufficient credits')

    def _wait_state(self, expected_states, timeout=10 * 60):
        polling_interval = 10   # seconds
        while self.state_get() not in expected_states and timeout >= 0:
            self.logger.debug('Current state is %s, waiting for state to change to one of %s'
                              % (self.state_get(), expected_states))
            time.sleep(polling_interval)
            timeout -= polling_interval
        if timeout < 0:
            raise Exception("Timeout after %s seconds with a polling interval of %s seconds"
                            " while waiting for manager state to become one of %s."
                            % (timeout, polling_interval, expected_states))

    def get_service_type(self):
        """Returns the service name (type).

        It should be overwritten by all the service managers.
        """
        return "<unnamed service>"

    def get_node_roles(self):
        """Returns a list of node roles used by the service manager.

        It should be overwritten by the service managers if using more
        than one role.
        """
        return [ self.ROLE_REGULAR ]

    def get_default_role(self):
        """Returns the default role for this service.

        The default role is used when starting the service or adding /
        removing nodes to / from the service when no other role is
        specified (for example when using the non-specific 'cps-tools
        service' command instead of 'cps-tools php/java/mysql/etc.'.

        It should be overwritten by the service managers if using more
        than one role.
        """
        return self.ROLE_REGULAR

    def get_starting_nodes(self):
        """Specifies the roles and number of nodes from each role that
        should be started when the service is started.

        Returns a dict with roles as keys and the number of nodes from
        each role as values.

        It should be overwritten by the service managers if starting with
        a role different from the default one or with more than one node.
        """
        return { self.get_default_role(): 1 }

    def get_standard_sninfo(self, role, cloud):
        return { 'role': role, 'cloud': cloud }

    def get_standard_sninfo_with_volume(self, role, cloud, vol_name, vol_size):
        device_name = self.config_parser.get('manager', 'DEV_TARGET')
        volume = { 'vol_name': vol_name,
                   'vol_size': vol_size,
                   'dev_name': device_name }
        node_info = self.get_standard_sninfo(role, cloud)
        node_info['volumes'] = [ volume ]
        return node_info

    def get_role_sninfo(self, role, cloud):
        """Returns a dict containing the node information that will be
        provided to the cloud controller when starting nodes of the specified
        type (role). This will be the basis for the creation of a ServiceNode
        (hence the name sninfo - ServiceNode info).

        It should be overwritten by the service managers if roles use
        storage volumes, other special configurations or support running
        only on a specific cloud.

        To get a basic configuration that can be customized, the following
        standard methods can be used:
            self.get_standard_sninfo(role, cloud)
            self.get_standard_sninfo_with_volume(role, cloud, vol_name, vol_size)
        """
        return self.get_standard_sninfo(role, cloud)

    def get_sninfo(self, node_roles, cloud):
        sninfo = []
        for role, count in node_roles.iteritems():
            for _ in range(count):
                sninfo.append(self.get_role_sninfo(role, cloud))
        return sninfo

    def get_role_logs(self, role):
        """Returns a list containing the logs that are be exposed by an agent
        of the specified type (role). Each log is represented by a dict
        containing the name of the log file, the description and the file
        path inside the agent.

        It should be overwritten by the service managers if specific roles
        need to expose additional log files.
        """
        return [ {'filename': 'cpsagent.log',
                  'description': 'agent log',
                  'path': '/var/log/cpsagent.log'} ]

    def get_context_replacement(self):
        """Returns a dict used to fill in the values of variables in the
        VM contextualization script.

        It should be overwritten by the service managers if applicable.
        """
        return {}

    # return true if successful
    def on_start(self, nodes):
        raise Exception("start method not implemented for this service")

    def on_stop(self):
        raise Exception("stop method not implemented for this service")

    def check_add_nodes(self, node_roles):
        pass

    def on_add_nodes(self, nodes):
        raise Exception("add_nodes method not implemented for this service")

    def check_remove_nodes(self, node_roles):
        count = sum(node_roles.values())
        if count >= len(self.nodes):
            raise WrongNrNodesException(count, len(self.nodes) - 1)

    def on_remove_nodes(self, node_roles):
        raise Exception("remove_nodes method not implemented for this service")

    def check_create_volume(self, volume_name, volume_size, agent_id):
        raise Exception("create_volume method not currently supported for this service")

    def on_create_volume(self, node, volume):
        pass

    def check_delete_volume(self, node, volume):
        raise Exception("delete_volume method not currently supported for this service")

    def on_delete_volume(self, node, volume):
        pass

    def on_git_push(self):
        pass

    @expose('GET')
    def get_service_history(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'state_log': self.state_log})

    @expose('GET')
    def get_manager_log(self, kwargs):
        """Return logfile"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        try:
            return HttpJsonResponse({'log': file_get_contents(self.logfile)})
        except:
            return HttpErrorResponse('Failed to read log')

    @expose('GET')
    def get_agent_log(self, kwargs):
        """Return logfile"""
        node_ids = [ str(node.id) for node in self.nodes ]
        exp_params = [('agentId', is_in_list(node_ids)),
                      ('filename', is_string, None)]
        try:
            agent_id, filename = check_arguments(exp_params, kwargs)

            # Get the node that has the specified agent_id
            node = [ node for node in self.nodes if node.id == agent_id ][0]

            # If a filename was specified...
            if filename:
                # Get the logs for the node's role
                logs = self.get_role_logs(node.role)

                # Check that the filename is valid for that role
                filenames = map(lambda log: log['filename'], logs)
                exp_params = [('filename', is_in_list(filenames))]
                check_arguments(exp_params, dict(filename=filename))

                # Replace the filename with its corresponding path in the agent
                filename = [ log['path'] for log in logs
                                         if log['filename'] == filename ][0]

            res = self.fetch_agent_log(node.ip, self.AGENT_PORT, filename)
            return HttpJsonResponse(res)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

    # the following two methods are the base agent client
    def _check(self, response):
        code, body = response
        if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
        data = json.loads(body)
        if data['error']: raise Exception(data['error'])
        else : return data['result']

    def fetch_agent_log(self, host, port, filename=None):
        """GET (filename) get_log"""
        method = 'get_log'
        params = {}
        if filename:
            params['filename'] = filename
        return self._check(https.client.jsonrpc_get(host, port, '/', method, params=params))



class ApplicationManager(BaseManager):

    def __init__(self, httpsserver, config_parser, **kwargs):
        BaseManager.__init__(self, config_parser)

        # self.controller = Controller(config_parser)
        self.callbacker = DirectorCallbacker(config_parser)
        self.service_id = 0
        self.httpsserver = httpsserver
        self.kwargs = kwargs

        # IPOP setup
        ipop.configure_conpaas_node(config_parser)

        # Ganglia setup
        self.ganglia = ManagerGanglia(config_parser)

        try:
            self.ganglia.configure()
        except Exception, err:
            self.logger.exception('Error configuring Ganglia: %s' % err)
            self.ganglia = None
            return

        err = self.ganglia.start()

        if err:
            self.logger.exception(err)
            self.ganglia = None
        else:
            self.logger.info('Ganglia started successfully')

        # self.counter = 0
        self.state_set(self.S_RUNNING)

    @expose('GET')
    def check_process(self, kwargs):
        """Check if manager process started - just return an empty response"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse()

    @expose('GET')
    def get_app_info(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({
                                # 'methods': self._get_supporeted_functions(),
                                'states': self._get_manager_states(),
                                'nodes': [node.id for node in self.nodes],
                                'volumes': self.volumes.keys()
                                })

    def __copy_config_parser(self, base_config):
        # Create a deep copy of the configuration object
        config_string = StringIO.StringIO()
        base_config.write(config_string)

        # We must reset the buffer to make it ready for reading.
        config_string.seek(0)
        new_config = ConfigParser.ConfigParser()
        new_config.readfp(config_string)

        return new_config

    @expose('POST')
    def add_service(self, kwargs):
        """Expose methods relative to a specific service manager"""

        exp_params = [('service_type', is_in_list(manager_services.keys()))]
        try:
            service_type = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.kwargs.update(kwargs)
        services = manager_services

        try:
            module = __import__(services[service_type]['module'], globals(), locals(), ['*'])
        except ImportError:
            self.state_set(self.S_ERROR)
            raise Exception('Could not import module containing service class "%(module)s"' %
                services[service_type])

        # Get the appropriate class for this service
        service_class = services[service_type]['class']
        try:
            instance_class = getattr(module, service_class)
        except AttributeError:
            self.state_set(self.S_ERROR)
            raise Exception('Could not get service class %s from module %s' % (service_class, module))

        self.state_set(self.S_ADAPTING)

        #probably lock it
        self.service_id = self.service_id + 1

        service_config_parser = self.__copy_config_parser(self.config_parser)
        self._add_manager_configuration(service_config_parser, str(self.service_id), service_type)
        # self._run_manager_start_script(service_config_parser, service_type)

        #Create an instance of the service class
        service_insance = instance_class(service_config_parser, **self.kwargs)

        self.httpsserver.instances[self.service_id] = service_insance
        service_manager_exposed_functions = service_insance.get_exposed_methods()

        for http_method in service_manager_exposed_functions:
           for func_name in service_manager_exposed_functions[http_method]:
               self.httpsserver._register_method(http_method, self.service_id, func_name, service_manager_exposed_functions[http_method][func_name])

        self.state_set(self.S_RUNNING)
        return HttpJsonResponse({ 'service_id': self.service_id })

    @expose('POST')
    def remove_service(self, kwargs):
        exp_params = [('service_id', is_in_list(self.httpsserver.instances.keys()))]
        try:
            service_id = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.state_set(self.S_ADAPTING)
        Thread(target=self._do_stop_service, args=[service_id, True]).start()
        return HttpJsonResponse()

    @expose('POST')
    def start_service(self, kwargs):
        exp_params = [('service_id', is_in_list(self.httpsserver.instances.keys())),
                      ('cloud', is_string)]
        try:
            service_id, cloud = check_arguments(exp_params, kwargs)
            self.check_credits()

            service_manager = self.httpsserver.instances[service_id]
            service_manager.check_state([self.S_INIT, self.S_STOPPED])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        service_manager.logger.info('Manager starting up')
        service_manager.state_set(self.S_PROLOGUE)

        Thread(target=self._do_start_service, args=[service_id, cloud]).start()

        return HttpJsonResponse({ 'state': service_manager.state_get() })

    def _do_start_service(self, service_id, cloud):
        service_manager = self.httpsserver.instances[service_id]

        node_roles = service_manager.get_starting_nodes()
        sninfo = service_manager.get_sninfo(node_roles, cloud)
        nodes = self.callbacker.create_nodes(sninfo, service_id, service_manager)

        self.nodes += nodes
        service_manager.nodes = nodes
        if service_manager.on_start(nodes):
            service_manager.state_set(self.S_RUNNING)
        else:
            service_manager.state_set(self.S_ERROR)

    @expose('POST')
    def stop_service(self, kwargs):
        exp_params = [('service_id', is_in_list(self.httpsserver.instances.keys()))]
        try:
            service_id = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        service_manager = self.httpsserver.instances[service_id]
        service_manager.state_set(self.S_EPILOGUE)
        Thread(target=self._do_stop_service, args=[service_id, False]).start()
        return HttpJsonResponse({ 'state': service_manager.state_get() })

    def _do_stop_service(self, service_id, remove):
        service_manager = self.httpsserver.instances[service_id]
        if service_manager.state_get() != self.S_INIT:
            nodes = service_manager.on_stop()
            service_manager.nodes = []
            service_manager.state_set(self.S_STOPPED)
            for node in nodes:

                # remove also the volumes associated to those nodes
                for k, v in self.volumes.items():
                    if v['vm_id']==node.id:
                        del self.volumes[k]

                self.nodes.remove(filter(lambda n: n.id == node.id, self.nodes)[0])
            self.callbacker.remove_nodes(nodes)
        else:
            service_manager.state_set(self.S_STOPPED)

        if remove:
            code_repo = service_manager.config_parser.get('manager', 'CODE_REPO')
            os.system("rm -rf %s" % code_repo)

            del self.httpsserver.instances[service_id]
            self.httpsserver._deregister_methods(service_id)
            self.state_set(self.S_RUNNING)

    @expose('POST')
    def add_nodes(self, kwargs):
        exp_params = [('service_id', is_in_list(self.httpsserver.instances.keys())),
                      ('nodes', is_dict),
                      ('cloud', is_string)]
        try:
            service_id, node_roles, cloud = check_arguments(exp_params, kwargs)
            self.check_credits()

            service_manager = self.httpsserver.instances[service_id]
            service_manager.check_node_roles(node_roles)
            service_manager.check_state([self.S_RUNNING])
            service_manager.check_add_nodes(node_roles)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        service_manager.state_set(self.S_ADAPTING)
        Thread(target=self._do_add_nodes, args=[service_id, node_roles, cloud]).start()
        return HttpJsonResponse({ 'state': service_manager.state_get() })

    def _do_add_nodes(self, service_id, node_roles, cloud):
        service_manager = self.httpsserver.instances[service_id]

        sninfo = service_manager.get_sninfo(node_roles, cloud)
        nodes = self.callbacker.create_nodes(sninfo, service_id, service_manager)

        self.nodes += nodes
        service_manager.nodes += nodes
        if service_manager.on_add_nodes(nodes):
            service_manager.state_set(self.S_RUNNING)
        else:
            service_manager.state_set(self.S_ERROR)

    @expose('POST')
    def remove_nodes(self, kwargs):
        exp_params = [('service_id', is_in_list(self.httpsserver.instances.keys())),
                      ('nodes', is_dict)]
        try:
            service_id, node_roles = check_arguments(exp_params, kwargs)

            service_manager = self.httpsserver.instances[service_id]
            service_manager.check_node_roles(node_roles)
            service_manager.check_state([self.S_RUNNING])
            service_manager.check_remove_nodes(node_roles)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        service_manager.state_set(self.S_ADAPTING)
        Thread(target=self._do_remove_nodes, args=[service_id, node_roles]).start()
        return HttpJsonResponse({ 'state': service_manager.state_get() })

    def _do_remove_nodes(self, service_id, node_roles):
        service_manager = self.httpsserver.instances[service_id]
        nodes = service_manager.on_remove_nodes(node_roles)
        for node in nodes:
            for k, v in self.volumes.items():
                    if v['vm_id']==node.id:
                        del self.volumes[k]
            self.nodes.remove(filter(lambda n: n.id == node.id, self.nodes)[0])
            service_manager.nodes.remove(filter(lambda n: n.id == node.id, service_manager.nodes)[0])
        self.logger.debug("Current nodes: %s, current volumes: %s" % (self.nodes, self.volumes.keys()))
        self.callbacker.remove_nodes(nodes)
        # if len(service_manager.nodes) == 0:
        #     service_manager.state_set(self.S_STOPPED)
        # else:
        #     service_manager.state_set(self.S_RUNNING)

    def check_volume_name(self, vol_name):
        if not re.compile('^[A-za-z0-9-_]+$').match(vol_name):
            raise Exception('Volume name contains invalid characters')

    @expose('POST')
    def create_volume(self, kwargs):
        node_ids = [ str(node.id) for node in self.nodes ]
        exp_params = [('volumeName', is_not_in_list(self.volumes.keys())),
                      ('volumeSize', is_pos_int),
                      ('agentId', is_in_list(node_ids))]
        try:
            vol_name, vol_size, agent_id = check_arguments(exp_params, kwargs)
            self.check_volume_name(vol_name)

            service_id, _ = self.get_service_id_by_vm_id(agent_id)

            service_manager = self.httpsserver.instances[service_id]
            service_manager.check_state([self.S_RUNNING])
            service_manager.check_create_volume(vol_name, vol_size, agent_id)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        service_manager.state_set(self.S_ADAPTING)
        Thread(target=self._do_create_volume, args=[vol_name, vol_size, agent_id, service_manager]).start()

        return HttpJsonResponse({ 'service_id': service_id })

    def _do_create_volume(self, vol_name, vol_size, agent_id, service_manager):
        """Create a new volume and attach it to the specified agent"""

        service_manager.logger.info("Going to create a new volume")

        try:
            node = [ node for node in self.nodes if node.id == agent_id ][0]
            try:
                # We try to create a new volume.
                volume_name = "vol-%s" % vol_name
                service_manager.logger.debug("Trying to create a volume for the node=%s" % node.id)

                volume = self.callbacker.create_volume(vol_size, volume_name, node.vmid, node.cloud_name)
                volume_id = volume['volume_id']
            except Exception, ex:
                service_manager.logger.exception("Failed to create volume %s: %s" % (volume_name, ex))
                raise

            try:
                # try to find a dev name that is not already in use by the node
                dev_names_in_use = [ vol['dev_name'] for vol in self.volumes.values() if vol['vm_id'] == agent_id]
                dev_name = self.config_parser.get('manager', 'DEV_TARGET')
                while dev_name in dev_names_in_use:
                    # increment the last char from dev_name
                    dev_name = dev_name[:-1] + chr(ord(dev_name[-1]) + 1)
                # attach the volume
                _, dev_name = self.attach_volume(volume_id, node.vmid, service_manager, dev_name, node.cloud_name)

            except Exception, ex:
                service_manager.logger.exception("Failed to attach disk to node %s: %s" % (node.id, ex))
                self.destroy_volume({'vol_id':volume_id, 'cloud': node.cloud_name})
                raise

            volume = {'vol_name': vol_name, 'vol_id' : volume_id,
                      'vol_size': vol_size, 'vm_id': agent_id,
                      'dev_name': dev_name, 'cloud': node.cloud_name}
            try:
                service_manager.on_create_volume(node, volume)
            except Exception, ex:
                service_manager.logger.exception('Failed to configure node %s: %s' % (node.id, ex))
                self.detach_volume(volume)
                self.destroy_volume(volume)
                raise
        except Exception, ex:
            service_manager.logger.exception('Failed to create volume: %s.' % ex)
            service_manager.state_set(self.S_ERROR)
            return

        self.volumes[str(vol_name)] = volume

        service_manager.logger.info('Volume %s created and attached' % vol_name)
        self.logger.info('Current volumes %s ' % self.volumes.keys())
        service_manager.state_set(self.S_RUNNING)

    def attach_volume(self, volume_id, vm_id, service_manager, device_name=None, cloud=None):

        if device_name is None:
            device_name=self.config_parser.get('manager', 'DEV_TARGET')

        service_manager.logger.info("Attaching volume %s to VM %s as %s" % (volume_id, vm_id, device_name))

        # try:
        #     volume = self.get_volume(volume_id)
        # except Exception:
        #     self.logger.info("Volume %s not known" % volume_id)
        #     return

        for attempt in range(1, 11):
            try:
                ret = self.callbacker.attach_volume(vm_id, volume_id, device_name, cloud), device_name
                break;
            except Exception, err:
                service_manager.logger.info("Attempt %s: %s" % (attempt, err))
                # It might take a bit for the volume to actually be
                # created. Let's wait a little and try again.
                time.sleep(10)

        if ret:
            return ret
        else:
            raise Exception("Error attaching volume %s" % volume_id)

    @expose('POST')
    def delete_volume(self, kwargs):
        exp_params = [('volumeName', is_in_list(self.volumes.keys()))]
        try:
            vol_name = check_arguments(exp_params, kwargs)
            self.check_volume_name(vol_name)

            volume = self.volumes[vol_name]
            node = [ node for node in self.nodes if node.id == volume['vm_id'] ][0]
            service_id, _ = self.get_service_id_by_vm_id(node.id)

            service_manager = self.httpsserver.instances[service_id]
            service_manager.check_state([self.S_RUNNING])
            service_manager.check_delete_volume(node, volume)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        service_manager.state_set(self.S_ADAPTING)
        Thread(target=self._do_delete_volume, args=[volume, node, service_manager]).start()

        return HttpJsonResponse({ 'service_id': service_id })

    def _do_delete_volume(self, volume, node, service_manager):
        """Detach a volume and delete it"""
        service_manager.logger.info("Going to remove volume %s" % volume['vol_name'])

        # service_manager.logger.debug("Detaching and deleting volume %s" % volume['vol_name'])
        try:
            service_manager.on_delete_volume(node, volume)
        except Exception, ex:
            service_manager.logger.exception('Failed to mount volume on node %s: %s' % (node.id, ex))

        self.detach_volume(volume, service_manager)
        self.destroy_volume(volume, service_manager)

        self.volumes.pop(volume['vol_name'])

        service_manager.logger.info('Volume %s removed' % volume['vol_name'])
        service_manager.state_set(self.S_RUNNING)

    def destroy_volume(self, volume, service_manager):
        service_manager.logger.info("Destroying volume with id %s" %  volume['vol_id'])

        for attempt in range(1, 11):
            try:
                ret = self.callbacker.destroy_volume(volume['vol_id'], volume['cloud'])
                break
            except Exception, err:
                service_manager.logger.info("Attempt %s: %s" % (attempt, err))
                # It might take a bit for the volume to actually be
                # detached. Let's wait a little and try again.
                time.sleep(10)

        # service_manager.logger.debug("destroy volume ret %s" %  ret)
        if 'error' in ret:
            raise Exception("Error destroying volume %s" % volume['vol_id'])

    def detach_volume(self, volume, service_manager):
        service_manager.logger.info("Detaching volume %s..." % volume['vol_id'])
        ret = self.callbacker.detach_volume(volume['vol_id'], volume['cloud'])
        service_manager.logger.info("Volume %s detached" % volume['vol_id'])
        return ret

    @expose('POST')
    def list_volumes(self, kwargs):
        exp_params = [('service_id', is_in_list(self.httpsserver.instances.keys()), 0)]
        try:
            service_id = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        try:
            self.check_state([self.S_RUNNING, self.S_ADAPTING])
        except:
            return HttpJsonResponse({ 'volumes': [] })

        vols = copy.copy(self.volumes)
        rep_vols = []

        for vol_name in vols:
            vol = vols[vol_name]
            vol['service_id'], vol['service_name'] = self.get_service_id_by_vm_id(vol['vm_id'])

            if service_id != 0:
                if vol['service_id'] == service_id:
                    rep_vols.append(vol)
            else:
                rep_vols.append(vol)

        return HttpJsonResponse({ 'volumes': rep_vols })

    def get_service_id_by_vm_id(self, vm_id):
        for man_id in self.httpsserver.instances:
            if man_id != 0:
                for node in self.httpsserver.instances[man_id].nodes:
                    if node.id == vm_id:
                        return man_id, self.httpsserver.instances[man_id].get_service_type()
        return None

    @expose('POST')
    def stopall(self, kwargs):
        for service_id in self.httpsserver.instances:
            if service_id != 0:
                self._do_stop_service(service_id)
            # self.httpsserver.instances[service_id]._do_stop()
        return HttpJsonResponse()

    def _do_stop(self):
        pass

    def _get_manager_states(self):
        states={}
        for instance in self.httpsserver.instances:
            states[instance] = self.httpsserver.instances[instance].state_get()
        return states

    def _get_nr_services(self):
        return len(self.httpsserver.instances) - 1

    def _get_supporeted_functions(self):
        functions  = {'GET': {}, 'POST': {}, 'UPLOAD': {}}
        for http_method in self.httpsserver.callback_dict:
            for service_id in self.httpsserver.callback_dict[http_method]:
                methods = [method for method in self.httpsserver.callback_dict[http_method][service_id]]
                functions[http_method][service_id] = methods
        return functions

    def _add_manager_configuration(self, config_parser, service_id, service_type):
        # Add service-specific configurations
        config_parser.set('manager', 'TYPE', service_type)
        config_parser.set('manager', 'SERVICE_ID', service_id)

        logfile = config_parser.get('manager', 'LOG_FILE')
        logfile = logfile.replace('manager', 'manager%s' % service_id)
        config_parser.set('manager', 'LOG_FILE', logfile)

        code_repo = config_parser.get('manager', 'CODE_REPO')
        code_repo = os.path.join(code_repo, str(service_id))
        config_parser.set('manager', 'CODE_REPO', code_repo)

        # (teodor) We don't need to support this anymore, as no service is currently
        #          using configuration files. It was an ugly hack anyway.
        #
        # conpaas_home = config_parser.get('manager', 'conpaas_home')
        # mngr_cfg_dir = os.path.join(conpaas_home, 'config', 'manager')
        # mngr_service_cfg = os.path.join(mngr_cfg_dir, service_type + '-manager.cfg')
        # if os.path.isfile(mngr_service_cfg):
        #     config_parser.read(mngr_service_cfg)
        #
        #     #TODO:(genc) get rid of static path
        #     vars_cfg = os.path.join("/root", 'vars.cfg')
        #     ini_str = '[root]\n' + open(vars_cfg, 'r').read()
        #     ini_fp = StringIO.StringIO(ini_str)
        #     config = ConfigParser.RawConfigParser()
        #     config.readfp(ini_fp)
        #
        #     # populate values refering to other values
        #     for key, value in config_parser.items('manager'):
        #         if value.startswith('%') and value.endswith('%'):
        #             config_parser.set('manager', key, config.get('root', value.strip('%').lower()))

    # def _run_manager_start_script(self, config_parser, service_type):
    #     #before running the manager script get again the variable values from the context
    #     conpaas_home = config_parser.get('manager', 'conpaas_home')
    #     mngr_scripts_dir = os.path.join(conpaas_home, 'scripts', 'manager')
    #     mngr_startup_scriptname = os.path.join(mngr_scripts_dir, service_type + '-manager-start')
    #     if os.path.isfile(mngr_startup_scriptname):
    #         proc = subprocess.Popen(['bash', mngr_startup_scriptname] , close_fds=True)
    #         proc.wait()

    @expose('UPLOAD')
    def upload_startup_script(self, kwargs):
        """Write the file uploaded in kwargs['script'] to filesystem.

        Return the script absoulte path on success, HttpErrorResponse on
        failure.
        """
        exp_params = [('script', is_uploaded_file),
                      ('sid', is_string)]
        try:
            script, service_id = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        # Rebuild context script
        # TODO (genc): fix this
        # self.controller.generate_context("web")

        self.logger.debug("Uploading startup script for service %s" % service_id)

        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        filedir = os.path.join(basedir, str(service_id))
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        filename = 'startup.sh'
        fullpath = os.path.join(filedir, filename)

        # Write the uploaded script to filesystem
        file_write_contents(fullpath, script.file.read())

        self.logger.debug("Script uploaded successfully to '%s'" % fullpath)

        # All is good. Return the filename of the uploaded script
        return HttpJsonResponse({'filename': fullpath})

    @expose('GET')
    def get_startup_script(self, kwargs):
        """Return contents of the currently defined startup script, if any"""
        exp_params = [('sid', is_in_list(self.httpsserver.instances.keys()))]
        try:
            service_id = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        fullpath = os.path.join(basedir, str(service_id), 'startup.sh')

        try:
            return HttpJsonResponse(file_get_contents(fullpath))
        except IOError:
            return HttpErrorResponse('No startup script')

    @expose('POST')
    def git_push_hook(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        repo = git.DEFAULT_CODE_REPO
        revision = git.git_code_version(repo)

        for service_id in self.httpsserver.instances:
            if service_id != 0:
                self.httpsserver.instances[service_id].on_git_push()

        return HttpJsonResponse('code version: git-%s' % revision)


class ManagerException(Exception):

    E_CONFIG_READ_FAILED = 0
    E_CONFIG_COMMIT_FAILED = 1
    E_ARGS_INVALID = 2
    E_ARGS_UNEXPECTED = 3
    E_ARGS_MISSING = 4
    E_IAAS_REQUEST_FAILED = 5
    E_STATE_ERROR = 6
    E_CODE_VERSION_ERROR = 7
    E_NOT_ENOUGH_CREDIT = 8
    E_UNKNOWN = 9

    E_STRINGS = [
        'Failed to read configuration',
        'Failed to commit configuration',
        'Invalid arguments',
        'Unexpected arguments %s',  # 1 param (a list)
        'Missing argument "%s"',  # 1 param
        'Failed to request resources from IAAS',
        'Cannot perform requested operation in current state',
        'No code version selected',
        'Not enough credits',
        'Unknown error',
    ]

    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.args = args
        if 'detail' in kwargs:
            self.message = '%s (%s)' % (
                (self.E_STRINGS[code] % args), str(kwargs['detail']))
        else:
            self.message = self.E_STRINGS[code] % args


class WrongNrNodesException(Exception):

    WRONG_NR_NODES = "Requesting to delete %(count)s%(role)s nodes "\
                     "while %(current)s can be removed"

    def __init__(self, count, current, role=None):
        vals = { 'count': count,
                 'role': ' ' + role if role else '',
                 'current': 'only ' + str(current) if current > 0 else 'none' }
        Exception.__init__(self, self.WRONG_NR_NODES % vals)

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

import json, httplib, libcloud, subprocess

from conpaas.core import https 
from conpaas.core.log import create_logger
from conpaas.core.expose import expose
from conpaas.core.controller import Controller
from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import FileUploadField
from conpaas.core.https.server import ConpaasRequestHandlerComponent

from conpaas.core import ipop
from conpaas.core.ganglia import ManagerGanglia

from conpaas.core.services import manager_services

class BaseManager(ConpaasRequestHandlerComponent):
    """Manager class with the following exposed methods:

    startup() -- POST
    getLog() -- GET
    upload_startup_script() -- UPLOAD
    get_startup_script() -- GET
    delete() -- POST
    """

    # Manager states 
    S_INIT = 'INIT'         # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING = 'RUNNING'   # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient state - frontend will 
                            # keep polling until manager out of transient state
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED = 'STOPPED'   # manager stopped
    S_ERROR = 'ERROR'       # manager is in error state

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
        self.logger = create_logger(__name__)
        self.logger.debug('Using libcloud version %s' % libcloud.__version__)

        self.controller = Controller(config_parser)
        self.logfile = config_parser.get('manager', 'LOG_FILE')
        self.config_parser = config_parser
        self.state = self.S_INIT

        self.volumes = []

        

    def _check_state(self, expected_states):
        if self.state not in expected_states:
            raise Exception("Wrong service state: was expecting one of %s"\
                            " but current state is '%s'" \
                            % (expected_states, self.state))

    def _wait_state(self, expected_states, timeout=10 * 60):
        polling_interval = 10   # seconds
        while self.state not in expected_states and timeout >= 0:
            self.logger.debug('Current state is %s, waiting for state to change to one of %s'
                              % (self.state, expected_states))
            time.sleep(polling_interval)
            timeout -= polling_interval
        if timeout < 0:
            raise Exception("Timeout after %s seconds with a polling interval of %s seconds"
                            " while waiting for manager state to become one of %s."
                            % (timeout, polling_interval, expected_states))

    @expose('POST')
    def startup(self, kwargs):
        """Start the given service"""
        # Starting up the service makes sense only in the INIT or STOPPED
        # states
        if self.state != self.S_INIT and self.state != self.S_STOPPED:
            vals = { 'curstate': self.state, 'action': 'startup' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)

        # Check if the specified cloud, if any, is available
        if 'cloud' in kwargs:
            try:
                self._init_cloud(kwargs['cloud'])
            except Exception:
                return HttpErrorResponse(
                    "A cloud named '%s' could not be found" % kwargs['cloud'])

        self.logger.info('Manager starting up')
        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, kwargs=kwargs).start()

        return HttpJsonResponse({ 'state': self.state })

    @expose('GET')
    def getLog(self, kwargs):
        """Return logfile"""
        try:
            return HttpJsonResponse({'log': open(self.logfile).read()})
        except:
            return HttpErrorResponse('Failed to read log')

    def upload_script(self, kwargs, filename):
        """Write the file uploaded in kwargs['script'] to filesystem.

        Return the script absoulte path on success, HttpErrorResponse on
        failure.
        """
        self.logger.debug("upload_script: called with filename=%s" % filename)

        # Check if the required argument 'script' is present
        if 'script' not in kwargs:
            return HttpErrorResponse(ManagerException(
                ManagerException.E_ARGS_MISSING, 'script').message)

        script = kwargs.pop('script')

        # Check if any trailing parameter has been submitted
        if len(kwargs) != 0:
            return HttpErrorResponse(ManagerException(
                ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        # Script has to be a FileUploadField
        if not isinstance(script, FileUploadField):
            return HttpErrorResponse(ManagerException(
                ManagerException.E_ARGS_INVALID,
                detail='script should be a file'
            ).message)

        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        fullpath = os.path.join(basedir, filename)

        # Write the uploaded script to filesystem
        open(fullpath, 'w').write(script.file.read())

        self.logger.debug("upload_script: script uploaded successfully to '%s'"
                          % fullpath)

        # Return the script absolute path
        return fullpath

    @expose('UPLOAD')
    def upload_startup_script(self, kwargs):
        ret = self.upload_script(kwargs, 'startup.sh')

        if type(ret) is HttpErrorResponse:
            # Something went wrong. Return the error
            return ret

        # Rebuild context script 
        self.controller.generate_context("web")

        # All is good. Return the filename of the uploaded script
        return HttpJsonResponse({'filename': ret})

    @expose('GET')
    def get_startup_script(self, kwargs):
        """Return contents of the currently defined startup script, if any"""
        basedir = self.config_parser.get('manager', 'CONPAAS_HOME')
        fullpath = os.path.join(basedir, 'startup.sh')

        try:
            return HttpJsonResponse(open(fullpath).read())
        except IOError:
            return HttpErrorResponse('No startup script')

    def create_volume(self, size, name, vm_id, cloud=None):
        self.logger.info('Creating a volume named %s (%s MBs)' % (
            name, size))

        # If cloud is None, the controller will create this volume on the
        # default cloud
        volume = self.controller.create_volume(size, name, vm_id, cloud)

        # Keep track of the cloud this volume has been created on
        volume.cloud = cloud

        # Keep track of this volume
        self.volumes.append(volume)

        return volume

    def get_volume(self, volume_id):
        for vol in self.volumes:
            if volume_id == vol.id:
                return vol

        known_volumes = [ vol.id for vol in self.volumes ]

        raise Exception("Volume '%s' not found. Known volumes: %s" %
                (volume_id, known_volumes))

    def destroy_volume(self, volume_id):
        self.logger.info("Destroying volume with id %s" % volume_id)

        try:
            volume = self.get_volume(volume_id)
        except Exception:
            self.logger.info("Volume %s not known" % volume_id)
            return

        for attempt in range(1, 11):
            try:
                ret = self.controller.destroy_volume(volume, volume.cloud)
                break
            except Exception, err:
                self.logger.info("Attempt %s: %s" % (attempt, err))
                # It might take a bit for the volume to actually be
                # detached. Let's wait a little and try again.
                time.sleep(10)

        if ret:
            self.volumes.remove(volume)
        else:
            raise Exception("Error destroying volume %s" % volume_id)
   
    def attach_volume(self, volume_id, vm_id, device_name=None):
        if device_name is None:
            device_name=self.config_parser.get('manager', 'DEV_TARGET')

        self.logger.info("Attaching volume %s to VM %s as %s" % (volume_id,
            vm_id, device_name))

        volume = self.get_volume(volume_id)

        class node:
            id = vm_id

        return self.controller.attach_volume(node, volume, device_name,
                volume.cloud), device_name

    def detach_volume(self, volume_id):
        self.logger.info("Detaching volume %s..." % volume_id)

        volume = self.get_volume(volume_id)
        ret = self.controller.detach_volume(volume, volume.cloud)

        self.logger.info("Volume %s detached" % volume_id)
        return ret

    def _init_cloud(self, cloud=None):
        if cloud is None or cloud == 'default':
            cloud = 'iaas'
        return self.controller.get_cloud_by_name(cloud)

    @expose('POST')
    def stop(self, kwargs):
        """Switch to EPILOGUE and call a thread to delete all nodes"""
        # Shutdown only if RUNNING
        if self.state != self.S_RUNNING:
            vals = { 'curstate': self.state, 'action': 'stop' }
            return HttpErrorResponse(self.WRONG_STATE_MSG % vals)
        
        self.state = self.S_EPILOGUE
        Thread(target=self._do_stop, args=[]).start()

        return HttpJsonResponse({ 'state': self.state })


    # @expose('POST')
    # def delete(self, kwargs):
    #     """
    #     Terminate the service after releasing all resources, including cleanly
    #     shutting down agent VMs.

    #     No parameters.
    #     """
    #     Thread(target=self._do_delete, args=[]).start()
    #     return HttpJsonResponse()

    # def _do_delete(self):
    #     ''' Terminate the service, releasing all resources. '''

    #     self.logger.info("Shutting down the service...")
    #     self._do_shutdown()

    #     self.logger.info("Terminating the service...")
    #     self.controller.force_terminate_service()

class ApplicationManager(BaseManager):
    def __init__(self, httpsserver, config_parser, **kwargs):
        BaseManager.__init__(self, config_parser)
        self.service_id = 0
        self.httpsserver = httpsserver
        self.config_parser = config_parser
        self.kwargs = kwargs
        self.state = self.S_INIT

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

    @expose('GET')
    def check_manager_process(self, kwargs):
        """Check if manager process started - just return an empty response"""
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse()    


    @expose('GET')
    def infoapp(self, kwargs):

        return HttpJsonResponse({'info':'this application is doing fine, don\'t worry!',
                                'methods': self._get_supporeted_functions(),
                                'states': self._get_manager_states()
            })    

    @expose('POST')
    def add_service(self, kwargs):
        """Expose methods relative to a specific service manager"""
        self.state = self.S_ADAPTING
        self.kwargs.update(kwargs)

        if 'service_type' not in kwargs:
            vals = { 'arg': 'service_type' }
            return HttpErrorResponse('Argument %s is missing' % vals)

        service_type = kwargs.pop('service_type')
        services = manager_services

        try:
            module = __import__(services[service_type]['module'], globals(), locals(), ['*'])
        except ImportError:
            self.state = self.S_ERROR
            raise Exception('Could not import module containing service class "%(module)s"' % 
                services[service_type])

        # Get the appropriate class for this service
        service_class = services[service_type]['class']
        try:
            instance_class = getattr(module, service_class)
        except AttributeError:
            self.state = self.S_ERROR
            raise Exception('Could not get service class %s from module %s' % (service_class, module))

        #probably lock it 
        self.service_id = self.service_id + 1 

        service_config_parser = copy.copy(self.config_parser)
        self._add_manager_configuration(service_config_parser, str(self.service_id), service_type)
        self._run_manager_start_script(service_config_parser, service_type)
        
        #Create an instance of the service class
        service_insance = instance_class(service_config_parser, **self.kwargs)
        
        self.httpsserver.instances[self.service_id] = service_insance
        service_manager_exposed_functions = service_insance.get_exposed_methods()
        
        for http_method in service_manager_exposed_functions:
           for func_name in service_manager_exposed_functions[http_method]:
               self.httpsserver._register_method(http_method, self.service_id, func_name, service_manager_exposed_functions[http_method][func_name])

        self.state = self.S_RUNNING
        return HttpJsonResponse({'service_id':self.service_id})

    @expose('POST')
    def remove_service(self, kwargs):
        self.state = self.S_ADAPTING
        if 'service_id' not in kwargs:
            vals = { 'arg': 'service_id' }
            self.state = self.S_RUNNING
            return HttpErrorResponse('Argument %s is missing' % vals)
        service_id = kwargs.pop('service_id')

        if service_id not in self.httpsserver.instances:
            self.state = self.S_RUNNING
            return HttpErrorResponse('Wrong service_id: %s ' % service_id)
        del self.httpsserver.instances[service_id]
        self.httpsserver._deregister_methods(service_id)
        self.state = self.S_RUNNING
        return HttpJsonResponse()

    @expose('POST')
    def stopall(self, kwargs):
        for service_id in self.httpsserver.instances: 
            self.httpsserver.instances[service_id]._do_stop()
        return HttpJsonResponse()

    def _do_stop(self):
        pass

    def _get_manager_states(self):
        states={}
        for instance in self.httpsserver.instances:
            states[instance] = self.httpsserver.instances[instance].state
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
        # Add service-specific config file (if any)
        config_parser.set('manager', 'TYPE', service_type)
        config_parser.set('manager', 'SERVICE_ID', service_id)
        conpaas_home = config_parser.get('manager', 'conpaas_home')
        mngr_cfg_dir = os.path.join(conpaas_home, 'config', 'manager')
        mngr_service_cfg = os.path.join(mngr_cfg_dir, service_type + '-manager.cfg')
        if os.path.isfile(mngr_service_cfg):
            config_parser.read(mngr_service_cfg)

            #TODO:(genc) get rid of static path 
            vars_cfg = os.path.join("/root", 'vars.cfg')
            ini_str = '[root]\n' + open(vars_cfg, 'r').read()
            ini_fp = StringIO.StringIO(ini_str)
            config = ConfigParser.RawConfigParser()
            config.readfp(ini_fp)
            
            # populate values refering to other values
            for key, value in config_parser.items('manager'):
                if value.startswith('%') and value.endswith('%'):
                    config_parser.set('manager', key, config.get('root', value.strip('%').lower()))

    def _run_manager_start_script(self, config_parser, service_type):
        #before running the manager script get again the variable values from the context
        conpaas_home = config_parser.get('manager', 'conpaas_home')
        mngr_scripts_dir = os.path.join(conpaas_home, 'scripts', 'manager')
        mngr_startup_scriptname = os.path.join(mngr_scripts_dir, service_type + '-manager-start')          
        if os.path.isfile(mngr_startup_scriptname):
            proc = subprocess.Popen(['bash', mngr_startup_scriptname] , close_fds=True)
            proc.wait()


# the following two methods are the application manager client
def _check(response):
    code, body = response
    if code != httplib.OK: raise HttpError('Received http response code %d' % (code))
    data = json.loads(body)
    if data['error']: raise Exception(data['error']) 
    else : return data['result']

def check_manager_process(host, port):
  method = 'check_manager_process'
  https.client.conpaas_init_ssl_ctx('/etc/cpsdirector/certs', 'director') 
  return _check(https.client.jsonrpc_get(host, port, '/', method))
        
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
            self.message = '%s DETAIL:%s' % (
                (self.E_STRINGS[code] % args), str(kwargs['detail']))
        else:
            self.message = self.E_STRINGS[code] % args

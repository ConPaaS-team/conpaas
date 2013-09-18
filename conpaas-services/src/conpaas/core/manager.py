# -*- coding: utf-8 -*-

"""
    conpaas.core.manager
    ====================

    ConPaaS core: service-independent manager code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread

import time
import os.path

import libcloud

from conpaas.core.log import create_logger
from conpaas.core.expose import expose
from conpaas.core.controller import Controller
from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import FileUploadField

from conpaas.core import ipop
from conpaas.core.ganglia import ManagerGanglia

class BaseManager(object):
    """Manager class with the following exposed methods:

    startup() -- POST
    getLog() -- GET
    upload_startup_script() -- UPLOAD
    get_startup_script() -- GET
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
        self.logger = create_logger(__name__)
        self.logger.debug('Using libcloud version %s' % libcloud.__version__)

        self.controller = Controller(config_parser)
        self.logfile = config_parser.get('manager', 'LOG_FILE')
        self.config_parser = config_parser
        self.state = self.S_INIT

        self.volumes = []

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
            except Exception, err:
                self.logger.info("Attempt %s: %s" % (attempt, err))
                # It might take a bit for the volume to actually be
                # detached. Let's wait a little and try again.
                time.sleep(10)

        if ret:
            self.volumes.remove(volume)
        else:
            raise Exception("Error destroying volume %s" % volume_id)

    def attach_volume(self, volume_id, vm_id, device_name):
        self.logger.info("Attaching volume %s to VM %s as %s" % (volume_id,
            vm_id, device_name))

        volume = self.get_volume(volume_id)

        class node:
            id = vm_id

        return self.controller.attach_volume(node, volume, device_name,
                volume.cloud)

    def detach_volume(self, volume_id):
        self.logger.info("Detaching volume %s..." % volume_id)

        volume = self.get_volume(volume_id)
        ret = self.controller.detach_volume(volume, volume.cloud)

        self.logger.info("Volume %s detached" % volume_id)
        return ret

    def _init_cloud(self, cloud):
        if cloud == 'default':
            cloud = 'iaas'
        return self.controller.get_cloud_by_name(cloud)


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

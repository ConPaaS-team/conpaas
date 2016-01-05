"""
Copyright (c) 2010-2015, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import re
import os
import time
import signal

from threading import Thread
from subprocess import Popen, PIPE
from os.path import exists, devnull, join, lexists
from shutil import rmtree
import pickle
import zipfile
import tarfile
import tempfile
import simplejson

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse,\
    FileUploadField
from conpaas.core.agent import BaseAgent, AgentException
from conpaas.core import git
from conpaas.core.misc import run_cmd

class GenericAgent(BaseAgent):
    """Agent class with the following exposed methods:

    check_agent_process() -- GET
    init_agent(agents_info, ip) -- POST
    update_code(filetype, codeVersionId, file) -- UPLOAD
    mount_volume(dev_name, vol_name) -- POST
    unmount_volume(dev_name) -- POST
    execute_script(command, parameters, agents_info) -- POST
    get_script_status() -- GET
    get_log(filename) -- GET
    """
    def __init__(self, config_parser, **kwargs):
        """Initialize Generic Agent.

        'config_parser' represents the agent config file.
        **kwargs holds anything that can't be sent in config_parser.
        """
        BaseAgent.__init__(self, config_parser)

        self.SERVICE_ID = config_parser.get('agent', 'SERVICE_ID')
        self.generic_dir = config_parser.get('agent', 'CONPAAS_HOME')
        self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
        self.LOG_FILE = config_parser.get('agent', 'LOG_FILE')
        self.CODE_DIR = join(self.VAR_CACHE, 'bin')
        self.ROOT_DIR = '/root'
        self.VOLUME_DIR = '/media'
        self.env = {}
        self.processes = {}

    @expose('POST')
    def init_agent(self, kwargs):
        """Set the environment variables"""

        if 'agents_info' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'agents_info').message)
        agents_info = simplejson.loads(kwargs.pop('agents_info'))

        if 'ip' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'ip').message)
        agent_ip = kwargs.pop('ip')

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        self.state = 'ADAPTING'

        self.logger.info('Setting agent environment')

        target_dir = self.VAR_CACHE
        with open(join(target_dir, 'agents.json'), 'w') as outfile:
            simplejson.dump(agents_info, outfile)

        agent_role = [i['role'] for i in agents_info if i['ip'] == agent_ip][0]
        master_ip = [i['ip'] for i in agents_info if i['role'] == 'master'][0]

        self.env.update({'MY_IP':agent_ip})
        self.env.update({'MY_ROLE':agent_role})
        self.env.update({'MASTER_IP':master_ip})

        self.state = 'RUNNING'
        self.logger.info('Agent initialized')
        return HttpJsonResponse()

    @expose('UPLOAD')
    def update_code(self, kwargs):

        if 'filetype' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'filetype').message)
        filetype = kwargs.pop('filetype')

        if 'codeVersionId' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'codeVersionId').message)
        codeVersionId = kwargs.pop('codeVersionId')

        if 'file' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'file').message)
        file = kwargs.pop('file')

        if filetype != 'git' and not isinstance(file, FileUploadField):
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_INVALID, detail='"file" should be a file').message)
        else:
            revision = file

        self.logger.info("Updating code to version '%s'" % codeVersionId)

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        if filetype == 'zip':
            source = zipfile.ZipFile(file.file, 'r')
        elif filetype == 'tar':
            source = tarfile.open(fileobj=file.file)
        elif filetype == 'git':
            source = git.DEFAULT_CODE_REPO
        else:
            return HttpErrorResponse('Unknown archive type ' + str(filetype))

        # kill all scripts that may still be running
        if self.processes:
            self._kill_all_processes()
            self.processes = {}

        target_dir = self.CODE_DIR

        if exists(target_dir):
            rmtree(target_dir)

        if filetype == 'git':
            subdir = str(self.SERVICE_ID)
            self.logger.debug("git_enable_revision('%s', '%s', '%s', '%s')" %
                    (target_dir, source, revision, subdir))
            git.git_enable_revision(target_dir, source, revision, subdir)
        else:
            source.extractall(target_dir)

        self.logger.info("Code updated, executing the 'init' command")

        # every time a new code tarball is activated, execute the init.sh script
        self._execute_script('init')

        return HttpJsonResponse()

    @expose('POST')
    def mount_volume(self, kwargs):
        """Mount a volume to a Generic node."""

        if 'dev_name' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'dev_name').message)
        dev_name = "/dev/%s" % kwargs.pop('dev_name')

        if 'vol_name' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'vol_name').message)
        vol_name = kwargs.pop('vol_name')

        if not re.compile('^[A-za-z0-9-_]+$').match(vol_name):
            return HttpErrorResponse('Volume name contains invalid characters')

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        self.logger.info("Mount operation starting up for volume '%s' on '%s'"
                % (vol_name, dev_name))

        self.state = 'ADAPTING'
        try:
            mount_point = join(self.VOLUME_DIR, vol_name)
            self._mount(dev_name, mount_point, True)
        except Exception as e:
            self.logger.exception("Failed to mount volume '%s'" % vol_name)
            self.state = 'ERROR'
            return HttpErrorResponse('Failed to mount volume: ' + e.message)

        self.state = 'RUNNING'
        self.logger.info('Mount operation completed')
        return HttpJsonResponse()

    def _check_dev_is_attached(self, dev_name):
        # if the device file does not exist, the volume is definitely not
        # attached yet
        if not lexists(dev_name):
            return False

        # force the kernel to re-read the partition table
        # this allows reusing the device name after a volume was detached
        run_cmd('sfdisk -R %s' % dev_name)

        # check if the device appears in the partitions list
        short_dev_name = dev_name.split('/')[2]
        output, _ = run_cmd('cat /proc/partitions')
        return short_dev_name in output

    def _mount(self, dev_name, mount_point, mkfs):
        devnull_fd = open(devnull, 'w')
        # waiting for our block device to be available
        dev_found = False
        dev_prefix = dev_name.split('/')[2][:-1]

        for attempt in range(1, 11):
            self.logger.info("Generic node waiting for block device '%s'" % dev_name)
            if self._check_dev_is_attached(dev_name):
                dev_found = True
                break
            else:
                # On EC2 the device name gets changed
                # from /dev/sd[a-z] to /dev/xvd[a-z]
                if self._check_dev_is_attached(dev_name.replace(dev_prefix, 'xvd')):
                    dev_found = True
                    dev_name = dev_name.replace(dev_prefix, 'xvd')
                    self.logger.info("Block device is renamed to '%s'" % dev_name)
                    break

            time.sleep(10)

        # create mount point
        mkdir_cmd = "mkdir -p %s" % mount_point
        run_cmd(mkdir_cmd)

        if dev_found:
            self.logger.info("Generic node has now access to '%s'" % dev_name)

            # prepare block device
            if mkfs:
                self.logger.info("Creating new file system on '%s'" % dev_name)
                prepare_args = ['mkfs.ext4', '-q', '-m0', dev_name]
                proc = Popen(prepare_args, stdin=PIPE, stdout=devnull_fd,
                        stderr=devnull_fd, close_fds=True)

                proc.communicate(input="y") # answer interactive question with y
                if proc.wait() != 0:
                    self.logger.critical('Failed to prepare storage device:(code=%d)' %
                            proc.returncode)
                else:
                    self.logger.info('File system created successfully')
            else:
                self.logger.info(
                  "Not creating a new file system on '%s'" % dev_name)
                time.sleep(10)

            # mount
            mount_args = ['mount', dev_name, mount_point]
            mount_cmd = ' '.join(mount_args)
            self.logger.debug("Running command '%s'" % mount_cmd)
            _, err = run_cmd(mount_cmd)

            if err:
                self.logger.critical('Failed to mount storage device: %s' % err)
            else:
                self.logger.info("Generic node has prepared and mounted '%s'"
                        % mount_point)
        else:
            self.logger.critical("Block device '%s' unavailable" % dev_name)

    @expose('POST')
    def unmount_volume(self, kwargs):
        """Unmount a volume to a Generic node."""

        if 'vol_name' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'vol_name').message)
        vol_name = kwargs.pop('vol_name')

        if not re.compile('^[A-za-z0-9-_]+$').match(vol_name):
            return HttpErrorResponse('Volume name contains invalid characters')

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        self.logger.info("Unmount operation starting up for volume '%s'"
                % vol_name)

        self.state = 'ADAPTING'
        try:
            self._unmount(vol_name)
        except Exception as e:
            self.logger.exception("Failed to unmount volume '%s'" % vol_name)
            self.state = 'ERROR'
            return HttpErrorResponse('Failed to unmount volume: ' + e.message)

        self.state = 'RUNNING'
        self.logger.info('Unmount operation completed')
        return HttpJsonResponse()

    def _unmount(self, vol_name):
        mount_point = join(self.VOLUME_DIR, vol_name)

        # kill all processes still using the volume
        fuser_args = ['fuser', '-km', mount_point]
        fuser_cmd = ' '.join(fuser_args)
        self.logger.debug("Running command '%s'" % fuser_cmd)
        run_cmd(fuser_cmd)

        # unmount
        unmount_args = ['umount', mount_point]
        unmount_cmd = ' '.join(unmount_args)
        self.logger.debug("Running command '%s'" % unmount_cmd)
        _, err = run_cmd(unmount_cmd)
        if err:
            self.logger.critical('Failed to unmount storage device: %s' % err)
        else:
            self.logger.info("Generic node has succesfully unmounted '%s'"
                    % mount_point)

    @expose('POST')
    def execute_script(self, kwargs):
        if 'command' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'command').message)
        command = kwargs.pop('command')
        if command not in ( 'notify', 'run', 'interrupt', 'cleanup' ):
            return HttpErrorResponse('Invalid command: %s' % command)

        if 'parameters' not in kwargs:
            parameters = ''
        else:
            parameters = kwargs.pop('parameters')

        if 'agents_info' not in kwargs:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_MISSING, 'agents_info').message)
        agents_info = simplejson.loads(kwargs.pop('agents_info'))

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        if command == 'notify':
            self.logger.info("Executing the '%s' command" % command)
        else:
            self.logger.info("Executing the '%s' command with parameters '%s'"
                    % (command, parameters))

        self.state = 'ADAPTING'

        target_dir = self.VAR_CACHE
        with open(join(target_dir, 'agents.json'), 'w') as outfile:
            simplejson.dump(agents_info, outfile)

        if command == 'interrupt':
            # if no script is running, do nothing
            if not self._are_scripts_running():
                self.logger.info("No scripts are currently running")

            # if interrupt is already running, kill all processes
            elif self._get_script_status('interrupt') == 'RUNNING':
                self.logger.info("Script 'interrupt.sh' is already running")
                self._kill_all_processes()

            # execute the script and afterwards kill all processes
            else:
                Thread(target=self._do_interrupt, args=[parameters]).start()
        else:
            # if scripts are already running, do nothing
            if self._are_scripts_running():
                self.logger.info("Scripts are already running")

            # execute the script
            else:
                self._execute_script(command, parameters)

        self.state = 'RUNNING'
        return HttpJsonResponse()

    def _do_interrupt(self, parameters):
        # execute interrupt.sh
        self._execute_script('interrupt', parameters)

        # wait for it to finish execution
        process = self.processes['interrupt']
        if process is not None:
            process.wait()

        # kill all processes
        self._kill_all_processes()

    def _execute_script(self, command, parameters=''):
        script_name = '%s.sh' % command
        script_path = join(self.CODE_DIR, script_name)

        if not exists(script_path):
            self.logger.critical("Script '%s' does not exist in the active code tarball"
                    % script_name)
            return

        start_args = [ "bash",  script_path ] + parameters.split()
        self.processes[command] = Popen(start_args, cwd=self.generic_dir,
                env=self.env, close_fds=True, preexec_fn=os.setsid)

        self.logger.info("Script '%s' is running" % script_name)

    def _kill_all_processes(self):
        self.logger.info("Killing all running processes")
        for process in self.processes.values():
            if process is not None and process.poll() is None:
                try:
                    pgrp = process.pid
                    self.logger.debug("Killing process group %s" % pgrp)
                    os.killpg(pgrp, signal.SIGTERM)
                except Exception as e:
                    self.logger.critical('Failed to kill process group %s' % pgrp)

    def _are_scripts_running(self):
        for command in ( 'init', 'notify', 'run', 'interrupt', 'cleanup' ):
            if self._get_script_status(command) == 'RUNNING':
                return True
        return False

    @expose('GET')
    def get_script_status(self, kwargs):
        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        scripts = {}
        for command in ( 'init', 'notify', 'run', 'interrupt', 'cleanup' ):
            script_name = "%s.sh" % command
            scripts[script_name] = self._get_script_status(command)
        return HttpJsonResponse({ 'scripts' : scripts })

    def _get_script_status(self, command):
        if command not in self.processes or self.processes[command] is None:
            return "NEVER STARTED"

        returncode = self.processes[command].poll()
        if returncode is not None:
            return "STOPPED (return code %s)" % returncode
        else:
            return "RUNNING"

    @expose('GET')
    def get_log(self, kwargs):
        """Return the contents of a logfile"""
        if 'filename' not in kwargs:
            filename = self.LOG_FILE
        else:
            filename = kwargs.pop('filename')
            if filename not in ( 'agent.out', 'agent.err' ):
                return HttpErrorResponse("ERROR: Invalid log filename: '%s'"
                        % filename)
            filename = join(self.ROOT_DIR, filename)

        if len(kwargs) != 0:
            return HttpErrorResponse(AgentException(
                AgentException.E_ARGS_UNEXPECTED, kwargs.keys()).message)

        try:
            return HttpJsonResponse({'log': open(filename).read()})
        except:
            return HttpErrorResponse("Failed to read log file: '%s'" % filename)

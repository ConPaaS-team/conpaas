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

from conpaas.core.misc import run_cmd, run_cmd_code
from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

START_CLUSTER = None
STOP_CLUSTER = None
TASKMANAGER = None
FLINK_CONFIG = None
TIMEOUT = None

class FlinkAgent(BaseAgent):

    def __init__(self, config_parser, **kwargs):
        """Initialize Flink Agent.

        'config_parser' represents the agent config file.
        **kwargs holds anything that can't be sent in config_parser.
        """
        BaseAgent.__init__(self, config_parser)

        self.SERVICE_ID = config_parser.get('agent', 'SERVICE_ID')
        self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')

        global START_CLUSTER, STOP_CLUSTER, TASKMANAGER, FLINK_CONFIG, TIMEOUT
        START_CLUSTER = config_parser.get('flink', 'START_CLUSTER')
        STOP_CLUSTER = config_parser.get('flink', 'STOP_CLUSTER')
        TASKMANAGER = config_parser.get('flink', 'TASKMANAGER')
        FLINK_CONFIG = config_parser.get('flink', 'FLINK_CONFIG')
        TIMEOUT = config_parser.get('flink', 'TIMEOUT')

        self.master_ip = None

    @expose('POST')
    def init_agent(self, kwargs):
        """Set the environment variables"""

        exp_params = [('master_ip', is_string)]
        try:
            self.master_ip = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info('Updating the Flink configuration file')

        f = open(FLINK_CONFIG, "r")
        lines = f.readlines()
        f.close()

        f = open(FLINK_CONFIG, "w")
        for line in lines:
            if "jobmanager.rpc.address" in line:
                f.write("jobmanager.rpc.address: %s\n" % self.master_ip)
            else:
                f.write(line)
        f.write("akka.ask.timeout: %s\n" % TIMEOUT)
        f.write("akka.lookup.timeout: %s\n" % TIMEOUT)
        f.write("akka.logger-startup-timeout: %s\n" % TIMEOUT)
        f.write("fs.overwrite-files: true\n")
        f.close()

        self.logger.info('Agent initialized')
        return HttpJsonResponse()

    @expose('POST')
    def start_master(self, kwargs):
        """Start the JobManager and TaskManager processes"""

        exp_params = []
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info('Starting the JobManager and TaskManager processes')

        start_args = [ START_CLUSTER ]
        devnull_fd = open(devnull, 'w')
        proc = Popen(start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            self.logger.critical('Failed to start master: (code=%d)' % proc.returncode)

        self.logger.info('JobManager and TaskManager started')

        self._wait_event("taskmanager", "Successful\ initialization")
        self.logger.info('JobManager and TaskManager initialized')

        return HttpJsonResponse()

    @expose('POST')
    def start_worker(self, kwargs):
        """Start the TaskManager processes"""

        exp_params = []
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info('Starting the TaskManager process')

        start_args = [ TASKMANAGER, 'start' ]
        devnull_fd = open(devnull, 'w')
        proc = Popen(start_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            self.logger.critical('Failed to start worker: (code=%d)' % proc.returncode)

        self.logger.info('TaskManager started')

        self._wait_event("taskmanager", "Successful\ initialization")
        self.logger.info('TaskManager initialized')

        return HttpJsonResponse()

    @expose('POST')
    def stop_worker(self, kwargs):
        """Stop the TaskManager processes"""

        exp_params = []
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info('Stopping the TaskManager process')

        stop_args = [ TASKMANAGER, 'stop' ]
        devnull_fd = open(devnull, 'w')
        proc = Popen(stop_args, stdout = devnull_fd, stderr = devnull_fd, close_fds = True)
        if proc.wait() != 0:
            self.logger.critical('Failed to stop worker: (code=%d)' % proc.returncode)

        self._wait_event("taskmanager", "Shutting\ down")
        self.logger.info('TaskManager stopped')
        return HttpJsonResponse()

    @expose('POST')
    def wait_unregister(self, kwargs):
        """Wait for the TaskManager processes to be unregistered"""

        exp_params = []
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self._wait_event("jobmanager", "Unregistered\ task\ manager")
        return HttpJsonResponse()

    def _wait_event(self, process, event_string):
        wait_time = 5
        code = 1
        while code != 0:
            time.sleep(wait_time)
            poll_cmd = ("grep " + event_string + " " +
                        "/var/cache/cpsagent/flink-" + process + ".log")
            _, _, code = run_cmd_code(poll_cmd)

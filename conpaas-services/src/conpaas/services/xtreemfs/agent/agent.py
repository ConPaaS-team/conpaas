# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from os.path import exists, join
from os import makedirs, remove

from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse
from conpaas.core.https.server import HttpFileDownloadResponse
from conpaas.services.xtreemfs.agent import role
from conpaas.core.agent import BaseAgent, AgentException
from conpaas.core.misc import run_cmd
from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

from threading import Lock
import pickle
import base64
import copy

class XtreemFSAgent(BaseAgent):
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser
                                # (hopefully the new service won't need anything extra)
        BaseAgent.__init__(self, config_parser)
        role.init(config_parser)

        self.VAR_TMP = config_parser.get('agent','VAR_TMP')

        self.dir_file = join(self.VAR_TMP,'dir.pickle')
        self.mrc_file = join(self.VAR_TMP,'mrc.pickle')
        self.osd_file = join(self.VAR_TMP,'osd.pickle')
        self.mrc_lock = Lock()
        self.dir_lock = Lock()
        self.osd_lock = Lock()

        self.DIR = role.DIR
        self.MRC = role.MRC
        self.OSD = role.OSD

    def _create(self, post_params, class_file, pClass):
        if exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_EXISTS).message)
        try:
            if type(post_params) != dict:
                raise TypeError()
            self.logger.debug('Creating class')
            p = pClass(**post_params)
            self.logger.debug('Created class')
        except (ValueError, TypeError) as e:
            ex = AgentException(AgentException.E_ARGS_INVALID, detail=str(e))
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)
        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)
        else:
            try:
                self.logger.debug('Openning file %s' % class_file)
                fd = open(class_file, 'w')
                pickle.dump(p, fd)
                fd.close()
            except Exception as e:
                ex = AgentException(AgentException.E_CONFIG_COMMIT_FAILED,
                    detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)
            else:
                self.logger.debug('Created class file')
                return HttpJsonResponse()

    def _stop(self, kwargs, class_file, pClass):
        self.logger.debug("_stop(kwargs=%s, class_file=%s, pClass=%s)" %
                (kwargs, class_file, pClass))

        if not exists(class_file):
            self.logger.error("class_file '%s' does not exist" % class_file)

            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)

        try:
            try:
                fd = open(class_file, 'r')
                p = pickle.load(fd)
                self.logger.debug('dump file %s loaded' %class_file)
                fd.close()
            except Exception as e:
                ex = AgentException(
                    AgentException.E_CONFIG_READ_FAILED, detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)

            if 'drain' in kwargs:
                p.stop(kwargs['drain'])
            else:
                p.stop()

            self.logger.debug("Removing class_file '%s'" % class_file)
            remove(class_file)
            return HttpJsonResponse()

        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)

    @expose('POST')
    def createDIR(self, kwargs):
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('uuid', is_string)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.dir_lock:
            return self._create(orig_kwargs, self.dir_file, self.DIR)

    @expose('POST')
    def createMRC(self, kwargs):
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('dir_serviceHost', is_string),
                      ('uuid', is_string),
                      ('hostname', is_string)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.mrc_lock:
            return self._create(orig_kwargs, self.mrc_file, self.MRC)

    @expose('POST')
    def createOSD(self, kwargs):
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('dir_serviceHost', is_string),
                      ('uuid', is_string),
                      ('hostname', is_string),
                      ('mkfs', is_bool, True),
                      ('device_name', is_string)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.osd_lock:
            return self._create(orig_kwargs, self.osd_file, self.OSD)

    @expose('POST')
    def stopDIR(self, kwargs):
        """Kill the DIR service"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.dir_lock:
            return self._stop(kwargs, self.dir_file, self.DIR)

    @expose('POST')
    def stopMRC(self, kwargs):
        """Kill the MRC service"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.mrc_lock:
            return self._stop(kwargs, self.mrc_file, self.MRC)

    @expose('POST')
    def stopOSD(self, kwargs):
        """Kill the OSD service"""
        try:
            exp_params = [('drain', is_bool, False)]
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.osd_lock:
            return self._stop(kwargs, self.osd_file, self.OSD)

    @expose('POST')
    def startup(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info('Agent started up')
        return HttpJsonResponse()

    @expose('POST')
    def set_snapshot(self, kwargs):
        try:
            exp_params = [('archive_url', is_string)]
            archive_url = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.info('set_snapshot: restoring archive')

        archive_cmd = "wget --ca-certificate /etc/cpsagent/certs/ca_cert.pem "
        archive_cmd += archive_url + " -O - | tar xz -C /"

        self.logger.debug('set_snapshot: %s' % archive_cmd)

        out, err = run_cmd(archive_cmd)

        self.logger.debug('set_snapshot: stdout %s' % out)
        self.logger.debug('set_snapshot: stderr %s' % err)

        self.logger.info('set_snapshot: archive restored successfully')
        return HttpJsonResponse()

    @expose('POST')
    def get_snapshot(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        # pack data from:
        #     /etc/cpsagent/certs/ (original agent certificates)
        #     /etc/xos/xtreemfs/ (config files, SSL-certificates, policies)
        #     /var/lib/xtreemfs/ (save everything, after shutting down the services)
        #     /var/log/xtreemfs/ (xtreemfs log files)
        filename = "/root/snapshot.tar.gz"
        dirs = "var/lib/xtreemfs/ etc/xos/xtreemfs/ var/log/xtreemfs/ etc/cpsagent/certs"

        err, out = run_cmd("tar -czf %s %s" % (filename, dirs), "/")
        if err:
            self.logger.exception(err)
            return HttpErrorResponse(err)

        return HttpFileDownloadResponse("snapshot.tar.gz", filename)

    @expose('POST')
    def set_certificates(self, kwargs):
        try:
            exp_params = [('dir', is_string),
                          ('mrc', is_string),
                          ('osd', is_string),
                          ('truststore', is_string)]
            dir_cert, mrc_cert, osd_cert, trusted = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.logger.debug('set_snapshot called')

        # write certificates and truststore to the xtreemfs config directory
        path = "/etc/xos/xtreemfs/truststore/certs"
        if not exists(path):
            makedirs(path)
        open(path + "/dir.p12", 'wb').write(base64.b64decode(dir_cert))
        open(path + "/mrc.p12", 'wb').write(base64.b64decode(mrc_cert))
        open(path + "/osd.p12", 'wb').write(base64.b64decode(osd_cert))
        open(path + "/trusted.jks", 'wb').write(base64.b64decode(trusted))

        return HttpJsonResponse()

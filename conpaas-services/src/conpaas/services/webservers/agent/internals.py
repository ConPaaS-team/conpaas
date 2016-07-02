# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from os.path import exists, devnull, join
from subprocess import Popen
from os import remove, makedirs, rename
from shutil import rmtree
from threading import Lock
import pickle
import zipfile
import tarfile
import copy

from conpaas.core.agent import BaseAgent, AgentException
from conpaas.services.webservers.agent import role

from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse, FileUploadField
from conpaas.core.expose import expose
from conpaas.core import git

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file


class WebServersAgent(BaseAgent):

    def __init__(self, config_parser):
        BaseAgent.__init__(self, config_parser)

        role.init(config_parser)

        self.SERVICE_ID = config_parser.get('agent', 'SERVICE_ID')
        self.VAR_TMP = config_parser.get('agent', 'VAR_TMP')
        self.VAR_CACHE = config_parser.get('agent', 'VAR_CACHE')
        self.VAR_RUN = config_parser.get('agent', 'VAR_RUN')

        self.webserver_file = join(self.VAR_TMP, 'web-php.pickle')
        self.webservertomcat_file = join(self.VAR_TMP, 'web-tomcat.pickle')
        self.httpproxy_file = join(self.VAR_TMP, 'proxy.pickle')
        self.php_file = join(self.VAR_TMP, 'php.pickle')
        self.tomcat_file = join(self.VAR_TMP, 'tomcat.pickle')
        self.scalaris_file = join(self.VAR_TMP, 'scalaris.pickle')

        self.web_lock = Lock()
        self.webservertomcat_lock = Lock()
        self.httpproxy_lock = Lock()
        self.php_lock = Lock()
        self.tomcat_lock = Lock()
        self.scalaris_lock = Lock()

        self.WebServer = role.NginxStatic
        self.HttpProxy = role.NginxProxy

        if self.ganglia:
            self.ganglia.add_modules(('nginx_mon', 'nginx_proxy_mon',
                                      'php_fpm_mon'))

    def _get(self, get_params, class_file, pClass):
        if not exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            fd = open(class_file, 'r')
            p = pickle.load(fd)
            fd.close()
        except Exception as e:
            ex = AgentException(
                AgentException.E_CONFIG_READ_FAILED,
                pClass.__name__, class_file, detail=e)
            self.logger.exception(ex.message)
            return HttpErrorResponse(ex.message)
        else:
            return HttpJsonResponse({'return': p.status()})

    def _create(self, post_params, class_file, pClass):
        if exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_EXISTS).message)
        try:
            if type(post_params) != dict:
                raise TypeError()
            p = pClass(**post_params)
        except (ValueError, TypeError) as e:
            ex = AgentException(AgentException.E_ARGS_INVALID, detail=str(e))
            return HttpErrorResponse(ex.message)
        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)
        else:
            try:
                fd = open(class_file, 'w')
                pickle.dump(p, fd)
                fd.close()
            except Exception as e:
                ex = AgentException(AgentException.E_CONFIG_COMMIT_FAILED, detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)
            else:
                return HttpJsonResponse()

    def _update(self, post_params, class_file, pClass):
        try:
            if type(post_params) != dict:
                raise TypeError()
            fd = open(class_file, 'r')
            p = pickle.load(fd)
            fd.close()
            p.configure(**post_params)
            p.restart()
        except (ValueError, TypeError) as e:
            self.logger.exception(e)
            ex = AgentException(AgentException.E_ARGS_INVALID)
            return HttpErrorResponse(ex.message)
        except Exception as e:
            self.logger.exception(e)
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            return HttpErrorResponse(ex.message)
        else:
            try:
                fd = open(class_file, 'w')
                pickle.dump(p, fd)
                fd.close()
            except Exception as e:
                self.logger.exception(ex.message)
                ex = AgentException(AgentException.E_CONFIG_COMMIT_FAILED, detail=e)
                return HttpErrorResponse(ex.message)
            else:
                return HttpJsonResponse()

    def _stop(self, get_params, class_file, pClass):
        if not exists(class_file):
            return HttpErrorResponse(AgentException(
                AgentException.E_CONFIG_NOT_EXIST).message)
        try:
            try:
                fd = open(class_file, 'r')
                p = pickle.load(fd)
                fd.close()
            except Exception as e:
                ex = AgentException(
                    AgentException.E_CONFIG_READ_FAILED, detail=e)
                self.logger.exception(ex.message)
                return HttpErrorResponse(ex.message)
            p.stop()
            remove(class_file)
            return HttpJsonResponse()
        except Exception as e:
            ex = AgentException(AgentException.E_UNKNOWN, detail=e)
            self.logger.exception(e)
            return HttpErrorResponse(ex.message)

    @expose('POST')
    def createScalaris(self, kwargs):
        """Create the ScalarisProcessManager"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('first_node', is_bool),
                      ('known_hosts', is_string)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.scalaris_lock:
            return self._create(orig_kwargs, self.scalaris_file, role.ScalarisProcessManager)

    @expose('POST')
    def createWebServer(self, kwargs):
        """Create the WebServer"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('port', is_pos_int),
                      ('code_versions', is_list)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.web_lock:
            return self._create(orig_kwargs, self.webserver_file, self.WebServer)

    @expose('POST')
    def updateWebServer(self, kwargs):
        """UPDATE the WebServer"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('port', is_pos_int),
                      ('code_versions', is_list)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.web_lock:
            return self._update(orig_kwargs, self.webserver_file, self.WebServer)

    @expose('GET')
    def getHttpProxyState(self, kwargs):
        """GET state of HttpProxy"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.httpproxy_lock:
            return self._get(kwargs, self.httpproxy_file, self.HttpProxy)

    @expose('POST')
    def stopWebServer(self, kwargs):
        """KILL the WebServer"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.web_lock:
            return self._stop(kwargs, self.webserver_file, self.WebServer)

    @expose('POST')
    def createHttpProxy(self, kwargs):
        """Create the HttpProxy"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('port', is_pos_int),
                      ('code_version', is_string),
                      ('web_list', is_non_empty_list),
                      ('fpm_list', is_list, []),
                      ('tomcat_list', is_list, []),
                      ('tomcat_servlets', is_list, []),
                      ('cdn', is_bool, None)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.httpproxy_lock:
            return self._create(orig_kwargs, self.httpproxy_file, self.HttpProxy)

    @expose('POST')
    def updateHttpProxy(self, kwargs):
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('port', is_pos_int),
                      ('code_version', is_string),
                      ('web_list', is_non_empty_list),
                      ('fpm_list', is_list, []),
                      ('tomcat_list', is_list, []),
                      ('tomcat_servlets', is_list, []),
                      ('cdn', is_bool, None)]
        try:
            check_arguments(exp_params, kwargs)

            with self.httpproxy_lock:
                return self._update(orig_kwargs, self.httpproxy_file, self.HttpProxy)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

    @expose('POST')
    def stopHttpProxy(self, kwargs):
        """KILL the HttpProxy"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.httpproxy_lock:
            return self._stop(kwargs, self.httpproxy_file, self.HttpProxy)

    @expose('GET')
    def getPHPState(self, kwargs):
        """GET state of PHPProcessManager"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.php_lock:
            return self._get(kwargs, self.php_file, role.PHPProcessManager)

    @expose('POST')
    def createPHP(self, kwargs):
        """Create the PHPProcessManager"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('port', is_pos_int),
                      ('scalaris', is_string),
                      ('configuration', is_dict)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.php_lock:
            return self._create(orig_kwargs, self.php_file, role.PHPProcessManager)

    @expose('POST')
    def updatePHP(self, kwargs):
        """UPDATE the PHPProcessManager"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('port', is_pos_int),
                      ('scalaris', is_string),
                      ('configuration', is_dict)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.php_lock:
            return self._update(orig_kwargs, self.php_file, role.PHPProcessManager)

    @expose('POST')
    def stopPHP(self, kwargs):
        """KILL the PHPProcessManager"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.php_lock:
            return self._stop(kwargs, self.php_file, role.PHPProcessManager)

    def fix_session_handlers(self, dir):
        session_dir = join(self.VAR_CACHE, 'www')
        cmd_path = join(session_dir, 'phpsession.sh')
        script_path = join(session_dir, 'phpsession.php')
        devnull_fd = open(devnull, 'w')
        proc = Popen([cmd_path, dir, script_path], stdout=devnull_fd, stderr=devnull_fd, close_fds=True)
        proc.wait()
        # if proc.wait() != 0:
        #  self.logger.exception('Failed to start the script to fix the session handlers')
        #  raise OSError('Failed to start the script to fix the session handlers')

    @expose('UPLOAD')
    def updatePHPCode(self, kwargs):
        valid_filetypes = [ 'zip', 'tar', 'git' ]
        exp_params = [('filetype', is_in_list(valid_filetypes)),
                      ('codeVersionId', is_string),
                      ('file', is_uploaded_file, None),
                      ('revision', is_string, '')]
        try:
            filetype, codeVersionId, file, revision = check_arguments(exp_params, kwargs)
            if filetype != 'git' and not file:
                raise Exception("The '%s' filetype requires an uploaded file" % filetype)
            elif filetype == 'git' and not revision:
                raise Exception("The 'git' filetype requires the 'revision' parameter")
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if filetype == 'zip':
            source = zipfile.ZipFile(file.file, 'r')
        elif filetype == 'tar':
            source = tarfile.open(fileobj=file.file)
        elif filetype == 'git':
            source = git.DEFAULT_CODE_REPO

        if not exists(join(self.VAR_CACHE, 'www')):
            makedirs(join(self.VAR_CACHE, 'www'))

        target_dir = join(self.VAR_CACHE, 'www', codeVersionId)
        if exists(target_dir):
            rmtree(target_dir)

        if filetype == 'git':
            subdir = str(self.SERVICE_ID)
            self.logger.debug("git_enable_revision('%s', '%s', '%s', '%s')" %
                    (target_dir, source, revision, subdir))
            git.git_enable_revision(target_dir, source, revision, subdir)
        else:
            source.extractall(target_dir)

        # Fix session handlers
        self.fix_session_handlers(target_dir)

        return HttpJsonResponse()

    @expose('GET')
    def getTomcatState(self, kwargs):
        """GET state of Tomcat6"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.tomcat_lock:
            return self._get(kwargs, self.tomcat_file, role.Tomcat6)

    @expose('POST')
    def createTomcat(self, kwargs):
        """Create Tomcat6"""
        orig_kwargs = copy.copy(kwargs)
        exp_params = [('tomcat_port', is_pos_int)]
        try:
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.tomcat_lock:
            return self._create(orig_kwargs, self.tomcat_file, role.Tomcat6)

    @expose('POST')
    def stopTomcat(self, kwargs):
        """KILL Tomcat6"""
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        with self.tomcat_lock:
            return self._stop(kwargs, self.tomcat_file, role.Tomcat6)

    @expose('UPLOAD')
    def updateTomcatCode(self, kwargs):
        valid_filetypes = [ 'zip', 'tar', 'git' ]
        exp_params = [('filetype', is_in_list(valid_filetypes)),
                      ('codeVersionId', is_string),
                      ('file', is_uploaded_file, None),
                      ('revision', is_string, '')]
        try:
            filetype, codeVersionId, file, revision = check_arguments(exp_params, kwargs)
            if filetype != 'git' and not file:
                raise Exception("The '%s' filetype requires an uploaded file" % filetype)
            elif filetype == 'git' and not revision:
                raise Exception("The 'git' filetype requires the 'revision' parameter")
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if filetype == 'zip':
            source = zipfile.ZipFile(file.file, 'r')
        elif filetype == 'tar':
            source = tarfile.open(fileobj=file.file)
        elif filetype == 'git':
            source = git.DEFAULT_CODE_REPO

        target_dir = join(self.VAR_CACHE, 'tomcat_instance', 'webapps', codeVersionId)
        if exists(target_dir):
            rmtree(target_dir)

        if filetype == 'git':
            subdir = str(self.SERVICE_ID)
            self.logger.debug("git_enable_revision('%s', '%s', '%s', '%s')" %
                    (target_dir, source, revision, subdir))
            git.git_enable_revision(target_dir, source, revision, subdir)
        else:
            source.extractall(target_dir)

        return HttpJsonResponse()

# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread
from xml.dom import minidom
from tempfile import mkdtemp
from shutil import rmtree
import zipfile
import tempfile
import stat
import os.path

from conpaas.services.webservers.manager.config import CodeVersion, JavaServiceConfiguration
from conpaas.services.webservers.agent import client
from conpaas.services.webservers.misc import archive_open, archive_get_members
from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse

from . import BasicWebserversManager, ManagerException
from conpaas.core.expose import expose
from conpaas.core import git

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file


class JavaManager(BasicWebserversManager):

    def __init__(self, config_parser, **kwargs):
        BasicWebserversManager.__init__(self, config_parser)
        if kwargs['reset_config']:
            self._create_initial_configuration()

    def _update_code(self, config, nodes):
        for serviceNode in nodes:
            # Push the current code version via GIT if necessary
            if config.codeVersions[config.currentCodeVersion].type == 'git':
                filepath = config.codeVersions[config.currentCodeVersion].filename
                _, err = git.git_push(git.DEFAULT_CODE_REPO, serviceNode.ip)
                if err:
                    self.logger.debug('git-push to %s: %s' % (serviceNode.ip, err))
            else:
                filepath = os.path.join(self.code_repo, config.currentCodeVersion)

            try:
                # UPLOAD TOMCAT CODE TO TOMCAT
                if serviceNode.isRunningBackend:
                    client.updateTomcatCode(
                        serviceNode.ip, 5555, config.currentCodeVersion,
                        config.codeVersions[config.currentCodeVersion].type,
                        filepath)
                if serviceNode.isRunningProxy or serviceNode.isRunningWeb:
                    client.updatePHPCode(
                        serviceNode.ip, 5555, config.currentCodeVersion,
                        config.codeVersions[config.currentCodeVersion].type,
                        filepath)
            except client.AgentException:
                self.logger.exception('Failed to update code at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to update code at node %s' % str(serviceNode))
                return

    def _start_proxy(self, config, nodes):
        kwargs = {
            'web_list': config.getWebTuples(),
            'tomcat_list': config.getBackendTuples(),
            'tomcat_servlets': self._get_servlet_urls(config.currentCodeVersion),
        }

        for proxyNode in nodes:
            try:
                if config.currentCodeVersion is not None:
                    client.createHttpProxy(proxyNode.ip, 5555,
                                           config.proxy_config.port,
                                           config.currentCodeVersion,
                                           **kwargs)
            except client.AgentException:
                self.logger.exception('Failed to start proxy at node %s' % str(proxyNode))
                self.state_set(self.S_ERROR, msg='Failed to start proxy at node %s' % str(proxyNode))
                raise

    def _update_proxy(self, config, nodes):
        kwargs = {
            'web_list': config.getWebTuples(),
            'tomcat_list': config.getBackendTuples(),
            'tomcat_servlets': self._get_servlet_urls(config.currentCodeVersion),
        }

        for proxyNode in nodes:
            try:
                if config.currentCodeVersion is not None:
                    client.updateHttpProxy(proxyNode.ip, 5555,
                                           config.proxy_config.port,
                                           config.currentCodeVersion,
                                           **kwargs)
            except client.AgentException:
                self.logger.exception('Failed to update proxy at node %s' % str(proxyNode))
                self.state_set(self.S_ERROR, msg='Failed to update proxy at node %s' % str(proxyNode))
                raise

    def _start_backend(self, config, nodes):
        for serviceNode in nodes:
            try:
                client.createTomcat(serviceNode.ip, 5555, config.backend_config.port)
            except client.AgentException:
                self.logger.exception('Failed to start Tomcat at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to start Tomcat at node %s' % str(serviceNode))
                raise

    def _stop_backend(self, config, nodes):
        for serviceNode in nodes:
            try:
                client.stopTomcat(serviceNode.ip, 5555)
            except client.AgentException:
                self.logger.exception('Failed to stop Tomcat at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to stop Tomcat at node %s' % str(serviceNode))
                raise

    @expose('GET')
    def get_service_info(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'state': self.state_get(), 'type': 'JAVA'})

    @expose('GET')
    def get_configuration(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        config = self._configuration_get()
        return HttpJsonResponse({'codeVersionId': config.currentCodeVersion})

    @expose('POST')
    def update_java_configuration(self, kwargs):
        config = self._configuration_get()
        exp_params = [('codeVersionId', is_in_list(config.codeVersions))]
        try:
            codeVersionId = check_arguments(exp_params, kwargs)
            self.check_state([self.S_INIT, self.S_STOPPED, self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        state = self.state_get()
        if state == self.S_INIT or state == self.S_STOPPED:
            if codeVersionId:
                config.currentCodeVersion = codeVersionId
            self._configuration_set(config)
        elif state == self.S_RUNNING:
            self.state_set(self.S_ADAPTING, msg='Updating configuration')
            Thread(target=self.do_update_configuration, args=[config, codeVersionId]).start()

        return HttpJsonResponse()

    def _get_servlet_urls_from_webxml(self, webxml_filename):
        ret = []
        doc = minidom.parse(webxml_filename)
        mappers = doc.getElementsByTagName('servlet-mapping')
        for m in mappers:
            url = m.getElementsByTagName('url-pattern')[0].firstChild.wholeText
            ret.append(url)
        return ret

    def _get_servlet_urls(self, codeVersionId):
        ret = []
        archname = os.path.join(self.code_repo, codeVersionId)

        if os.path.isfile(archname):
            # File-based code upload
            arch = archive_open(archname)
            filelist = archive_get_members(arch)
            if 'WEB-INF/web.xml' in filelist:
                tmp_dir = mkdtemp()
                arch.extract('WEB-INF/web.xml', path=tmp_dir)
                ret = self._get_servlet_urls_from_webxml(os.path.join(tmp_dir, 'WEB-INF', 'web.xml'))
                rmtree(tmp_dir, ignore_errors=True)

            return ret

        # git-based code upload
        webxml_filename = os.path.join(archname, 'WEB-INF', 'web.xml')
        if os.path.isfile(webxml_filename):
            ret = self._get_servlet_urls_from_webxml(webxml_filename)

        return ret

    def do_update_configuration(self, config, codeVersionId):
        if codeVersionId is not None:
            config.prevCodeVersion = config.currentCodeVersion
            config.currentCodeVersion = codeVersionId
            self._update_code(config, config.serviceNodes.values())
            self._update_web(config, config.getWebServiceNodes())
            self._update_proxy(config, config.getProxyServiceNodes())

        self.state_set(self.S_RUNNING)
        self._configuration_set(config)

    def _create_initial_configuration(self):
        config = JavaServiceConfiguration()
        config.backend_count = 0
        config.web_count = 0
        config.proxy_count = 1

        if not os.path.exists(self.code_repo):
            os.makedirs(self.code_repo)

        fileno, path = tempfile.mkstemp()
        fd = os.fdopen(fileno, 'w')
        fd.write('''<html>
  <head>
  <title>Welcome to ConPaaS!</title>
  </head>
  <body bgcolor="white" text="black">
  <center><h1>Welcome to ConPaaS!</h1></center>
  </body>
  </html>''')
        fd.close()
        os.chmod(path, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)

        if len(config.codeVersions) > 0:
            return
        zfile = zipfile.ZipFile(os.path.join(self.code_repo, 'code-default'), mode='w')
        zfile.write(path, 'index.html')
        zfile.close()
        os.remove(path)
        config.codeVersions['code-default'] = CodeVersion('code-default', 'code-default.war', 'zip', description='Initial version')
        config.currentCodeVersion = 'code-default'
        self._configuration_set(config)

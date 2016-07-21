# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread
import re
import tarfile
import tempfile
import stat
import os.path

from conpaas.services.webservers.manager.config import CodeVersion, PHPServiceConfiguration
from conpaas.services.webservers.agent import client
from conpaas.core.https.server import HttpErrorResponse, HttpJsonResponse
from . import BasicWebserversManager, ManagerException
from conpaas.core.expose import expose

from conpaas.core import git

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

# try:
#     from conpaas.services.webservers.manager.autoscaling.scaler import ProvisioningManager
# except ImportError as ex:
#     provision_mng_error = "%s" % ex
ProvisioningManager = None

from multiprocessing.pool import ThreadPool


class PHPManager(BasicWebserversManager):

    def __init__(self, config_parser, **kwargs):
        BasicWebserversManager.__init__(self, config_parser)
        if kwargs['reset_config']:
            self._create_initial_configuration()

        if ProvisioningManager is None:
            # self.logger.info('Provisioning Manager can not be initialized: %s' % provision_mng_error)
            self.scaler = None
        else:
            try:
                self.scaler = ProvisioningManager(config_parser)
            except Exception as ex:
                self.logger.exception('Failed to initialize the Provisioning Manager %s' % str(ex))

    def _render_scalaris_node(self, node, role):
        ip = node.ip.replace('.', ',')
        return '{{' + ip + '},14195,' + role + '}'

    def _render_scalaris_hosts(self, nodes):
        rendered_nodes = [self._render_scalaris_node(node, 'service_per_vm') for node in nodes]
        return '[' + ', '.join(rendered_nodes) + ']'

    def _start_scalaris(self, config, nodes, first_start):
        known_hosts = self._render_scalaris_hosts(config.serviceNodes.values())
        for serviceNode in nodes:
            try:
                client.createScalaris(serviceNode.ip, 5555, first_start, known_hosts)
                first_start = False
            except client.AgentException:
                self.logger.exception('Failed to start Scalaris at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to start Scalaris at node %s' % str(serviceNode))
                raise

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
                client.updatePHPCode(serviceNode.ip, 5555, config.currentCodeVersion,
                                     config.codeVersions[config.currentCodeVersion].type,
                                     filepath)
            except client.AgentException:
                self.logger.exception('Failed to update code at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to update code at node %s' % str(serviceNode))
                raise

    def _start_proxy(self, config, nodes):
        kwargs = {
            'web_list': config.getWebTuples(),
            'fpm_list': config.getBackendTuples(),
            'cdn': config.cdn,
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
            'fpm_list': config.getBackendTuples(),
            'cdn': config.cdn
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
                client.createPHP(serviceNode.ip, 5555, config.backend_config.port,
                                 config.backend_config.scalaris, config.backend_config.php_conf.conf)
            except client.AgentException:
                self.logger.exception('Failed to start php at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to start php at node %s' % str(serviceNode))
                raise

    def _update_backend(self, config, nodes):
        for serviceNode in nodes:
            try:
                client.updatePHP(serviceNode.ip, 5555, config.backend_config.port,
                                 config.backend_config.scalaris, config.backend_config.php_conf.conf)
            except client.AgentException:
                self.logger.exception('Failed to update php at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to update php at node %s' % str(serviceNode))
                raise

    def _stop_backend(self, config, nodes):
        for serviceNode in nodes:
            try:
                client.stopPHP(serviceNode.ip, 5555)
            except client.AgentException:
                self.logger.exception('Failed to stop php at node %s' % str(serviceNode))
                self.state_set(self.S_ERROR, msg='Failed to stop php at node %s' % str(serviceNode))
                raise

    @expose('GET')
    def get_service_info(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'state': self.state_get(), 'type': 'PHP'})

    @expose('GET')
    def get_configuration(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        config = self._configuration_get()
        phpconf = {}
        for key in config.backend_config.php_conf.defaults:
            if key in config.backend_config.php_conf.conf:
                phpconf[key] = config.backend_config.php_conf.conf[key]
            else:
                phpconf[key] = config.backend_config.php_conf.defaults[key]

        return HttpJsonResponse({
            'codeVersionId': config.currentCodeVersion,
            'phpconf': phpconf,
            'cdn': config.cdn,
            'autoscaling': config.autoscaling,
        })

    @expose('POST')
    def on_autoscaling(self, kwargs):
        """
        Enable auto-scaling for this PHP service.
        The auto-scaling will add or remove nodes to reach the expected response
        time in milliseconds while keeping a low credit usage.

        POST parameters
        ---------------
        cool_down : int
            time in minutes between adaptation points
        reponse_time : int
            service level objective (SLO) for the web and backend response time in milliseconds
        strategy : string
            one of "low", "medium_down", "medium_up", "medium", "high"
        """
        self.logger.info('on_autoscaling entering')
        try:
            valid_strategy = [ 'low', 'medium_down', 'medium_up', 'medium', 'high' ]
            exp_params = [('cool_down', is_pos_nul_int),
                          ('reponse_time', is_pos_nul_int),
                          ('strategy', is_in_list(valid_strategy))]
            cool_down, reponse_time, strategy = check_arguments(exp_params, kwargs)

            if not self.scaler:
                raise Exception(
                    'Provisioning Manager has not been initialized: %s' %
                    provision_mng_error)

            self.autoscaling_threads = ThreadPool(processes=1)
            self.autoscaling_threads.apply_async(self.scaler.do_provisioning, (response_time, cool_down, strategy))
            config = self._configuration_get()
            config.autoscaling = True
            self._configuration_set(config)

            return HttpJsonResponse({'autoscaling': config.autoscaling})
        except Exception as ex:
            self.logger.critical('Error when trying to stop the autoscaling mechanism: %s' % ex)
            return HttpErrorResponse("%s" % ex)

    @expose('POST')
    def off_autoscaling(self, kwargs):
        self.logger.info('off_autoscaling entering')
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)

            if not self.scaler:
                raise Exception(
                    'Provisioning Manager has not been initialized: %s' %
                    provision_mng_error)

            self.autoscaling_threads.terminate()
            self.scaler.stop_provisioning()
            config = self._configuration_get()
            config.autoscaling = False
            self._configuration_set(config)

            self.logger.info('off_autoscaling done')
            return HttpJsonResponse({'autoscaling': config.autoscaling})
        except Exception as ex:
            self.logger.critical('Error when trying to stop the autoscaling mechanism: %s' % ex)
            return HttpErrorResponse("%s" % ex)

    @expose('POST')
    def update_php_configuration(self, kwargs):
        config = self._configuration_get()
        exp_params = [('codeVersionId', is_in_list(config.codeVersions), None),
                      ('phpconf', is_dict, {})]
        try:
            codeVersionId, phpconf = check_arguments(exp_params, kwargs)
            self.check_state([self.S_INIT, self.S_STOPPED, self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if codeVersionId is None and not phpconf:
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING,
                    'at least one of "codeVersionId" or "phpconf"').message)

        if phpconf:
            for key in phpconf.keys():
                if key not in config.backend_config.php_conf.defaults:
                    return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, 'phpconf attribute "%s"' % (str(key))).message)
                if not re.match(config.backend_config.php_conf.format[key], phpconf[key]):
                    return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID).message)

        state = self.state_get()
        if state == self.S_INIT or state == self.S_STOPPED:
            if codeVersionId:
                config.currentCodeVersion = codeVersionId
            for key in phpconf:
                config.backend_config.php_conf.conf[key] = phpconf[key]
            self._configuration_set(config)
        elif state == self.S_RUNNING:
            self.state_set(self.S_ADAPTING, msg='Updating configuration')
            Thread(target=self.do_update_configuration, args=[config, codeVersionId, phpconf]).start()

        return HttpJsonResponse()

    def do_update_configuration(self, config, codeVersionId, phpconf):
        if phpconf:
            for key in phpconf:
                config.backend_config.php_conf.conf[key] = phpconf[key]
            self._update_backend(config, config.getBackendServiceNodes())
        if codeVersionId is not None:
            self.prevCodeVersion = config.currentCodeVersion
            config.currentCodeVersion = codeVersionId
            self._update_code(config, config.serviceNodes.values())
            self._update_web(config, config.getWebServiceNodes())
            self._update_proxy(config, config.getProxyServiceNodes())
        self.state_set(self.S_RUNNING)
        self._configuration_set(config)

    def _create_initial_configuration(self):
        print 'CREATING INIT CONFIG'
        config = PHPServiceConfiguration()
        config.backend_count = 0
        config.web_count = 0
        config.proxy_count = 1
        config.cdn = False
        config.autoscaling = False

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
        tfile = tarfile.TarFile(name=os.path.join(self.code_repo, 'code-default'), mode='w')
        tfile.add(path, 'index.html')
        tfile.close()
        os.remove(path)
        config.codeVersions['code-default'] = CodeVersion('code-default', 'code-default.tar', 'tar', description='Initial version')
        config.currentCodeVersion = 'code-default'
        self._configuration_set(config)

    @expose('POST')
    def cdn_enable(self, kwargs):
        '''
        Enable/disable CDN offloading.
        The changes must be reflected on the load balancer a.k.a proxy
        '''
        try:
            exp_params = [('enable', is_bool),
                          ('address', is_string, False)]
            enable, cdn = check_arguments(exp_params, kwargs)

            if enable:
                self.logger.info('Enabling CDN hosted at "%s"' % (cdn))
            else:
                self.logger.info('Disabling CDN')

            config = self._configuration_get()
            config.cdn = cdn
            self._update_proxy(config, config.getProxyServiceNodes())
            self._configuration_set(config)
            return HttpJsonResponse({'cdn': config.cdn})
        except Exception as ex:
            self.logger.exception(ex)
            return HttpErrorResponse("%s" % ex)

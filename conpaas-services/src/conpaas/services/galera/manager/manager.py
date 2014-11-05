# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from threading import Thread, Timer
import os
import tempfile
import string
from random import choice
import collections

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse, FileUploadField
from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager, ManagerException
from conpaas.core.misc import check_arguments, is_pos_nul_int, is_string, is_list_dict2, is_uploaded_file
from conpaas.core.misc import run_cmd_code

import conpaas.services.galera.agent.client as agent
from conpaas.services.galera.agent.client import AgentException
from conpaas.services.galera.manager.config import Configuration

import logging
import commands
import MySQLdb
class GaleraManager(BaseManager):

    # MySQL Galera node types
    REGULAR_NODE = 'node'  # regular node running a mysqld daemon
    GLB_NODE = 'glb_node'  # load balancer running a glbd daemon
    volumes_dict={}
    def __init__(self, conf, **kwargs):
        BaseManager.__init__(self, conf)

        self.logger.debug("Entering GaleraServerManager initialization")
        self.controller.generate_context('galera')
        self.controller.config_clouds({"mem": "512", "cpu": "1"})
        self.state = self.S_INIT
        self.config = Configuration(conf)
        self.logger.debug("Leaving GaleraServer initialization")

    @expose('POST')
    def startup(self, kwargs):
        """
        Starts this MySQL Galera service.

        Parameters
        ----------
        cloud : string
            (optional)
            name of cloud to start the service's manager
            (select the default cloud by default).

        Returns a dict with the single key 'state' with the new service state.
        """
	self.logger.debug('try to startup service' )
        try:
            self._check_state([self.S_INIT, self.S_STOPPED])
            exp_params = [('cloud', is_string, None)]
            cloud = check_arguments(exp_params, kwargs)
            start_cloud = self._init_cloud(cloud)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.state = self.S_PROLOGUE
        Thread(target=self._do_startup, args=(start_cloud, )).start()
        return HttpJsonResponse({'state': self.state})

    def _do_startup(self, start_cloud):
        """ Starts up the galera service. """

        #TODO: Get any existing configuration (if the service was stopped and restarted)
        self.logger.debug('do_startup: Going to request one new node')

        # Generate a password for root
        # TODO: send a username?
        self.root_pass = ''.join([choice(string.letters + string.digits) for i in range(10)])
        self.controller.add_context_replacement(dict(mysql_username='mysqldb',
                                                     mysql_password=self.root_pass),
                                                cloud=start_cloud)
        try:
            node_instances = self.controller.create_nodes(1,
                                                          agent.check_agent_process,
                                                          self.config.AGENT_PORT,
                                                          start_cloud)
            # We need to create a new volume.
            #volume_name = "galera-%s" % node_instances[0].ip
	    #node_id=node_instances[0].id.replace("iaas", "")
	    #self.logger.debug("Node_id=%s" % node_id)
            #volume = self.create_volume(1024, volume_name,node_id, cloud=start_cloud)
	    #self.attach_volume(volume.id, node_id)
	    self._start_mysqld(node_instances)
            self.config.addMySQLServiceNodes(node_instances)
        except Exception, ex:
            # rollback
            self.controller.delete_nodes(node_instances)
            self.logger.exception('do_startup: Failed to request a new node on cloud %s: %s.' % (start_cloud.get_cloud_name(), ex))
            self.state = self.S_STOPPED
            return
        self.state = self.S_RUNNING

    def _start_mysqld(self, nodes):
        dev_name = None
        existing_nodes = self.config.get_nodes_addr()
        for serviceNode in nodes:
	    try: 
		# We try to create a new volume.
            	volume_name = "mysql-%s" % serviceNode.ip
            	node_id=serviceNode.id.replace("iaas", "")
	        self.logger.debug("trying to create a volume for the node_id=%s" % node_id)
        	volume = self.create_volume(1024, volume_name,node_id)
            except AgentException, ex:
                self.logger.exception('Failed creating volume   %s: %s' % (volume_name, ex))
                raise
            try:
		_, dev_name = self.attach_volume(volume.id, node_id)
		self.volumes_dict[serviceNode.ip]=volume.id
            except AgentException, ex:
                self.logger.exception('Failed to attaching disk to Galera node %s: %s' % (str(serviceNode), ex))
                raise
            try:
                agent.start_mysqld(serviceNode.ip, self.config.AGENT_PORT, existing_nodes, dev_name)
            except AgentException, ex:
                self.logger.exception('Failed to start Galera node %s: %s' % (str(serviceNode), ex))
                raise
        try:
            glb_nodes = self.config.get_glb_nodes()
	    self.logger.debug('Galera node already active: %s' % glb_nodes) 
            nodesIp=[]
	    nodesIp = ["%s:%s" % (node.ip, self.config.MYSQL_PORT)  # FIXME: find real mysql port instead of default 3306
                         for node in nodes]
	    for glb in glb_nodes:
		agent.add_glbd_nodes(glb.ip, self.config.AGENT_PORT, nodesIp)
        except Exception as ex:
            self.logger.exception('Failed to configure GLB nodes with new Galera nodes: %s' % ex)
            raise

    def _start_glbd(self, new_glb_nodes):
        for new_glb in new_glb_nodes:
            try:
                nodes = ["%s:%s" % (node.ip, self.config.MYSQL_PORT)  # FIXME: find real mysql port instead of default 3306
                         for node in self.config.get_nodes()]
                self.logger.debug('create_glb_node all galera nodes = %s' % nodes)
                self.logger.debug('create_glb_node for new_glb.ip  = %s' % new_glb.ip)
                agent.start_glbd(new_glb.ip, self.config.AGENT_PORT, nodes)
            except AgentException:
                self.logger.exception('Failed to start Galera GLB Node at node %s' % new_glb.ip)
                raise

    @expose('GET')
    def list_nodes(self, kwargs):
        """
        List this MySQL Galera current agents.

        No parameters.

        Returns a dict with keys:
        nodes : list of regular node identifiers
        glb_nodes : lits of load balancing node identifiers
        """
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'nodes': [node.id for node in self.config.get_nodes()],
                                 'glb_nodes': [node.id for node in self.config.get_glb_nodes()],
                                 })

    @expose('GET')
    def get_node_info(self, kwargs):
        """
        Gets info of a specific node.

        Parameters
        ----------
        serviceNodeId : string
            identifier of node to query

        Returns a dict with keys:
        serviceNode : dict with keys:
            id : string
                node identifier
            ip : string
                node public IP address
            vmid : string
                unique identifier of the VM inside the cloud provider
            cloud :string
                name of cloud provider
        """
        try:
            exp_params = [('serviceNodeId', is_string)]
            serviceNodeId = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if serviceNodeId not in self.config.serviceNodes and serviceNodeId not in self.config.glb_service_nodes :
            return HttpErrorResponse('Unknown "serviceNodeId" %s, should be one of %s.'
                                     % (serviceNodeId, self.config.serviceNodes.keys()))
        serviceNode = self.config.getMySQLNode(serviceNodeId)
        return HttpJsonResponse({'serviceNode': {'id': serviceNode.id,
                                                 'ip': serviceNode.ip,
                                                 'vmid': serviceNode.vmid,
                                                 'cloud': serviceNode.cloud_name,
						 'isNode': serviceNode.isNode,
						 'isGlb_node': serviceNode.isGlb_node
                                                 }
                                 })

    @expose('POST')
    def add_nodes(self, kwargs):
        """
        Add new nodes for this MySQL Galera service.

        Parameters
        ----------
        nodes : int
            number of new regular nodes to add (default 0)
        glb_nodes : int
            number of new Galera Load Balancers nodes to add (default 0)
        cloud : string
            cloud name where to create nodes (default to default cloud)

        Returns an error if nodes + glb_nodes == 0.
        """
        try:
            self._check_state([self.S_RUNNING])
            exp_params = [('nodes', is_pos_nul_int, 0),
                          ('glb_nodes', is_pos_nul_int, 0),
                          ('cloud', is_string, None)]
            nodes, glb_nodes, cloud = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if nodes + glb_nodes <= 0:
            return HttpErrorResponse('Both arguments "nodes" and "glb_nodes" are null.')

        self.state = self.S_ADAPTING

        # TODO: check if argument "cloud" is an known cloud
        if nodes > 0:
            Thread(target=self._do_add_nodes, args=[self.REGULAR_NODE, nodes, cloud]).start()
	    #self._do_add_nodes(self.REGULAR_NODE, nodes, cloud)
        if glb_nodes > 0:
            Thread(target=self._do_add_nodes, args=[self.GLB_NODE, glb_nodes, cloud]).start()
	    #self._do_add_nodes(self.GLB_NODE, glb_nodes, cloud)
        return HttpJsonResponse()

    def _do_add_nodes(self, node_type, count, cloud=None):
        try:
            start_cloud = self._init_cloud(cloud)
            self.controller.add_context_replacement(dict(mysql_username='mysqldb',
                                                         mysql_password=self.root_pass),
                                                    cloud=start_cloud)
            node_instances = self.controller.create_nodes(count,
                                                          agent.check_agent_process,
                                                          self.config.AGENT_PORT,
                                                          start_cloud)
	    if node_type == self.REGULAR_NODE:
		self._start_mysqld(node_instances)
		self.config.addMySQLServiceNodes(node_instances)
            elif node_type == self.GLB_NODE:
                self._start_glbd(node_instances)
                self.config.addGLBServiceNodes(node_instances)
        except Exception, ex:
            # rollback
            for node in node_instances:
                agent.stop(node.ip, self.config.AGENT_PORT)
            self.controller.delete_nodes(node_instances)
            self.logger.exception('Could not add nodes: %s' % ex)
        self.state = self.S_RUNNING

    @expose('GET')
    def getMeanLoad(self, kwargs):
        """
        TODO: placeholder for obtaining performance metrics.

        No parameters.

        Returns a dict with keys:
            'loads': float array, wsrep_local_recv_queue_avg of each node
            'meanLoad':float, average load of wsrep_local_recv_queue_avg galera variable across the nodes
            'updates': float, array within the  number of update queries across the nodes
            'meanUpdate' : average number of update queries across the nodes
            'selects': int array, array within the  number of select queries across the nodes
            'meanSelect': float, average number of select queries across the nodes
            'deletes' : int array,array within the  number of delete queries across the nodes
            'meanDelete' : float, average number of delete queries across the nodes
            'inserts': int array, array within the  number of insert queries across the nodes
            'meanInsert': float average number of insert  queries across the nodes
        """
        nodes = self.config.get_nodes()
	loads=[]
	load=0.0
	updates=[]
	update=0.0
	selects=[]
	select=0
	deletes=[]
	delete=0
	inserts=[]
	insert=0
	for node in nodes:
		db = MySQLdb.connect(node.ip, 'mysqldb', self.root_pass)
        	exc = db.cursor()
       		exc.execute("SHOW STATUS LIKE 'wsrep_local_recv_queue_avg';")
        	localLoad=exc.fetchone()[1]
		loads.append(localLoad)
		load=load+float(localLoad)
		#select
		exc.execute("SHOW GLOBAL STATUS LIKE 'Com_select';")
                localSelect=exc.fetchone()[1]
                selects.append(localSelect)
                select=select+float(localSelect)
                #insert
                exc.execute("SHOW GLOBAL STATUS LIKE 'Com_insert';")
                localInsert=exc.fetchone()[1]
                inserts.append(localInsert)
                insert=insert+float(localInsert)
                #delete
                exc.execute("SHOW GLOBAL STATUS LIKE 'Com_delete';")
                localDelete=exc.fetchone()[1]
                deletes.append(localDelete)
                delete=delete+float(localDelete)
                #update
                exc.execute("SHOW GLOBAL STATUS LIKE 'Com_update';")
                localUpdate=exc.fetchone()[1]
                updates.append(localUpdate)
                update=update+float(localUpdate)
	if len(nodes)!=0 :
		l=len(nodes)
	else:
		l=1
	meanLoad=load/l
	meanSelect=select/l
	meanUpdate=update/l
	meanDelete=delete/l
	meanInsert=insert/l
	return HttpJsonResponse({
                                 'loads': loads,
                                 'meanLoad': meanLoad,
				 'updates': updates,
				 'meanUpdate' : meanUpdate,
				 'selects': selects,
				 'meanSelect': meanSelect,
				 'deletes' : deletes,
				 'meanDelete' : meanDelete,
				 'inserts': inserts,
				 'meanInsert': meanInsert
                                 })

    @expose('GET')
    def getGangliaParams(self, kwargs):
        """
        TODO: it allows to obtain Monitoring info from Ganglia.

        No parameters.

        Returns a dict with keys:
            Ganglia : xml
        """

        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
	    import commands
	    xml=commands.getstatusoutput("curl -s telnet://localhost:8651/")
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        return HttpJsonResponse({
                                 'Ganglia': xml
                                 })

    @expose('GET')
    def get_service_performance(self, kwargs):
        """
        TODO: placeholder for obtaining performance metrics.

        No parameters.

        Returns a dict with keys:
            request_rate : int
            error_rate : int
            throughput : int
            response_time : int
        """

        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
	return HttpJsonResponse({
				 'request_rate': 0,
                                 'error_rate': 0,
                                 'throughput': 0,
                                 'response_time': 0,
                                 })

    @expose('POST')
    def remove_nodes(self, kwargs):
        """
        Remove MySQL Galera nodes.

        Parameters
        ----------
        nodes : int
            number of regular nodes to remove (default 0)
        glb_nodes : int
            number of Galera Load Balancer nodes to remove (default 0)

        Returns an error if "nodes + glb_nodes == 0".
        """
        try:
            self._check_state([self.S_RUNNING])
            exp_params = [('nodes', is_pos_nul_int, 0),
                          ('glb_nodes', is_pos_nul_int, 0)]
            nodes, glb_nodes = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        if nodes + glb_nodes <= 0:
            return HttpErrorResponse('Both arguments "nodes" and "glb_nodes" are null.')
        total_nodes = len(self.config.get_nodes())
        if nodes > 0 and nodes > total_nodes:
            return HttpErrorResponse('Cannot remove %s nodes: %s nodes at most.'
                                     % (nodes, total_nodes))
        total_glb_nodes = len(self.config.get_glb_nodes())
        if glb_nodes > 0 and glb_nodes > total_glb_nodes:
            return HttpErrorResponse('Cannot remove %s nodes: %s nodes at most.'
                                     % (glb_nodes, total_glb_nodes))
        self.state = self.S_ADAPTING
        rm_reg_nodes = self.config.get_nodes()[:nodes]
        rm_glb_nodes = self.config.get_glb_nodes()[:glb_nodes]
        Thread(target=self._do_remove_nodes, args=[rm_reg_nodes,rm_glb_nodes]).start()
        return HttpJsonResponse()

    def _do_remove_nodes(self,rm_reg_nodes,rm_glb_nodes):
	glb_nodes = self.config.get_glb_nodes()
        nodesIp = ["%s:%s" % (node.ip, self.config.MYSQL_PORT)  # FIXME: find real mysql port instead of default 3306
                         for node in rm_reg_nodes]
        for glb in glb_nodes:
                agent.remove_glbd_nodes(glb.ip, self.config.AGENT_PORT, nodesIp)
	nodes = rm_reg_nodes + rm_glb_nodes
	for node in nodes:
            agent.stop(node.ip, self.config.AGENT_PORT)
        for node in rm_reg_nodes:
	    volume_id=self.volumes_dict[node.ip]
	    self.detach_volume(volume_id)
	    self.destroy_volume(volume_id)
        self.controller.delete_nodes(nodes)
        self.config.remove_nodes(nodes)
	if (len(self.config.get_nodes()) +len(self.config.get_glb_nodes())==0 ):
		self.state=self.S_STOPPED
	else :
        	self.state = self.S_RUNNING

    @expose('POST')
    def migrate_nodes(self, kwargs):
        """
        Migrate nodes from one cloud to another.

        Parameters
        ----------
        nodes : list of dict with keys
            from_cloud : string
                name of origin cloud
            vmid : string
                identifier of the node to migrate inside the origin cloud
            to_cloud : string
                name of destination cloud

         delay : int
             (optional with default value to 0) time in seconds to delay
             the removal of the old node. 0 means "remove old node as
             soon as the new node is up", 60 means "remove old node
             after 60 seconds after the new node is up". Useful to keep
             the old node active while the DNS and its caches that
             still have the IP address of the old node are updated
             to the IP address of the new node.
        """
        try:
            self._check_state([self.S_RUNNING])
            exp_keys = ['from_cloud', 'vmid', 'to_cloud']
            exp_params = [('nodes', is_list_dict2(exp_keys)),
                          ('delay', is_pos_nul_int, 0)]
            nodes, delay = check_arguments(exp_params, kwargs)
        except Exception, ex:
            return HttpErrorResponse('%s' % ex)

        service_nodes = self.config.get_nodes()
        self.logger.debug("While migrate_nodes, service_nodes = %s." % service_nodes)
        migration_plan = []
        for migr in nodes:
            from_cloud_name = migr['from_cloud']
            node_id = migr['vmid']
            dest_cloud_name = migr['to_cloud']
            if from_cloud_name == '' or dest_cloud_name == '':
                return HttpErrorResponse('Missing cloud name in parameter "nodes": from_cloud="%s" to_cloud="%s"'
                                         % (from_cloud_name, dest_cloud_name))
            try:
                candidate_nodes = [node for node in service_nodes
                                   if node.cloud_name == from_cloud_name
                                   and node.vmid == node_id]
                if candidate_nodes == []:
                    avail_nodes = ', '.join([node.cloud_name + ':' + node.vmid
                                             for node in service_nodes])
                    raise Exception("Node %s in cloud %s is not a valid node"
                                    " of this service. It should be one of %s"
                                    % (node_id, from_cloud_name, avail_nodes))
                node = candidate_nodes[0]
                dest_cloud = self.controller.get_cloud_by_name(dest_cloud_name)
            except Exception, ex:
                return HttpErrorResponse("%s" % ex)
            migration_plan.append((node, dest_cloud))

        if migration_plan == []:
            return HttpErrorResponse('ERROR: argument is missing the nodes to migrate.')

        self.state = self.S_ADAPTING
        Thread(target=self._do_migrate_nodes, args=[migration_plan, delay]).start()
        return HttpJsonResponse()

    def _do_migrate_nodes(self, migration_plan, delay):
        self.logger.info("Migration: starting with plan %s and delay %s."
                         % (migration_plan, delay))
        # TODO: use instead collections.Counter with Python 2.7
        clouds = [dest_cloud for (_node, dest_cloud) in migration_plan]
        new_vm_nb = collections.defaultdict(int)
        for cloud in clouds:
            new_vm_nb[cloud] += 1
        try:
            new_nodes = []
            # TODO: make it parallel
            for cloud, count in new_vm_nb.iteritems():
                self.controller.add_context_replacement(dict(mysql_username='mysqldb',
                                                             mysql_password=self.root_pass),
                                                        cloud=cloud)

                new_nodes.extend(self.controller.create_nodes(count,
                                                              agent.check_agent_process,
                                                              self.config.AGENT_PORT,
                                                              cloud))
                self._start_mysqld(new_nodes)
                self.config.addMySQLServiceNodes(new_nodes)
        except Exception, ex:
            # error happened: rolling back...
            for node in new_nodes:
                agent.stop(node.ip, self.config.AGENT_PORT)
            self.controller.delete_nodes(new_nodes)
            self.config.remove_nodes(new_nodes)
            self.logger.exception('_do_migrate_nodes: Could not'
                                  ' start nodes: %s' % ex)
            self.state = self.S_RUNNING
            raise ex

        self.logger.debug("Migration: new nodes %s created and"
                          " configured successfully." % (new_nodes))

        # New nodes successfully created
        # Now scheduling the removing of old nodes
        old_nodes = [node for node, _dest_cloud in migration_plan]
        if delay == 0:
            self.logger.debug("Migration: removing immediately"
                              " the old nodes: %s." % old_nodes)
            self._do_migrate_finalize(old_nodes)
        else:
            self.logger.debug("Migration: setting a timer to remove"
                              " the old nodes %s after %d seconds."
                              % (old_nodes, delay))
            self._start_timer(delay, self._do_migrate_finalize, old_nodes)
            self.state = self.S_RUNNING

    def _do_migrate_finalize(self, old_nodes):
        self.state = self.S_ADAPTING
        for node in old_nodes:
            agent.stop(node.ip, self.config.AGENT_PORT)
        self.controller.delete_nodes(old_nodes)
        self.config.remove_nodes(old_nodes)
        self.state = self.S_RUNNING
        self.logger.info("Migration: old nodes %s have been removed."
                         " END of migration." % old_nodes)

    def _start_timer(self, delay, callback, nodes):
        timer = Timer(delay, callback, args=[nodes])
        timer.start()

    @expose('GET')
    def get_service_info(self, kwargs):
        """
        Get service information.

        No parameters.

        Returns a dict with key 'state' containing the service current state,
        and key 'type' containing this service type.
        """
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        return HttpJsonResponse({'state': self.state, 'type': 'galera'})

    @expose('POST')
    def shutdown(self, kwargs):
        """
        Stop the service.

        No parameters.

        Returns a dict with a key 'state' containing the new service state.
        """
        try:
            self._check_state([self.S_RUNNING])
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        self.state = self.S_EPILOGUE
        Thread(target=self._do_shutdown, args=[]).start()
        return HttpJsonResponse({'state': self.state})

    def _do_shutdown(self):
        ''' Shuts down the service. '''
        self._do_remove_nodes(self.config.serviceNodes.values(),self.config.glb_service_nodes.values())
        self.config.serviceNodes = {}
	#self._do_remove_nodes(self.config.glb_service_nodes.values())
	self.config.glb_service_nodes = {}
        self.state = self.S_STOPPED

    @expose('POST')
    def set_password(self, kwargs):
        self.logger.debug('Setting password')
        try:
            self._check_state([self.S_RUNNING])
            exp_params = [('user', is_string),
                          ('password', is_string)]
            user, password = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("Cannot set new password: %s." % ex)

        one_node = self.config.get_nodes()[0]

        try:
            agent.set_password(one_node.ip, self.config.AGENT_PORT, user, password)
            self.root_pass = password
        except Exception as ex:
            self.logger.exception()
            return HttpErrorResponse('Failed to set new password: %s.' % ex)
        else:
            return HttpJsonResponse()

    @expose('UPLOAD')
    def load_dump(self, kwargs):
        """
        Load a dump into the database.

        Parameters
        ----------
        mysqldump_file : uploaded file
            name of uploaded file containing the database dump.
        """
        self.logger.debug('Uploading mysql dump')
        try:
            self._check_state([self.S_RUNNING])
            exp_params = [('mysqldump_file', is_uploaded_file)]
            mysqldump_file = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        fd, filename = tempfile.mkstemp(dir='/tmp')
        fd = os.fdopen(fd, 'w')
        upload = mysqldump_file.file
        bytes = upload.read(2048)
        while len(bytes) != 0:
            fd.write(bytes)
            bytes = upload.read(2048)
        fd.close()

        # at least one agent since state is S_RUNNING
        one_node = self.config.get_nodes()[0]
        try:
            agent.load_dump(one_node.ip, self.config.AGENT_PORT, filename)
        except Exception as ex:
            err_msg = 'Could not upload mysqldump_file: %s.' % ex
            self.logger.exception(err_msg)
            return HttpErrorResponse(err_msg)
        return HttpJsonResponse()

    @expose('GET')
    def sqldump(self, kwargs):
        """
        Dump the database.

        No parameters.

        Returns the dump of the database.
        """
        try:
            self._check_state([self.S_RUNNING])
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        # at least one agent since state is S_RUNNING
        one_node = self.config.get_nodes()[0]
        # adding option '--skip-lock-tables' to avoid issue
        #  mysqldump: Got error: 1142: SELECT,LOCK TABL command denied to user
        #   'mysqldb'@'10.158.0.28' for table 'cond_instances'
        #   when using LOCK TABLES
        # FIXME: is it MySQL 5.1 only? does it still occur with MySQL 5.5?
        cmd = 'mysqldump -u mysqldb -h %s --password=%s -A --skip-lock-tables' \
              % (one_node.ip, self.root_pass)
        out, error, return_code = run_cmd_code(cmd)

        if return_code == 0:
            return HttpJsonResponse(out)
        else:
            return HttpErrorResponse("Failed to run mysqldump: %s." % error)




    @expose('GET')
    def remove_specific_nodes(self, kwargs):
        """
        Remove MySQL Galera nodes.

        Parameters
        ----------
        nodes : int
            number of regular nodes to remove (default 0)
        glb_nodes : int
            number of Galera Load Balancer nodes to remove (default 0)

        Returns an error if "nodes + glb_nodes == 0".
        """
	try:
            self._check_state([self.S_RUNNING])
            exp_params = [('ip', is_string)]
            ip = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        self.state = self.S_ADAPTING
        rm_reg_nodes = self.config.get_nodes()
        rm_glb_nodes = self.config.get_glb_nodes()
	is_in_glb=False
	is_in_reg=False
        for node in self.config.get_nodes():
            if node.ip == ip :
                nodeTarget=node
                is_in_reg=True
        for node in self.config.get_glb_nodes():
            if node.ip== ip :
                nodeTarget=node
                is_in_glb=True
        if is_in_reg==False and is_in_glb==False :
	    return HttpErrorResponse("%s" % "Sorry invalid ip !!!")
	elif is_in_reg == True :
            rm_reg_nodes=[nodeTarget]
            rm_glb_nodes=[]
        else :
            rm_glb_nodes=[nodeTarget]
            rm_reg_nodes=[]
        Thread(target=self._do_remove_nodes, args=[rm_reg_nodes,rm_glb_nodes]).start()
        return HttpJsonResponse()

    @expose('GET')
    def setMySqlParams(self, kwargs):
        """
        set a specified global variable of mysql to the value provided

        Parameters
        ----------
        variable : string
            name of MySQL variable
        value : string
            value to set
        
        """
        try:
            self._check_state([self.S_RUNNING])
            exp_params = [('variable', is_string),('value',is_string)]
            variable, value = check_arguments(exp_params, kwargs)
	    nodes = self.config.get_nodes()
	    for node in nodes:
		db = MySQLdb.connect(node.ip, 'mysqldb', self.root_pass)
		exc = db.cursor()
        	exc.execute('set global ' + variable + ' = ' + value + ';')
	    '''glb_nodes = self.config.get_glb_nodes()
	    n=len(nodes)*value
            for node in glb_nodes:
                db = MySQLdb.connect(node.ip, 'mysqldb', self.root_pass,port=8010)
                exc = db.cursor()
                exc.execute('set global ' + variable + ' = ' + n + ';')'''
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)
        return HttpJsonResponse("OK!")



========================
Server manager internals
========================

.. automodule:: conpaas.mysql.server.manager.internals
	:members: expose, wait_for_nodes, createServiceNodeThread

.. py:function:: list_nodes

   HTTP GET method. Uses :py:meth:`IaaSClient.listVMs()` to get list of all Service nodes. For each service node it gets it checks if it is in servers list. If some of them are missing they are removed from the list. Returns list of all service nodes.
   
   :returns: HttpJsonResponse - JSON response with the list of services
   :raises: HttpErrorResponse

.. py:function:: get_node_info
	
	HTTP GET method. Gets info of a specific node.

    :param param: serviceNodeId is a VMID of an existing service node.
    :type param: str
    :returns: HttpJsonResponse - JSON response with details about the node.
    :raises: ManagerException

.. py:function:: add_nodes

    HTTP POST method. Creates new node and adds it to the list of existing nodes in the manager. Makes internal call to :py:meth:`createServiceNodeThread`.

    :param kwargs: string describing a function (agent).
    :type param: str
    :returns: HttpJsonResponse - JSON response with details about the node.
    :raises: ManagerException

.. py:function:: remove_nodes

    HTTP POST method. Deletes specific node from a pool of agent nodes. 

    :param kwargs: string identifying a node.
    :type param: str
    :returns: HttpJsonResponse - JSON response with details about the node. OK if everything went well. ManagerException if something went wrong.
    :raises: ManagerException

.. py:function:: get_service_info

	HTTP GET method. Returns the current state of the manager. 

    :returns: HttpJsonResponse - JSON response with the description of the state.
    :raises: ManagerException

.. py:function:: set_up_replica_master

    HTTP POST method. Sets up a replica master node 

    :param id: new replica master id.
    :type param: dict
    :returns: HttpJsonResponse - JSON response with details about the new node. ManagerException if something went wrong.
    :raises: ManagerException

.. py:function:: set_up_replica_slave

	HTTP POST method. Sets up a replica slave node 

    :param id: new replica slave id.
    :type param: dict
    :returns: HttpJsonResponse - JSON response with details about the new node. ManagerException if something went wrong.
    :raises: ManagerException

.. py:function:: shutdown

	HTTP POST method. Shuts down the manager service. 

    :returns: HttpJsonResponse - JSON response with details about the status of a manager node: :py:attr`S_EPILOGUE`. ManagerException if something went wrong.
    :raises: ManagerException

.. py:function:: get_service_performance
	
	HTTP GET method. Placeholder for obtaining performance metrics.
     
    :param kwargs: Additional parameters.
    :type kwargs: dict 
    :returns:  HttpJsonResponse -- returns metrics

.. py:attribute:: S_INIT

   Contains string 'INIT' that describes server state.

.. py:attribute:: S_PROLOGUE

   Contains string 'STARTING' that describes server state.

.. py:attribute:: S_RUNNING

   Contains string 'RUNNING' that describes server state.

.. py:attribute:: S_ADAPTING

   Contains string 'ADAPTING' that describes server state.

.. py:attribute:: S_EPILOGUE

   Contains string 'EPILOGUE' that describes server state.

.. py:attribute:: S_STOPPED

   Contains string 'STOPPED' that describes server state.

.. py:attribute:: S_ERROR

   Contains string 'ERROR' that describes server state.

.. py:attribute:: config

   After initialization used for methods found in :py:class:`Configuration()`

.. py:attribute:: dstate

.. py:attribute:: exposed_functions 

   Dictionary that is populated with functions that are registered in :py:func:`ManagerServer.__init__`

.. py:attribute:: iaas

.. autoclass:: MySQLServerManager
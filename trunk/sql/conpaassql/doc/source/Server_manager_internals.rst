========================
Server manager internals
========================

.. py:class:: MySQLServerManager

   .. py:method:: __init__(self, conf)

      Initializes :py:attr:`config` using Config and sets :py:attr:`state` to :py:attr:`S_INIT`
      
      .. py:attribute:: state

         State of MySQLServerManager.

      :param conf: Configuration file. 

.. py:function:: listServiceNodes(kwargs)

   Uses :py:meth:`IaaSClient.listVMs()` to get list of all Service nodes. For each service node it gets it checks if it is in servers list. If some of them are missing they are removed from the list. Returns list of all service nodes.

.. py:function:: createServiceNode(kwargs)

   Creates a new service node using :py:meth:`IaaSClient.newInstance()`. Calls :py:func:`createServiceNodeThread`.

.. py:function:: deleteServiceNode(kwargs)

   Using :py:meth:`IaaSClient.killInstance()` removes service node from OpenNebula and after removing calls :py:meth:`Configuration.removeMySQLServiceNode()`

.. py:function:: createServiceNodeThread(function, new_vm)

   Calls :py:func:`wait_for_nodes`. And after completing calls :py:meth:`Configuration.addMySQLServiceNode()` to add new service node.

.. py:function:: getMySQLServerManagerState(params)

   :rtype: Returns state of Server manager.

.. py:function:: wait_for_nodes(nodes, poll_interval=10)

   Every poll_interval seconds checks if node is up. Calls function getserverstate so it gets state of agent.

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

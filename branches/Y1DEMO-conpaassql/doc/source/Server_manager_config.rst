======
Config
======

Holds configuration for the ConPaaS SQL Server Manager.

.. py:class:: ManagerException(Exception)

   Handles exceptions

   .. py:method:: __init__(self, code, *args, **kwargs)
      
      Gets information about exception and formats apropriate message.

      .. py:attribute:: code

         Exception code.

      .. py:attribute:: args

         Exception arguments.

      .. py:attribute:: message

         Formated with parameters.

      :param code: Exception code.
      :param args: Exception arguments. 
      :param kwargs: If it contains detail then it's used in formatting message.

.. py:class:: ServiceNode(object)

   .. py:method:: __init__(self, vmid, runMySQL=False)

      Initializes service node. 

      .. py:attribute:: vmid

         Service node id. 

      .. py:attribute:: isRunningMySQL

         Indicator if service node is running MySQL 

      :param vmid: Id that will be set.
      :param runMySQL: Indicator if service node is running MySQL

   .. py:method:: __repr__(self)

      :rtype: Returns service node's information. Id ip and if mysql is running on this service node.

   .. py:method:: __cmp__(self, other)

      :param other: Service node whos id will be compared to. 
      :rtype: Returns 0 if id of other and self.id are the same. Returns -1 if other has higher id. If other has lower id returns 1.

.. py:class:: Configuration(object)

   .. py:method:: __read_config(self,config)

      Reads the configuration file and defines attributes with values from configuration file.

      .. py:attribute:: driver

         Name of driver that will be used to communicate with open nebula.

      .. py:attribute:: xmlrpc_conn_location

         Connection information.

      .. py:attribute:: conn_password

         Connection password

      .. py:attribute:: conn_username

         Connection username

      :param config: Configuration file.

   .. py:method:: __init__(self, configuration)

	Initializes :py:attr:`mysql_count` with value zero and empty dictionary :py:attr:`serviceNodes`. Calls :py:meth:`__read_config`

      .. py:attribute:: mysql_count

         Nomber of MySQL service nodes.

      .. py:attribute:: serviceNodes

         Dictionary of all service nodes.
 
      :param configuration: Configuration file.

   .. py:method:: getMySQLServiceNodes(self)

      :rtype: Returns :py:attr:`serviceNodes`

   .. py:method:: getMySQLTuples(self)         

      :rtype: Returns service node ip and MySQL port for each service node that is running MySQL.

   .. py:method:: getMySQLIPs(self)

      :rtype: Returns ip address for each virtual machine that runs MySQL.

   .. py:method:: addMySQLServiceNode(self, vmid, accesspoint)

      Adds new service node to :py:attr:`serviceNodes` defined by vmid. Also increases :py:attr:`mysql_count`

      :param vmid: Id that will be used for service node. 
      :param accesspoint: 

   .. py:method:: removeMySQLServiceNode(self, vmid)

      Removes service node from :py:attr:`serviceNodes` identified by parameter vmid.

      :param vmid: Input parameter used to find service node that in :py:attr:`serviceNodes` that will be removed.

.. py:attribute:: CONFIGURATION_FILE

   Holds the path to the configuration file

.. py:attribute:: logger

   Used for logging information.

.. py:attribute::  E_STRINGS

   List of error strings indexed by rows:   

   .. code-block:: python
      
      E_STRINGS = [  
      'Unexpected arguments %s',
      'Unable to open configuration file: %s',
      'Configuration file does not exist: %s',
      'Unknown error.'
      ]

.. py:attribute:: E_ARGS_UNEXPECTED

   Index 0 at :py:attr:`E_STRINGS`

.. py:attribute:: E_CONFIG_READ_FAILED

   Index 1 at :py:attr:`E_STRINGS`

.. py:attribute:: E_CONFIG_NOT_EXIST

   Index 2 at :py:attr:`E_STRINGS`

.. py:attribute:: E_UNKNOWN

   Index 3 at :py:attr:`E_STRINGS`

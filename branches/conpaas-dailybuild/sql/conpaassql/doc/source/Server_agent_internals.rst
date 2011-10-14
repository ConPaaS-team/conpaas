======================
Server agent Internals
======================

.. py:class:: MySQLServerConfiguration

   Class holds MySQL server configuration.

   .. py:method:: __init__(self)

      Initializes attributes. And calls :py:meth:`read_config`

      .. py:attribute:: hostname

         Gets hostname from socket.

         .. code-block:: python

             self.hostname = socket.gethostname()

      .. py:attribute:: restart_count
            
         Initializes variable restart_count with value zero.

         .. code-block:: python

            self.restart_count = 0            

      .. py:attribute:: pid_file

         Constructs pid file location.

         .. code-block:: python
   
            self.pid_file = "/var/lib/mysql/" + self.hostname + ".pid"

      .. py:attribute:: config_dir

         Set's configuration directory.

         .. code-block:: python
   
            self.config_dir = os.getcwd()

      .. py:attribute:: access_log

         Sets location of access_log.

         .. code-block:: python
   
            self.access_log = os.getcwd() + '/access.log'

      .. py:attribute:: error_log

         Sets location of error log. 

         .. code-block:: python
   
            self.error_log =  os.getcwd() + '/error.log'        

      .. py:attribute:: conn_location

         Defines location where to connect. Initialized as empty string. 

      .. py:attribute:: conn_username

         Defines username to use in connection to MySQL. Initialized as empty string.

      .. py:attribute:: conn_password

         Defines password to use in connection to MySQL. Initialized as empty string.

      .. py:attribute:: mycnf_filepath

         Location of MySQL configuration file. Initialized as empty string.

      .. py:attribute:: path_mysql_ssr

         Location of file that controls MySQL. It's used for starting stopping and restarting MySQL server. Initialized as empty string.

      .. py:attribute:: port_client

         Initialized as empty string.

      .. py:attribute:: port_mysqld

         Initialized as empty string.

      .. py:attribute:: bind_address

         Initialized as empty string.

      .. py:attribute:: data_dir

         Initialized as empty string.

   .. py:method:: read_config(self)

   Reads the configuration file and sets the value of :py:attr:`MySQLServerConfiguration.conn_location`, :py:attr:`MySQLServerConfiguration.conn_password` and :py:attr:`MySQLServerConfiguration.conn_location`. 

      .. code-block:: python

         self.conn_location = config.get("MySQL_root_connection", "location")
         self.conn_password = config.get("MySQL_root_connection", "password")
         self.conn_username = config.get("MySQL_root_connection", "username")

   From configuration file also gets values for :py:attr:`MySQLServerConfiguration.mycnf_filepath` and :py:attr:`MySQLServerConfiguration.path_mysql_ssr`. 

      .. code-block:: python

         self.mycnf_filepath = config.get("MySQL_configuration","my_cnf_file")
         self.path_mysql_ssr = config.get("MySQL_configuration","path_mysql_ssr")

   After obtaining :py:attr:`MySQLServerConfiguration.mycnf_filepath` MySQL server configuration file is read and parsed with :py:meth:`MySQLServerConfiguration.MySQLConfigParser`. Values for :py:attr:`MySQLServerConfiguration.port_mysqld`, :py:attr:`MySQLServerConfiguration.bind_address` and :py:attr:`MySQLServerConfiguration.data_dir` are defined from parsed file. Before exiting temporary file that was created by :py:meth:`MySQLServerConfiguration.MySQLConfigParser` is deleted.

      .. code-block:: python

         config.readfp( self.MySQLConfigParser(my_cnf_text))    
         self.port_mysqld = config.get ("mysqld", "port")      
         self.bind_address = config.get ("mysqld", "bind-address")
         self.data_dir = config.get ("mysqld", "datadir")

   .. py:method:: change_config(self, id_param, param)

      Changes the values in MySQL configuration file. Value that has to be changed is identified by id_param and value it changes into is defined by param

      :param id_param: should one of these values: datadir, port or bind-address
      :param param: defines the new value
    
   .. py:method:: MySQLConfigParser(self, text)

      Receives text as a parameter. Text is parsed so it has appropriate form. After the parsing is complete the new text is written to temporary file. File handler is then returned.
    
      :param text: Text that has to be parsed so it has the right form. 

   .. py:method:: add_user_to_MySQL(self, new_username, new_password)

      Adds a new user to MySQL. Username and password are defined with parameters. 

      :param new_username: Username that new user will have.
      :param new_password: Password that new user will have.
        
   .. py:method:: remove_user_to_MySQL(self, username)
    
      :param username: Username of user that will be removed. 

   .. py:method:: get_users_in_MySQL(self)

      Queries the list of all users from MySQL and returns it. 

      :rtype: returns list of all users in MySQL
    
   .. py:method:: create_MySQL_with_dump(self, f)

      Creates MySQL database with dump file. 

      :param f: Dump file that will be used to create MySQL database

.. py:class::  MySQLServer

   .. py:method:: __init__(self)

      Initializes instance of :py:class:`MySQLServerConfiguration` and :py:attr:`MySQLServer.state`

      .. py:attribute:: state

         At initializing sets the state to :py:attr:`S_INIT`

   .. py:method:: post_restart(self)

      Not yet implemented. Things to do after restart.
        
   .. py:method:: start(self)

      sets :py:attr:`MySQLServer.state` to :py:attr:`S_STARTING` and tries to start MySQL server. If starting failed :py:attr:`MySQLServer.state` is set to :py:attr:`S_STOPPED`. If starting succeeded :py:attr:`MySQLServer.state` is set to :py:attr:`S_RUNNING`.
    
   .. py:method:: stop(self)

      If server is running sets :py:attr:`MySQLServer.state` to :py:attr:`S_STOPPING`. If it succeeded :py:attr:`MySQLServer.state` is set to :py:attr:`S_STOPPED`.  If it fails to stop  :py:attr:`MySQLServer.state` is set to :py:attr:`S_RUNNING`. Method also checks for pid file in :py:attr:`MySQLServerConfiguration.pid_file`. If it doesnt exist :py:attr:`MySQLServer.state` is set to :py:attr:`S_STOPPED`.

   .. py:method:: restart(self)

      Increases :py:attr:`MySQLServerConfiguration.restart_count` by one. If restarting succeeded :py:attr:`MySQLServer.state` is set to :py:attr:`S_RUNNING` if not it is set to :py:attr:`S_STOPPED`

   .. py:method:: status(self)
 
      returns :py:attr:`MySQLServerConfiguration.port_mysqld` and :py:attr:`MySQLServer.state` of MySQL .

.. py:class:: AgentException(Exception)
   
   Class used to format Exceptions.

      .. code-block:: python

         class AgentException(Exception):
         def __init__(self, code, *args, **kwargs):
         self.code = code
         self.args = args
         if 'detail' in kwargs:
            self.message = '%s DETAIL:%s' % ( (E_STRINGS[code] % args), str(kwargs['detail']) )
         else:
             self.message = E_STRINGS[code] % args

.. py:attribute:: exposed_functions 

   Dictionary that is populated with functions that are registered in :py:func:`AgentServer.__init__`

.. py:function:: createMySQLServer

      Calls :py:meth:`MySQLServer.start`. If no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      if Exception was raised returns:

      .. code-block:: python

         return {'opState': 'ERROR', 'error': str(e)}

.. py:function:: stopMySQLServer(params)

      Calls :py:meth:`MySQLServer.stop`. If no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      if Exception was raised returns:

      .. code-block:: python

         return {'opState': 'ERROR', 'error': str(e)}

.. py:function:: restartMySQLServer(params)

      Calls :py:meth:`MySQLServer.restart`. If no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      if Exception was raised returns:

      .. code-block:: python

         return {'opState': 'ERROR', 'error': str(e)}

.. py:function:: getMySQLServerState(params)

      Calls :py:meth:`MySQLServer.status`. If no Exception was raised returns:

      .. code-block:: python

         return {'opState':'OK', 'return': status}

      if Exception was raised returns:

      .. code-block:: python

         return {'opState': 'ERROR', 'error': str(e)}
    
.. py:function:: setMySQLServerConfiguration(params)

      Calls :py:meth:`MySQLServer.restart`. If no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      if Exception was raised returns:

      .. code-block:: python

         return {'opState': 'ERROR', 'error': str(e)}

.. py:function:: createNewMySQLuser(params)

      Calls :py:meth:`MySQLServerConfiguration.add_user_to_MySQL`

      .. code-block:: python

         niam.config.add_user_to_MySQL(params['username'], params['password'])

      and if no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      If Exception was raised returns:

      .. code-block:: python

        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        return {'opState': 'ERROR', 'error': ex.message}  
    
.. py:function:: removeMySQLuser(params)

      Calls :py:meth:`MySQLServerConfiguration.remove_user_to_MySQL`

      .. code-block:: python

         niam.config.remove_user_to_MySQL(params['username'])

      and if no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      If Exception was raised returns:

      .. code-block:: python

        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        return {'opState': 'ERROR', 'error': ex.message}  
    
.. py:function:: listAllMySQLusers(params)

      Calls :py:meth:`MySQLServerConfiguration.get_users_from_MYSQL`

      .. code-block:: python

         niam.config.remove_user_to_MySQL(params['username'])

      and if no Exception was raised returns:

      .. code-block:: python

         return {'opState': 'OK'}

      If Exception was raised returns:

      .. code-block:: python

        ex = AgentException(E_MYSQL, 'error "%d, %s' %(e.args[0], e.args[1]))
        return {'opState': 'ERROR', 'error': ex.message}  

.. py:function:: create_with_MySQLdump(params)

      Calls :py:meth:`MySQLServerConfiguration.create_MySQL_with_dump`

      .. code-block:: python

         ret = niam.config.create_MySQL_with_dump(f)

.. py:attribute:: S_INIT

   Contains string 'INIT' that describes server state.

.. py:attribute:: S_STARTING

   Contains string 'STARTING' that describes server state.

.. py:attribute:: S_RUNNING

   Contains string 'RUNNING' that describes server state.

.. py:attribute:: S_STOPPING

   Contains string 'STOPPING' that describes server state.

.. py:attribute:: S_STOPPED

   Contains string 'STOPPED' that describes server state.

.. py:attribute::  E_STRINGS

   List of error strings indexed by rows:   

   .. code-block:: python

      E_STRINGS = [  
      'Unexpected arguments %s', # 1 param (a list)
      'Unable to open configuration file: %s',
      'Failed to parse configuration file error: %s',
      'Configuration file already exists',
      'Invalid arguments',
      'Unknown error. Description: %s',
      'Failed to commit configuration',
      'Missing argument: %s',
      'MySQL reported an error: %s'
       ]

.. py:attribute:: E_ARGS_UNEXPECTED

   Index 0 at :py:attr:`E_STRINGS`

.. py:attribute:: E_CONFIG_NOT_EXIST

   Index 1 at :py:attr:`E_STRINGS`

.. py:attribute:: E_CONFIG_READ_FAILED

   Index 2 at :py:attr:`E_STRINGS`

.. py:attribute:: E_CONFIG_EXISTS

   Index 3 at :py:attr:`E_STRINGS`

.. py:attribute:: E_ARGS_INVALID

   Index 4 at :py:attr:`E_STRINGS`

.. py:attribute:: E_UNKNOWN

   Index 5 at :py:attr:`E_STRINGS`

.. py:attribute:: E_CONFIG_COMMIT_FAILED

   Index 6 at :py:attr:`E_STRINGS`

.. py:attribute:: E_ARGS_MISSING

   Index 7 at :py:attr:`E_STRINGS`

.. py:attribute:: E_MYSQL

   Index 8 at :py:attr:`E_STRINGS`

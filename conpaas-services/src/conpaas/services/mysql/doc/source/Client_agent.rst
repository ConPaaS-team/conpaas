============
Client agent
============
.. py:function:: AgentException(Exception)

   Receives Exception.

.. py:function:: __check_reply(body)

   Raises :py:func:`AgentException` if receiveda object is not JSON or if response does not contain "opState". :py:func:`AgentException` is also raised if opState doesnt have value OK. 

   :param body: should contain opState
   :type body: JSON object
   :rtype: Returns body

.. py:function:: getMySQLServerState(host, port)

   :py:func:`_http_get` is used for getting state of MySQL Server on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: createMySQLServer(host, port)

   :py:func:`_http_post` is used for sending command for starting MySQL Server on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: printUsage()

   Prints instructions for use of Client agent.

.. py:function:: restartMySQLServer(host, port)

   :py:func:`_http_post` is used for sending command for restarting MySQL Server on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: stopMySQLServer(host, port)

   :py:func:`_http_post` is used for sending command for stoping MySQL Server on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response
    
.. py:function:: configure_user(host, port, username, password)

   :py:func:`_http_post` is used for sending :py:attr:`username` and :py:attr:`password` using :py:attr:`params` to create new MySQL user on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :param username: Username that new user will have
   :param password: Password that new user will have
   :rtype: Returns :py:func:`__check_reply` response
        
.. py:function:: get_all_users(host, port)

   :py:func:`_http_get` is used for sending :py:attr:`params`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`. Reply should be list of all MySQL users on given :py:attr:`host` and :py:attr:`port`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: remove_user(host,port,name)

   :py:func:`_http_post` is used for sending :py:attr:`username` using :py:attr:`params` that are used to remove MySQL user on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`. 

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :param name: Username of the user that will be removed
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: setMySQLServerConfiguration(host,port, param_id, val)

   :py:func:`_http_post` is used for sending :py:attr:`param_id` using params that are used to change MySQL server configuration on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :param param_id: Identifier of the parameter that has to be changed
   :param val: Value to which parameter has to be changed.
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: send_mysqldump(host,port,location)

   :py:func:`_http_post` is used for sending :py:attr:`params` and files located by :py:attr:`location`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :param location: Location on the computer for the MySQL dump file
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: _http_post(host, port, uri, params, files=[])

   Constructs a HTTP POST request

.. py:function:: _http_get(host, port, uri, params=None)

   Constructs a HTTP GET request

.. py:attribute:: host
   
   Attribute used to identify host name that MySQL server uses.

.. py:attribute:: port

   Attribute used to identify port that MySQL server uses.

.. py:attribute:: username

   Attribute used to set username that will be used in adding or removing user.

.. py:attribute:: password

   Attribute used to set password for a user.

.. py:attribute:: param_id

   Attribute used to identify parameter that will be changed on MySQL server. Changeable parameters are: data directory (datadir), port (port), bind address (bind-address).

.. py:attribute:: location

   Location of the MySQL dump file on the computer.

.. py:attribute:: httplib.OK

   Http response code 200

.. py:attribute:: params

   JSON object used to send actions and attributes using _http_post or _http_get

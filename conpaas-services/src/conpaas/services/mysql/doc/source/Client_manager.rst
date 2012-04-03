==============
Client manager
==============

.. automodule:: conpaas.mysql.client.manager_client
   :members:

.. py:function:: AgentException(Exception)

   Receives Exception.

.. py:function:: __check_reply(body)

   Raises :py:func:`AgentException` if receiveda object is not JSON or if response does not contain "opState". :py:func:`AgentException` is also raised if opState doesnt have value OK. 

   :param body: should contain opState
   :type body: JSON object
   :rtype: Returns body

.. py:function:: printUsage()
   
   Prints instructions for use of Client manger.

.. py:function:: getListServiceNodes(host, port)

   :py:func:`_http_get` is used for getting list of service nodes supplied by server manager on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`. Reply from the server manager should be a list of all raised-by-server nodes.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: getMySQLServerState(host, port)

   :py:func:`_http_get` is used for getting current state of server manager on given :py:attr:`host` and :py:attr:`port`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`. 

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: addServiceNode(host, port, function)

   :py:func:`_http_post` is used for sending command to Server manager on given :py:attr:`host` and :py:attr:`port` to create a new service node. Function of the new node is defined by :py:attr:`function`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :param function: What function will the new service node have: manager or agent
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: deleteServiceNode(host, port, id)

   :py:func:`_http_post` is used for sending command to server manager on given :py:attr:`host` and :py:attr:`port` to delete existing service node. Service node that will be deleted is defined by :py:attr:`id`. Raises Exception if return code is not :py:attr:`httplib.OK` else sends body to :py:func:`__check_reply`.

   :param host: Host that will be used to connect to MySQL Server
   :param port: Port that will be used to connect to MySQL Server
   :param id: ID of service node that will be removed. 
   :rtype: Returns :py:func:`__check_reply` response.

.. py:function:: _http_post(host, port, uri, params, files=[])

   Constructs a HTTP POST request.

.. py:function:: _http_get(host, port, uri, params=None)

   Constructs a HTTP GET request.

.. py:attribute:: host
   
   Attribute used to identify host name that MySQL server uses.

.. py:attribute:: port

   Attribute used to identify port that MySQL server uses.

.. py:attribute:: function

   Attribute used to define which function will the new node have.

.. py:attribute:: id 

   Attribute used to identify service node that will be deleted.

.. py:attribute:: httplib.OK

   Http response code 200

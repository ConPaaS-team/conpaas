======================
Server agent Internals
======================

.. automodule:: conpaas.mysql.server.agent.internals

.. autoclass:: MySQLServer

.. py:function:: create_server

    Creates an agent server. Calls to :py:meth:`MySQLServer.start`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

         return HttpJsonResponse({'return': 'ERROR', 'error': str(e)})
         
    :returns: HttpJsonResponse
    
.. py:function:: stop_server

    Stops the MySQL server.
    
    .. code-block:: python

         return HttpJsonResponse({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

         return HttpJsonResponse({'return': 'ERROR', 'error': str(e)})
         
    :returns: HttpJsonResponse
    
.. py:function:: restart_server

	Restarts the MySQL server. Calls to :py:meth:`MySQLServer.restart`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

         return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})
         
    :returns: HttpJsonResponse
    
.. py:function:: get_server_state
   
    Gets the MySQL server state. Calls to :py:meth:`MySQLServer.status`. If no Exception was raised returns:
    
    .. code-block:: python

         return HttpJsonResponse({'return': status})
         
    if Exception was raised returns:

    .. code-block:: python

        return HttpJsonResponse({'return': status})
         
    :returns: HttpJsonResponse
    :raises: AgentException
    
    
.. py:function:: configure_user
 
   Configures the new MySQL server user. Calls to :py:meth:`MySQLServerConfiguration.add_user_to_MySQL`. If no Exception was raised returns:
    
    .. code-block:: python

        return HttpJsonResponse ({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

        return HttpJsonResponse ({'return': 'ERROR', 'error': ex.message})         
    
   :param username: Username for the new user.    
   :type username: str
   :param password: Password for the new user.
   :type password: str
   :returns: HttpJsonResponse
   :raises: AgentException
    
.. py:function:: delete_user

    Deletes a user from MySQL server. Calls to :py:meth:`MySQLServerConfiguration.remove_user_to_MySQL`. If no Exception was raised returns:
    
    .. code-block:: python

        return HttpJsonResponse ({'return': 'OK'})
         
    if Exception was raised returns:

    .. code-block:: python

        return HttpJsonResponse({'return': 'ERROR', 'error': ex.message}) 
         
    :param username: Username for the user that will be removed.
    :param type: str
    :returns: HttpJsonResponse
    :raises: AgentException

.. py:function:: get_all_users

    Gets all configured users. Calls to :py:meth:`MySQLServerConfiguration.get_users_in_MySQL`. If no Exception was raised returns:
    
    .. code-block:: python

        return HttpJsonResponse ({'return': 'OK'})
         
    if AgentException was raised returns:

    .. code-block:: python

        return HttpJsonResponse( {'users': 'ERROR', 'error': ex.message}) 
         
    :param username: Username for the user that will be removed.
    :param type: str
    :returns: HttpJsonResponse
    :raises: AgentException
 
.. py:function:: set_up_replica_master
  
    Sets up a replica master. 
             
    :param username: Username for the user that will be removed.
    :param type: str
    :returns: HttpJsonResponse({'opState': 'OK'}  )
    :raises: AgentException    
  
    
.. py:function:: set_up_replica_slave
 
    Sets up a replica slave node.

    1)Change server id in the my.cnf. 

    2)You will need to configure the slave with settings 
    for connecting to the master, such as the host name, login credentials, and binary 
    log file name and position. See Section 15.1.1.10, Setting the Master Configuration 
    on the Slave. 
    
    Example:
        mysql>CHANGE MASTER TO  MASTER_HOST='vm-10-1-0-10', MASTER_USER='root', 
        MASTER_PASSWORD='topole48', MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS=106;
    
    :param master_host: hostname of the master node.
    :param master_log_file: filename of the master log.
    :param master_log_pos: position of the master log file.
    :param slave_server_id: id which will be written into my.cnf.
           
    :returns: HttpJsonResponse({'opState': 'OK'}  )
    :raises: AgentException     
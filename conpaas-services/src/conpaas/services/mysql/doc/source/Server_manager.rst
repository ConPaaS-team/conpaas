==============
Server manager
==============

.. py:class:: SQLServerRequestHandler(AbstractRequestHandler):

   .. py:method:: _dispatch(self, method, params)
      
      Sends back appropriate response code. 

.. py:class:: ManagerServer(HTTPServer, ThreadingMixIn)

   .. py:method:: __init__(self, server_address, RequestHandlerClass=AbstractRequestHandler)

      Initializes HTTP server. Calls :py:meth:`register_method` for every element inside exposed_function

   .. py:method:: register_method(self, http_method, func_name, callback)

      Registers a POST or GET method.


============
Server agent
============

.. py:class:: AgentServer(HTTPServer, ThreadingMixIn)

   .. py:method:: __init__(self, server_address, RequestHandlerClass=AbstractRequestHandler)

      Initializes HTTP server. Calls :py:meth:`register_method` for every element inside dictionary exposed_function

   .. py:method:: register_method(self, http_method, func_name, callback)

      Registers a POST or GET method.


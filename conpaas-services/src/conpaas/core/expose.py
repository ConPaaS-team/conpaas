# -*- coding: utf-8 -*-

"""
    conpaas.core.expose
    ===================

    ConPaaS core: expose http methods.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

exposed_functions_http_methods = {}
def expose(http_method):
    """
    This decorator simply stores the http_method for a given handler (exposed) function 
    in a global dictionary, namely exposed_functions_http_methods 
    """
    def decorator(func):
      exposed_functions_http_methods[id(func)] = http_method
      def wrapped(self, *args, **kwargs):
        return func(self, *args, **kwargs)
      return wrapped
    return decorator

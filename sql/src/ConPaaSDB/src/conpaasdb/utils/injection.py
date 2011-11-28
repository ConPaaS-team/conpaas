import logging
import inject

class FreshScope(inject.appscope):
    logger = logging.getLogger('inject.FreshScope')
    
    def get(self, type):
        if type in self._bindings:
            return self._bindings.get(type)()
    
    def __call__(self, cls):
        self.bind(cls, cls)
        return cls

fresh_scope = FreshScope()

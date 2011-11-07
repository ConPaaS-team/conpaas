class FakeEngineCore(object):
    def __init__(self):
        self.commands = []
    
    def execute(self, cmd, **kwargs):
        c, kw, res = self.commands.pop(0)
        
        assert cmd == c
        assert kwargs == kw
        
        return res
    
    def expect(self, cmd, **kwargs):
        self.commands.append((cmd, kwargs, None))
    
    def expect_result(self, cmd, result, **kwargs):
        self.commands.append((cmd, kwargs, result))

class FakeMySQLEngine(object):
    def __init__(self):
        self.engine = FakeEngineCore()
        self.execute = self.engine.execute
        self.expect = self.engine.expect
        self.expect_result = self.engine.expect_result

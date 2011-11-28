class FakeExecute(object):
    def __init__(self):
        self.commands = []
    
    def execute(self, command, **kwargs):
        c, res = self.commands.pop(0)
        
        assert command == c
        
        return res
    
    def expect(self, cmd):
        self.commands.append((cmd, None))
    
    def expect_result(self, cmd, result):
        self.commands.append((cmd, result))

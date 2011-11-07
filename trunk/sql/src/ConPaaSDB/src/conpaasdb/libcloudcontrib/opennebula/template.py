class OneTemplate(object):
    INDENT = ' ' * 4
    
    def __init__(self, template):
        self.template = template
    
    def _wrap(self, txt, char='"'):
        return char + txt.replace(char, '\\' + char) + char
    
    def serialize(self, node, level=0):
        if node is None:
            yield node
        elif isinstance(node, dict):
            if level:
                yield '['
            
            rows = []
            
            for key, value in node.items():
                serialized = list(self.serialize(value, level + 1))
                
                if serialized != [None]:
                    rows.append(self.INDENT * level + '%s = %s' % (
                                                key, '\n'.join(serialized)))
            
            rows_count = len(rows)
            
            for i, row in enumerate(rows):
                if level and i < rows_count - 1:
                    yield row + ','
                else:
                    yield row
            
            if level:
                yield self.INDENT * (level - 1) + ']'
        elif isinstance(node, bool):
            yield self._wrap('yes') if node else self._wrap('no')
        elif isinstance(node, basestring):
            yield self._wrap(node)
        else:
            yield str(node)
    
    def __str__(self):
        return '\n'.join(self.serialize(self.template))


import ast
import _ast
import string


class DecoratorVisitor(ast.NodeVisitor):

    def __init__(self):
        self.attr = None
        self.cert = None
        self.name = None

    def visit_Call(self, node):
        entry = {}
        ast.NodeVisitor.generic_visit(self, node)
        if self.attr == 'route':
            for keywrd in node.keywords:
                if keywrd.arg == 'methods':
                    methods = self._get_Str_List(keywrd.value)
                    entry['methods'] = string.join(sorted(methods), ', ')
            if len(node.args) > 0 and isinstance(node.args[0], ast.Str):
                entry['name'] = node.args[0].s
        if self.name == 'expose':
            if len(node.args) > 0 and isinstance(node.args[0], ast.Str):
                entry['methods'] = node.args[0].s
            entry['expose'] = ''
        if self.name == 'cert_required':
            for keywrd in node.keywords:
                if keywrd.arg == 'role':
                    role = keywrd.value.s
                    entry['certificate'] = '%s certificate required' % role
        return entry

    def visit_Attribute(self, node):
        ast.NodeVisitor.generic_visit(self, node)
        self.attr = node.attr

    def visit_Name(self, node):
        self.name = node.id

    def _get_Str_List(self, node):
        str_list = []
        for elt in node.elts:
            str_list.append(elt.s)
        return str_list


class APIExtractor(ast.NodeVisitor):
    """Interpret AST nodes to extract HTTP API information"""

    def __init__(self):
        self.all_functions_doc = []
        self.classes_doc = []
        self.deco_visitor = DecoratorVisitor()
        self.source_file = 'Unknown source file'

    def visit(self, node):
        ast.NodeVisitor.visit(self, node)

    def visit_ClassDef(self, node):
        prev_functions = self.all_functions_doc
        self.all_functions_doc = []
        self.generic_visit(node)
        if self.all_functions_doc:
            # some public entries were found in this class
            class_doc = {}
            class_doc['name'] = node.name
            class_doc['entries'] = self.all_functions_doc
            class_doc['extends'] = [base.id for base in node.bases
                                    if isinstance(base, _ast.Name)
                                    and base.id != 'object']
            class_doc['source_file'] = self.source_file
            self.classes_doc.append(class_doc)
        self.all_functions_doc = prev_functions

    def visit_FunctionDef(self, node):
        if node.decorator_list:
            function_doc = {}
            entries = []
            cert = None
            for decorator_node in node.decorator_list:
                deco = self.deco_visitor.visit(decorator_node)
                if deco:
                    if 'expose' in deco:
                        entries.append((node.name, deco['methods']))
                    if 'name' in deco:
                        entries.append((deco['name'], deco['methods']))
                    if 'cert_required' in deco:
                        cert = deco['cert_required']
            if entries:
                function_doc['names'] = entries
                docstring = ast.get_docstring(node)
                if docstring:
                    function_doc['doc'] = "%s" % docstring
                else:
                    function_doc['doc'] = "MISSING DOC."
                function_doc['source_file'] = self.source_file
                function_doc['cert_required'] = cert
                self.all_functions_doc.append(function_doc)

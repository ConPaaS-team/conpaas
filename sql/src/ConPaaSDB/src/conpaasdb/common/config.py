import colander as cl

from conpaasdb.utils.config import path_exists, is_port

class ConfigPackage(cl.Schema):
    package = cl.SchemaNode(cl.String(), validator=path_exists)

class ConfigProvider(cl.Schema):
    name = cl.SchemaNode(cl.Str())

class ConfigOpenNebula(cl.Schema):
    username = cl.SchemaNode(cl.Str())
    password = cl.SchemaNode(cl.Str(), missing=None)
    host = cl.SchemaNode(cl.Str())
    port = cl.SchemaNode(cl.Int(), validator=is_port)

class ConfigManager(cl.Schema):
    port = cl.SchemaNode(cl.Int(), validator=is_port)
    name = cl.SchemaNode(cl.Str())
    image_id = cl.SchemaNode(cl.Int())
    network_id = cl.SchemaNode(cl.Int())

class ConfigAgent(cl.Schema):
    port = cl.SchemaNode(cl.Int(), validator=is_port)
    name = cl.SchemaNode(cl.Str())
    image_id = cl.SchemaNode(cl.Int())
    network_id = cl.SchemaNode(cl.Int())

import colander as cl

from conpaasdb.utils.config import path_exists, is_port

class ConfigMySQL(cl.Schema):
    password = cl.SchemaNode(cl.Str(), missing=None)
    config = cl.SchemaNode(cl.String(), validator=path_exists)

class ConfigSupervisor(cl.Schema):
    user = cl.SchemaNode(cl.Str())
    password = cl.SchemaNode(cl.Str())
    port = cl.SchemaNode(cl.Int(), validator=is_port)

class ConfigSchema(cl.Schema):
    mysql = ConfigMySQL()
    supervisor = ConfigSupervisor()

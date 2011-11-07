import colander as cl

from conpaasdb.common.config import ConfigPackage, ConfigProvider,\
    ConfigOpenNebula, ConfigAgent

class ConfigMySQL(cl.Schema):
    password = cl.SchemaNode(cl.Str())

class ConfigSchema(cl.Schema):
    package = ConfigPackage()
    provider = ConfigProvider()
    opennebula = ConfigOpenNebula()
    agent = ConfigAgent()
    mysql = ConfigMySQL()

import colander as cl

from conpaasdb.common.config import ConfigPackage, ConfigProvider,\
    ConfigOpenNebula, ConfigManager

class ConfigSchema(cl.Schema):
    package = ConfigPackage()
    provider = ConfigProvider()
    opennebula = ConfigOpenNebula()
    manager = ConfigManager()

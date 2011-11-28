from conpaasdb.adapters.providers import get_provider
from conpaasdb.adapters.providers.base import Provider
from conpaasdb.agent import AgentSettings
from conpaasdb.manager import ManagerSettings
from conpaasdb.adapters.mysql import MySQLSettings
from conpaasdb.adapters.supervisor import SupervisorSettings
from conpaasdb.common import PackageSettings

def configure_package(injector, config):
    package_settings = PackageSettings()
    package_settings.package = config.package.package
    injector.bind(PackageSettings, package_settings)

def configure_provider(injector, config):
    provider_name = config.provider.name
    ProviderCls = get_provider(provider_name)
    provider_config = vars(config).get(provider_name)
    provider = ProviderCls(**vars(provider_config))
    injector.bind(Provider, provider)

def configure_manager(injector, config):
    manager_settings = ManagerSettings()
    manager_settings.port = config.manager.port
    manager_settings.name = config.manager.name
    manager_settings.image_id = config.manager.image_id
    manager_settings.network_id = config.manager.network_id
    injector.bind(ManagerSettings, manager_settings)

def configure_agent(injector, config):
    agent_settings = AgentSettings()
    agent_settings.port = config.agent.port
    agent_settings.name = config.agent.name
    agent_settings.image_id = config.agent.image_id
    agent_settings.network_id = config.agent.network_id
    injector.bind(AgentSettings, agent_settings)

def configure_mysql(injector, config):
    mysql_settings = MySQLSettings()
    mysql_settings.password = config.mysql.password
    mysql_settings.config = config.mysql.config
    injector.bind(MySQLSettings, mysql_settings)

def configure_supervisor(injector, config):
    supervisor_settings = SupervisorSettings()
    supervisor_settings.user = config.supervisor.user
    supervisor_settings.password = config.supervisor.password
    supervisor_settings.port = config.supervisor.port
    injector.bind(SupervisorSettings, supervisor_settings)

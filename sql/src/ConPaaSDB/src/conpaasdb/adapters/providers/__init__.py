from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

PROVIDERS = {
    'opennebula': ('conpaasdb.adapters.providers.opennebula', 'OpenNebulaProvider')
}

@flog
def get_provider(provider):
    mod, cls = PROVIDERS[provider]
    _mod = __import__(mod, globals(), locals(), [cls])
    return getattr(_mod, cls)

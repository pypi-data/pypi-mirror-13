
from voidpp_tools.json_config import JSONConfigLoader, ConfigLoaderException

loader = JSONConfigLoader(__file__)

def load_config(create = None):
    try:
        config = loader.load('asd-system-config.json', create = create)
    except ConfigLoaderException:
        config = {}
    return config

def save_config(config):
    loader.save(config)

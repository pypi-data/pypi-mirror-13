import os
from voidpp_tools.json_config import JSONConfigLoader

config_loader = JSONConfigLoader(os.path.dirname(__file__))

config = config_loader.load('pca9685-driver-http-config.json')

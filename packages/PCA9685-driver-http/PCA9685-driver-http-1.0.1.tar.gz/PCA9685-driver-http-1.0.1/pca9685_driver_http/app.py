from flask import Flask
import logging
import logging.config
from pca9685_driver import Device

from .config import config, config_loader

APPNAME = 'pca9685_driver_http'

app = Flask(APPNAME)

logging.config.dictConfig(config['logger'])

logger = logging.getLogger(__name__)

logger.info("Config loaded from %s" % config_loader.filename)

devices = {}

for name, conf in config['devices'].items():
    devices[name] = Device(conf['address'], conf['bus'])
    logger.info("PCA9685 device created on address %s in bus #%s" % (conf['address'], conf['bus']))

from .controllers import *
from .error_handlers import *

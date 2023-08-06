import logging
from pca9685_driver.device import DeviceException

from .app import app
from .http import HttpException, create_response

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def all_exception_handler(error):
    logger.exception(error)
    return create_response({'result': 'error', 'message': str(error)}, 500)

@app.errorhandler(HttpException)
def http_exception_handler(error):
    logger.exception(error)
    return create_response({'result': 'error', 'message': str(error)}, error.code)

@app.errorhandler(DeviceException)
def device_exception_handler(error):
    logger.exception(error)
    return create_response({'result': 'error', 'message': str(error)}, 400)

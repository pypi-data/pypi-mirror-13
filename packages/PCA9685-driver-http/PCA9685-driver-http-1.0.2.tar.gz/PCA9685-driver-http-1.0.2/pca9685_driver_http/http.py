import logging
import json

logger = logging.getLogger(__name__)

class HttpException(Exception):
    def __init__(self, message, code):
        super(HttpException, self).__init__(message)
        self.code = code

def create_response(data, code = 200):
    return json.dumps(data) + "\n", code

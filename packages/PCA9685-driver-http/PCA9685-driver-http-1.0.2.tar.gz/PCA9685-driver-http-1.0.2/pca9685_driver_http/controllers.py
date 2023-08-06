import logging
from flask import request
from pca9685_driver import Device
from querystring_parser import parser

from .app import app, devices
from .http import HttpException, create_response

logger = logging.getLogger(__name__)

def check_device(device):
    if device not in devices:
        raise HttpException("Unknown device '%s'" % device, 404)

@app.route('/devices/<device_name>/led/<int:led_number>', methods = ['GET'])
def get_led_value(device_name, led_number):
    check_device(device_name)
    value = devices[device_name].get_pwm(led_number)
    return create_response({'result': 'ok', 'value': value})

@app.route('/devices/<device_name>/led/<int:led_number>', methods = ['PUT'])
def set_led_value(device_name, led_number):
    check_device(device_name)
    value = int(request.form['value'])
    devices[device_name].set_pwm(led_number, value)
    return create_response({'result': 'ok'})

@app.route('/devices/<device_name>/led', methods = ['GET'])
def get_led_values(device_name):
    check_device(device_name)
    result = {}
    dev = devices[device_name]
    for led in range(0, Device.ranges['led_number'][1]+1):
        result[led] = dev.get_pwm(led)
    return create_response({'result': 'ok', 'values': result})

@app.route('/devices/<device_name>/led', methods = ['PUT'])
def set_led_values(device_name):
    check_device(device_name)
    dev = devices[device_name]
    args = parser.parse(request.get_data())
    for led, value in args['led'].items():
        dev.set_pwm(int(led), int(value))
    return create_response({'result': 'ok'})

@app.route('/devices/<device_name>/pwm-frequency', methods = ['GET'])
def get_pwm_frequency(device_name):
    check_device(device_name)
    return create_response({'result': 'ok', 'value': devices[device_name].get_pwm_frequency()})

@app.route('/devices/<device_name>/pwm-frequency', methods = ['PUT'])
def set_pwm_frequency(device_name):
    check_device(device_name)
    value = int(request.form['value'])
    devices[device_name].set_pwm_frequency(value)
    return create_response({'result': 'ok'})

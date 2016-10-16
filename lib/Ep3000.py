#!/usr/bin/env python

import time
import serial
from decimal import *

_serial = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate = 2400,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)


def send(command):
    _serial.write('{0:s}\r'.format(command))
    return _serial.readline()


class Command(object):
    def __init__(self, code):
        self.code = code
        self.last_result = None

    def check_result(self, result):
        return True

    def parse_result(self, result):
        return result

    def send(self):
        res = None
        while 1:
            res = send(self.code)
            if self.check_result(res): break
            time.sleep(.1)
        self.last_result = {
            "timestamp": time.time(),
            "payload": self.parse_result(res),
        }
        return self.last_result


class StatusCommand(Command):
    def __init__(self):
        super(StatusCommand, self).__init__('Q1')

    def check_result(self, result):
        return result[:1] == '(' and result[-1:] == '\r'

    def parse_result(self, result):
        data = result[1:-1].split(' ')
        bits = map(lambda bit: bool(int(bit)), list(data[7]))

        status = {
            "utility_fail": bits[0],
            "battery_low": bits[1],
            "avr_active": bits[2],
            "ups_fail": bits[3],
            "ups_line_interactive": bits[4],
            "test_in_progress": bits[5],
            "shuttdown_active": bits[6],
            "beeper_on": bits[7],
        }
        return {
            "status": status,
            "input_voltage": Decimal(data[0]),
            "input_fault_voltage": Decimal(data[1]),
            "output_voltage": Decimal(data[2]),
            "output_load": Decimal(data[3]),
            "output_frequency": Decimal(data[4]),
            "battery_voltage": Decimal(data[5]),
            "temperature": Decimal(data[6]),
        }

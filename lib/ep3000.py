#!/usr/bin/env python

import re
import time
import serial
from decimal import *
from common import ObjectDict

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
    _serial.flush()
    return _serial.readline()


class TooManyTriesException(Exception):
    pass


class Command(object):
    def __init__(self, code):
        self.code = code
        self.last_result = None

    def check_result(self, result):
        return True

    def parse_result(self, result):
        return result

    def send(self, max_tries = 10, sleep = .5):
        tries = 0
        res = None
        while True:
            if max_tries and tries > max_tries:
                print 'Last try (#%s) result: %s'%(tries, res)
                raise TooManyTriesException()
            elif tries > 1 and divmod(tries, 10)[1] == 0:
                print 'Last try (#%s) result: %s' % (tries, res)

            tries += 1
            try:
                res = send(self.code)
            except serial.SerialException:
                continue
            if self.check_result(res): break
            time.sleep(sleep)

        self.last_result = ObjectDict({
            "timestamp": time.time(),
            "tries": tries,
            "payload": self.parse_result(res),
        })

        return self.last_result


class StatusCommand(Command):
    checker = re.compile(
        r'^\([0-9]{3}\.[0-9] [0-9]{3}\.[0-9] [0-9]{3}\.[0-9] [0-9]{3}'
        r' [0-9]{2}\.[0-9] (?:[0-9]{2}\.[0-9]|[0-9]\.[0-9]{2})'
        r' [0-9]{2}\.[0-9] [01]{2}.[01]{5}\r$'
    )

    def __init__(self):
        super(StatusCommand, self).__init__('Q1')

    def check_result(self, result):
        return bool(type(self).checker.match(result))

    def parse_result(self, result):
        data = result[1:-1].split(' ')
        bits = map(lambda c: False if c == '0' else True, list(data[7]))

        status = ObjectDict({
            "utility_fail": bits[0],
            "battery_low": bits[1],
            "avr_active": bits[2],
            "ups_fail": bits[3],
            "ups_line_interactive": bits[4],
            "test_in_progress": bits[5],
            "shuttdown_active": bits[6],
            "beeper_on": bits[7],
        })

        return ObjectDict({
            "status": status,
            "input_voltage": Decimal(data[0]),
            "input_fault_voltage": Decimal(data[1]),
            "output_voltage": Decimal(data[2]),
            "output_load": Decimal(data[3]),
            "output_frequency": Decimal(data[4]),
            "battery_voltage": Decimal(data[5]),
            "temperature": Decimal(data[6]),
        })

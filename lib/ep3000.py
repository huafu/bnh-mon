#!/usr/bin/env python
# coding=utf-8
import atexit
import json
import re
import serial
import time

from common import log
from lib import LATESTS_RESULTS_PATH

_serial = None


def serial_port():
    global _serial
    if _serial is None:
        _serial = serial.Serial(
            port = '/dev/ttyUSB0',
            baudrate = 2400,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 1
        )
    return _serial


def serial_send(command):
    s = serial_port()
    s.write('{0:s}\r'.format(command))
    s.flush()
    return s.readline()


@atexit.register
def serial_close():
    global _serial
    if _serial is not None:
        _serial.close()
        _serial = None


class TooManyTriesException(Exception):
    pass


class Command(object):
    def __init__(self, code, pretty_name = None):
        self.code = code
        self.last_result = None
        self.pretty_name = pretty_name if pretty_name else code.lower()

    def check_result(self, result):
        return True

    def parse_result(self, result):
        return result

    def check_parsed_results(self, parsed_results):
        return True

    def send(self, max_tries = 10, sleep = .5):
        tries = 0
        res = None
        parsed_results = None
        while True:
            if max_tries and tries > max_tries:
                log('Last try (#%s) result: %s' % (tries, res), 'warning')
                raise TooManyTriesException()
            elif tries > 1 and divmod(tries, 10)[1] == 0:
                log('Last try (#%s) result: %s' % (tries, res), 'warning')

            tries += 1
            try:
                res = serial_send(self.code)
            except serial.SerialException:
                continue

            if self.check_result(res):
                parsed_results = self.parse_result(res)
                if self.check_parsed_results(parsed_results): break
                log('Weird values: %s' % (json.dumps(parsed_results)), 'warning')

            time.sleep(sleep)

        self.last_result = {
            "timestamp": time.time(),
            "tries": tries,
            "payload": parsed_results,
        }

        log('Got %s (%s) command response: %s' % (
            self.pretty_name, self.code, json.dumps(self.last_result)
        ))

        json_file = LATESTS_RESULTS_PATH + '/' + self.pretty_name + '.json'
        fp = open(json_file, 'w')
        json.dump(self.last_result, fp)
        fp.close()

        return self.last_result


class StatusCommand(Command):
    checker = re.compile(
        r'^\([0-9]{3}\.[0-9]? [0-9]{3}\.[0-9]? [0-9]{3}\.[0-9]? [0-9]{3}'
        r' [0-9]{2}\.[0-9]? [0-9]{2}\.[0-9]?'
        r' [0-9]{2}\.[0-9]? [01]{2}.[01]{5}\r$'
    )

    def __init__(self):
        super(StatusCommand, self).__init__('Q1', 'ep3000-status')

    def check_result(self, result):
        return bool(type(self).checker.match(result))

    def parse_result(self, result):
        data = result[1:-1].split(' ')
        bits = map(lambda c: False if c == '0' else True, list(data[7]))

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
            "input_voltage": float(data[0]),
            "input_fault_voltage": float(data[1]),
            "output_voltage": float(data[2]),
            "output_load": float(data[3]),
            "output_frequency": float(data[4]),
            "battery_voltage": float(data[5]),
            "temperature": float(data[6]),
        }


class UpsRatingCommand(Command):
    checker = re.compile(
        r'^\#[0-9]{3}\.[0-9]? [0-9]{3} (?:[0-9]{2}\.[0-9]{0,2}|[0-9]{3}\.[0-9]?)'
        r' [0-9]{2}\.[0-9]?\r$'
    )

    def __init__(self):
        super(UpsRatingCommand, self).__init__('F', 'ep3000-ups-rating')

    def check_result(self, result):
        return bool(type(self).checker.match(result))

    def parse_result(self, result):
        data = result[1:-1].split(' ')

        return {
            "rating_voltage": float(data[0]),
            "rating_current": float(data[1]),
            "battery_voltage": float(data[2]),
            "frequency": float(data[3]),
        }

#!/usr/bin/env python

from lib import *


def main():
    print StatusCommand().send().payload.battery_voltage

exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

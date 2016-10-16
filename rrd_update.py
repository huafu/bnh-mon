#!/usr/bin/env python

from lib import *


def main():
    status = ep3000.StatusCommand()

    def update_rrd():
        payload = status.send().payload
        print 'logged to rrd - load: %d%% - batt: %dV' % (
            payload.output_load,
            payload.battery_voltage
        )
        rrd.update_ep3000(payload)

    common.set_interval(update_rrd, 10)


exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

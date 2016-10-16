#!/usr/bin/env python

import time
from lib import *

def main():
    status = ep3000.StatusCommand()

    while not exiting_app:
        msg = status.send(max_tries = 0)
        payload = msg.payload
        rrd.update_ep3000(payload)
        print 'logged to rrd (%s tries) - load: %d%% - batt: %dV' % (
            msg.tries,
            payload.output_load,
            payload.battery_voltage
        )
        time.sleep(1)


exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

#!/usr/bin/env python
import json
import time
from lib import *


def main():
    status = ep3000.StatusCommand()
    rating = ep3000.UpsRatingCommand()

    while not exiting_app:
        msg = status.send(max_tries = 0)
        payload = msg['payload']
        rrd.update_ep3000(payload)
        rating.send()
        time.sleep(.5)


exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

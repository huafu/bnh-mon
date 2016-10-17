#!/usr/bin/env python

import rrdtool
from lib import *


def main():
    print ep3000.StatusCommand().send()['payload']
    print ep3000.UpsRatingCommand().send()['payload']
    # print rrd.create_ep3000()
    # rrd.generate_graphs()
    # rrdtool.fetch(
    #    rrd.FILE_EP3000,
    #    'AVERAGE',
    #    '--start -4h'
    # )


exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

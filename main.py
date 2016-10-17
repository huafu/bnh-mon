#!/usr/bin/env python

import rrdtool
from lib import *
from lib.rrd import create_ep3k_ups


def main():
    #print ep3000.StatusCommand().send()['payload']
    #print ep3000.UpsRatingCommand().send()['payload']
    print create_ep3k_ups()
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

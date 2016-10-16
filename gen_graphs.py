#!/usr/bin/env python
import time, os, sys
from lib import *

os.environ['TZ'] = "Asia/Bangkok"
time.tzset()

period = 'hourly'
if len(sys.argv) > 1:
    period = sys.argv[1]

if period == 'all':
    for period in ('hourly', 'daily', 'weekly', 'monthly', 'yearly'):
        rrd.generate_graphs(period)
        rrd.generate_graphs(period, True)
else:
    rrd.generate_graphs(period)
    rrd.generate_graphs(period, True)

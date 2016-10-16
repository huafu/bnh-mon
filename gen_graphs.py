#!/usr/bin/env python
import time, os, sys
from lib import *

os.environ['TZ'] = "Asia/Bangkok"
time.tzset()

period = 'hourly'
if len(sys.argv) > 1:
    period = sys.argv[1]
rrd.generate_graphs(period)

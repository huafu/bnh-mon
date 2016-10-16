#!/usr/bin/env python
import time, os
from lib import *

os.environ['TZ'] = "Asia/Bangkok"
time.tzset()

for period in ('hourly', 'daily', 'weekly', 'monthly', 'yearly'):
    rrd.generate_graphs(period)

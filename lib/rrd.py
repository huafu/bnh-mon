#!/usr/bin/env python

#
# rrdtool create ../rrd/ep3000.rrd \
#   -s 10 \
#   --no-overwrite \
#   DS:input_voltage:GAUGE:30:0:250 \
#   DS:input_fault_voltage:GAUGE:30:0:250 \
#   DS:output_voltage:GAUGE:30:0:250 \
#   DS:output_load:GAUGE:30:0:100 \
#   DS:output_frequency:GAUGE:30:0:70 \
#   DS:battery_voltage:GAUGE:30:0:60 \
#   DS:temperature:GAUGE:30:0:50 \
#   RRA:AVERAGE:0.5:6:43200 \
#   RRA:AVERAGE:0.5:360:175320
#
# Order:
#   input_voltage,input_fault_voltage,output_voltage,output_load,output_frequency,battery_voltage,temperature
#


import rrdtool
from constants import BASE_PATH

FILE_EP3000 = BASE_PATH + '/rrd/ep3000.rrd'


def update_ep3000(payload):
    values = 'N:%s:%s:%s:%s:%s:%s:%s' % (
        payload.input_voltage,
        payload.input_fault_voltage,
        payload.output_voltage,
        payload.output_load,
        payload.output_frequency,
        payload.battery_voltage,
        payload.temperature,
    )
    rrdtool.update(FILE_EP3000, values)

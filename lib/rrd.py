#!/usr/bin/env python
# coding=utf-8

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
TMP_PATH = BASE_PATH + '/tmp'

EP3000_DATA_NAMES = (
    {'name': 'input_voltage', 'unit': 'V', 'label': 'Input Voltage', 'color': '#276000', 'group': 'voltages'},
    {'name': 'input_fault_voltage', 'unit': 'V', 'label': 'Input Fault Voltage', 'color': '#9AFB00',
     'group': 'voltages'},
    {'name': 'output_voltage', 'unit': 'V', 'label': 'Output Voltage', 'color': '#A20B02', 'group': 'voltages'},
    {'name': 'output_load', 'unit': '%', 'label': 'Load Percent', 'color': '#FB6600', 'group': 'others'},
    {'name': 'output_frequency', 'unit': 'Hz', 'label': 'Output Frequency', 'color': '#D16502', 'group': 'others'},
    {'name': 'battery_voltage', 'unit': 'V', 'label': 'Battery Voltage', 'color': '#09629E', 'group': 'voltages'},
    {'name': 'temperature', 'unit': '°C', 'label': 'Temperature', 'color': '#9500FC', 'group': 'others'},
)

EP3000_GROUPS = {
    'voltages': {'unit': 'Volts'},
    'others': {'unit': 'Values'},
}


# def create_ep3000():
#     return rrdtool.create(
#         FILE_EP3000,
#         '-s 10',
#         '--no-overwrite',
#         'DS:input_voltage:GAUGE:60:0:250',
#         'DS:input_fault_voltage:GAUGE:60:0:250',
#         'DS:output_voltage:GAUGE:60:0:250',
#         'DS:output_load:GAUGE:60:0:100',
#         'DS:output_frequency:GAUGE:60:0:70',
#         'DS:battery_voltage:GAUGE:60:0:60',
#         'DS:temperature:GAUGE:60:0:50',
#         'RRA:AVERAGE:0.5:6:43200',
#         'RRA:AVERAGE:0.5:360:175320',
#     )


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


def generate_graphs(sched = 'hourly', grouped = False):
    import rrdtool
    if sched == 'weekly':
        period = 'w'
    elif sched == 'daily':
        period = 'd'
    elif sched == 'monthly':
        period = 'm'
    elif sched == 'hourly':
        period = 'h'
    elif sched == 'yearly':
        period = 'y'
    else:
        raise Exception("Unknown range kind: %s" % (sched))

    if grouped:
        for (group, conf) in EP3000_GROUPS.iteritems():
            file = "%s/ep3000-%s-%s.png" % (TMP_PATH, group, sched)
            args = (
                file,
                "--start",
                "-1%s" % (period),
                "--vertical-label=%s" % (conf['unit']),
                "-w 400",
            )
            line = 0
            for ds in EP3000_DATA_NAMES:
                if ds['group'] != group: continue
                line += 1
                name = ds['name']
                args += (
                    "DEF:val_%s=%s:%s:AVERAGE" % (name, FILE_EP3000, name),
                    "LINE%s:val_%s%s:%s " % (line, name, ds['color'], ds['label']),
                    "GPRINT:val_%s:MIN:Min\\: %%4.0lf " % (name),
                    "GPRINT:val_%s:MAX:Max\\: %%4.0lf " % (name),
                    "GPRINT:val_%s:AVERAGE:Avg\\: %%4.0lf " % (name),
                    "COMMENT:\n",
                )
            rrdtool.graph(*args)
            print "Generated %s grouped graph for %s in %s" % (sched, group, file)

    else:
        for ds in EP3000_DATA_NAMES:
            name = ds['name']
            file = "%s/ep3000-%s-%s.png" % (TMP_PATH, name, sched)
            rrdtool.graph(
                file,
                "--start",
                "-1%s" % (period),
                "--vertical-label=%s" % (ds['unit']),
                "-w 400",
                "DEF:val=%s:%s:AVERAGE" % (FILE_EP3000, name),
                "LINE1:val%s:%s" % (ds['color'], ds['label']),
                "GPRINT:val:MIN:Min\\: %4.0lf ",
                "GPRINT:val:MAX:Max\\: %4.0lf ",
                "GPRINT:val:AVERAGE:Avg\\: %4.0lf "
            )
            print "Generated %s graph for %s in %s" % (sched, name, file)

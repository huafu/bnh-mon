#!/usr/bin/env python
# coding=utf-8
import json
import os
import rrdtool
import time

from lib import FILE_EP3K_STATUS, FILE_EP3K_UPS, TMP_PATH, EP3K_DATA_NAMES, EP3K_GROUPS


def create_ep3k_status():
    if os.path.isfile(FILE_EP3K_STATUS):
        raise Exception("File already exists")
    return rrdtool.create(
        FILE_EP3K_STATUS,
        '-s 10',
        '--no-overwrite',
        'DS:input_voltage:GAUGE:60:0:250',
        'DS:input_fault_voltage:GAUGE:60:0:250',
        'DS:output_voltage:GAUGE:60:0:250',
        'DS:output_load:GAUGE:60:0:100',
        'DS:output_frequency:GAUGE:60:0:70',
        'DS:battery_voltage:GAUGE:60:0:60',
        'DS:temperature:GAUGE:60:0:50',
        'RRA:AVERAGE:0.5:6:43200',
        'RRA:AVERAGE:0.5:360:175320',
    )


def create_ep3k_ups():
    if os.path.isfile(FILE_EP3K_UPS):
        raise Exception("File already exists")
    return rrdtool.create(
        FILE_EP3K_UPS,
        '-s 10',
        '--no-overwrite',
        'DS:rating_voltage:GAUGE:60:0:250',
        'DS:rating_current:GAUGE:60:0:50',
        'DS:battery_voltage:GAUGE:60:0:60',
        'DS:frequency:GAUGE:60:0:70',
        'RRA:AVERAGE:0.5:6:43200',
        'RRA:AVERAGE:0.5:360:175320',
    )


def update_ep3k(st_payload = None, ups_payload = None):
    if st_payload:
        values = 'N:%s:%s:%s:%s:%s:%s:%s' % (
            st_payload['input_voltage'],
            st_payload['input_fault_voltage'],
            st_payload['output_voltage'],
            st_payload['output_load'],
            st_payload['output_frequency'],
            st_payload['battery_voltage'],
            st_payload['temperature'],
        )
        rrdtool.update(FILE_EP3K_STATUS, values)
    if ups_payload:
        values = 'N:%s:%s:%s:%s' % (
            ups_payload['rating_voltage'],
            ups_payload['rating_current'],
            ups_payload['battery_voltage'],
            ups_payload['frequency'],
        )
        rrdtool.update(FILE_EP3K_UPS, values)


def generate_graphs(sched = 'hourly', grouped = False):
    import rrdtool
    if sched == 'weekly':
        period = '1w'
    elif sched == 'daily':
        period = '1d'
    elif sched == 'monthly':
        period = '1m'
    elif sched == 'hourly':
        period = '2h'
    elif sched == 'yearly':
        period = '1y'
    else:
        raise Exception("Unknown range kind: %s" % (sched))

    if grouped:
        for (group, conf) in EP3K_GROUPS.iteritems():
            file = "%s/ep3000-%s-%s.png" % (TMP_PATH, group, sched)
            args = (
                file,
                "--start", " -%s" % (period),
                "--vertical-label=%s" % (conf['unit']),
                "-w 400",
            )
            line = 0
            for ds in EP3K_DATA_NAMES:
                if ds['group'] != group: continue
                line += 1
                name = ds['name']
                args += (
                    "DEF:val_%s=%s:%s:AVERAGE" % (name, FILE_EP3K_STATUS, name),
                    "LINE%s:val_%s%s:%s " % (line, name, ds['color'], ds['label']),
                    "GPRINT:val_%s:MIN:Min\\: %%4.0lf " % (name),
                    "GPRINT:val_%s:MAX:Max\\: %%4.0lf " % (name),
                    "GPRINT:val_%s:AVERAGE:Avg\\: %%4.0lf " % (name),
                    "COMMENT:\n",
                )
            rrdtool.graph(*args)
            print "Generated %s grouped graph for %s in %s" % (sched, group, file)

    else:
        for ds in EP3K_DATA_NAMES:
            name = ds['name']
            file = "%s/ep3000-%s-%s.png" % (TMP_PATH, name, sched)
            rrdtool.graph(
                file,
                "--start", "-%s" % (period),
                           "--vertical-label=%s" % (ds['unit']),
                "-w 400",
                           "DEF:val=%s:%s:AVERAGE" % (FILE_EP3K_STATUS, name),
                           "LINE1:val%s:%s" % (ds['color'], ds['label']),
                "GPRINT:val:MIN:Min\\: %4.0lf ",
                "GPRINT:val:MAX:Max\\: %4.0lf ",
                "GPRINT:val:AVERAGE:Avg\\: %4.0lf "
            )
            print "Generated %s graph for %s in %s" % (sched, name, file)


def rrd_to_json(start = None, end = int(time.time()), file = None):
    (timeInfo, columns, rows) = rrdtool.fetch(
        FILE_EP3K_STATUS, 'AVERAGE', '-r', '1s', '-s', '-1w'
    )
    rows.pop()  # remove the last datapoint because RRD sometimes gives funky values
    data = {}
    for i, datasource in enumerate(columns):
        values = [row[i] for row in rows]
        if 'timestamps' not in data:
            data['timestamps'] = list(range(*timeInfo))
        data[datasource] = values
    res = []
    found_start = False
    data['timestamps'].pop()
    for i, ts in enumerate(data['timestamps']):
        if not found_start and not data['output_voltage'][i]: continue
        found_start = True
        item = {'timestamp': ts, 'payload': {}}
        for col in columns:
            item['payload'][col] = None if data[col][i] is None else round(data[col][i], 1)
        res.append(item)
    return json.dumps(res)

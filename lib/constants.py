#!/usr/bin/env python
# coding=utf-8
import os

BASE_PATH = os.path.abspath(os.path.realpath(os.path.dirname(__file__)) + '/..')

VIDEO_DEVICE_INDEX = 0
VIDEO_DEVICE_NAME = "Aveo Technology Corp."
DISPLAYS_OFFSET = {
    'x': 108 + 52,
    'y': 85 - 21,
}
DISPLAYS = [
    {'x': 0, 'y': 0, 'width': 249, 'height': 92, 'numbers': 4, 'name': 'top'},
    {'x': -6, 'y': 126, 'width': 281, 'height': 85, 'number': 5, 'name': 'middle'},
    {'x': -8, 'y': 248, 'width': 287, 'height': 84, 'numbers': 5, 'name': 'bottom'},
]
LATESTS_RESULTS_PATH = BASE_PATH + '/public/latests'
FILE_EP3K_STATUS = BASE_PATH + '/rrd/ep3000.rrd'
FILE_EP3K_UPS = BASE_PATH + '/rrd/ep3000-ups.rrd'
TMP_PATH = BASE_PATH + '/public'
EP3K_DATA_NAMES = (
    {'name': 'input_voltage', 'unit': 'V', 'label': 'Input Voltage', 'color': '#276000', 'group': 'voltages'},
    {'name': 'input_fault_voltage', 'unit': 'V', 'label': 'Input Fault Volt.', 'color': '#9AFB00', 'group': 'voltages'},
    {'name': 'output_voltage', 'unit': 'V', 'label': 'Output Voltage', 'color': '#A20B02', 'group': 'voltages'},
    {'name': 'output_load', 'unit': '%', 'label': 'Load Percent', 'color': '#FB6600', 'group': 'others'},
    {'name': 'output_frequency', 'unit': 'Hz', 'label': 'Output Frequency', 'color': '#D16502', 'group': 'others'},
    {'name': 'battery_voltage', 'unit': 'V', 'label': 'Battery Voltage', 'color': '#09629E', 'group': 'others'},
    {'name': 'temperature', 'unit': '°C', 'label': 'Temperature', 'color': '#9500FC', 'group': 'others'},
)
EP3K_GROUPS = {
    'voltages': {'unit': 'Volts'},
    'others': {'unit': 'Values'},
}

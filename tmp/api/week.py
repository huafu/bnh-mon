#!/usr/bin/env python
# coding=utf-8

#from bottle import *

from lib import rrd_to_json


print 'Content-Type: application/json'
print
print rrd_to_json()

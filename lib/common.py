#!/usr/bin/env python
# coding=utf-8
import time


def log(message, kind = 'debug'):
    print "[%s][%s] %s" % (time.strftime('%Y-%m-%d %H:%M:%S'), kind, message)

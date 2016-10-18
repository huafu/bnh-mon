#!/usr/bin/env python

import time


class ObjectDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def log(message, kind = 'debug'):
    print "[%s][%s] %s" % (time.strftime('%Y-%m-%d %H:%M:%S'), kind, message)

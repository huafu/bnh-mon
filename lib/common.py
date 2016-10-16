#!/usr/bin/env python

import threading

from main import exiting_app


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


def set_interval(func, sec):
    def func_wrapper():
        if exiting_app: return
        n = set_interval(func, sec)
        try:
            func()
        except:
            n.cancel()
            raise
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

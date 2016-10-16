#!/usr/bin/env python

import threading
import time

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
    def thread():
        start = time.time()
        next = start + sec
        while not exiting_app:
            func()
            now = time.time()
            if now >= next:
                next = now + (int((now - start) / sec) + 1) * sec
            else:
                time.sleep(next - now)

    t = threading.Thread(target = thread)
    t.start()
    return t

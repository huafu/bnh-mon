#!/usr/bin/env python
# coding=utf-8
from lib import cam2


def main():
    for i in range(3): cam2.test(i)


exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

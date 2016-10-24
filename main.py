#!/usr/bin/env python
# coding=utf-8
import time

import Image

import lib.cam2 as cam2
import cv2


def main():

    # print bound_and_ocr(take_picture())
    # print read_and_parse()
    # print ocr_image(take_picture())
    # print ep3000.StatusCommand().send()['payload']
    # print ep3000.UpsRatingCommand().send()['payload']
    # print create_ep3k_ups()
    # rrd.generate_graphs()
    # rrdtool.fetch(
    #    rrd.FILE_EP3000,
    #    'AVERAGE',
    #    '--start -4h'
    # )
    # rrd_to_json()


exiting_app = False
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exiting_app = True
        raise

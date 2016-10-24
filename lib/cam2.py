#!/usr/bin/env python
# coding=utf-8
import atexit
import subprocess as sp
import time

import cv2
import imutils

from lib import VIDEO_DEVICE_NAME, VIDEO_DEVICE_INDEX, DISPLAYS_OFFSET, DISPLAYS

_video = None


def video_dev():
    global _video
    if _video is None:
        reset_device(find_device())
        time.sleep(.5)
        _video = cv2.VideoCapture(VIDEO_DEVICE_INDEX)
        if not _video.isOpened(): _video.open()
    return _video


@atexit.register
def video_close():
    global _video
    if _video is not None:
        _video.release()


def find_device():
    out = sp.check_output(["lsusb | grep '%s'" % (VIDEO_DEVICE_NAME)], shell = True)
    lines = out.split('\n')
    if len(lines) != 2: return None
    parts = lines[0].split(' ')
    dev = "/dev/bus/usb/%s/%s" % (parts[1], parts[3][:-1])
    # print dev
    return dev


def reset_device(device):
    out = sp.check_output(['sudo', 'usbreset', device])


# def ocr(img):
#     return tesseract.image_to_string(
#         Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
#         lang = "letsgodigital",
#         config = "-psm 7 -c tessedit_char_whitelist=.0123456789"
#     )


def take_picture():
    r = False
    img = None
    cam = video_dev()
    while r is not True: r, img = cam.read()
    img = imutils.rotate(img, 180)
    return img


def grab_display(img, index = 0):
    x = DISPLAYS_OFFSET['x'] + DISPLAYS[index]['x']
    y = DISPLAYS_OFFSET['y'] + DISPLAYS[index]['y']
    w = DISPLAYS[index]['width']
    h = DISPLAYS[index]['height']
    return img[y:y + h, x:x + w]


def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def black_and_white(img):
    (thresh, im_bw) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    return im_bw


def test(which = 0):
    name = DISPLAYS[which]['name']

    im = take_picture()

    im_rgb = grab_display(im, which)
    cv2.imwrite('%s.jpg' % (name), im_rgb)

    im_gray = grayscale(im_rgb)
    cv2.imwrite('%s-gray.jpg' % (name), im_gray)

    im_bw = black_and_white(im_gray)
    cv2.imwrite('%s-bw.jpg' % (name), im_bw)

#!/usr/bin/env python
# coding=utf-8

# night
#   ssocr -d -1 -T -t 90 -n 5 -f white -b black rgb_threshold [file]


# day
#   box 1 & 2
#     ssocr make_mono -p -d 4 -T -o out.jpg test.jpg
#   box 3
#     ssocr


import cv2

# from pytesseract import *
from subprocess import Popen, PIPE

from lib import BASE_PATH
from lib import ocr_image

CAM_PATH = BASE_PATH + '/public/assets/cam'

offset = {
    'x': 108 + 55,
    'y': 85 - 21,
}
rectangles = [
    {'x': 0, 'y': 0, 'width': 249, 'height': 92},
    {'x': -6, 'y': 126, 'width': 281, 'height': 85},
    {'x': -8, 'y': 248, 'width': 287, 'height': 84},
]


def read():
    cam = cv2.VideoCapture(0)
    s, img = cam.read()
    cam.release()
    if s:
        # rotate
        (h, w) = img.shape[:2]
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, 180, 1.0)
        return cv2.warpAffine(img, M, (w, h))


def save(img):
    cv2.imwrite(CAM_PATH + "/cam.jpg", img)


def bound_and_ocr(im):
    idx = 0
    parsed = []
    for rect in rectangles:
        idx += 1
        x = offset['x'] + rect['x']
        y = offset['y'] + rect['y']
        w = rect['width']
        h = rect['height']
        roi = im[y:y + h, x:x + w]

        cv2.imwrite(CAM_PATH + '/box-' + str(idx) + '.jpg', roi)

        parsed.append(ocr2(roi, idx))
        # print proc.returncode, err
    return parsed


def ocr1(img, idx):
    r, buf = cv2.imencode('.jpg', img)
    proc = Popen(
        ["ssocr -d -1 -T -t 35 -n 10 -r 6 -f white -b black rgb_threshold -o %s/out-%s.jpg -" % (CAM_PATH, idx)],
        stdin = PIPE,
        stderr = PIPE,
        stdout = PIPE,
        shell = True
    )
    out, err = proc.communicate(bytearray(buf))
    proc.stdin.close()
    proc.stderr.close()
    proc.stdout.close()
    proc.wait()
    return {'code': proc.returncode, 'error': err, 'value': out[:-1]}


def ocr2(img, idx):
    return {'code': 0, 'value': ocr_image(img), 'error': None}


def read_and_parse():
    im = read()
    if im is None: return
    save(im)
    numbers = bound_and_ocr(im)
    if numbers[0]['code'] != 0 or numbers[1]['code'] != 0 or numbers[2]['code'] != 0:
        print numbers
        return
    v1, v2, v3 = numbers[0]['value'], numbers[1]['value'], numbers[2]['value']
    if v1[::1] == '0' or v1 == '100':
        return {
            'efficiency': float(v1[::1] + '.' + v1[1::]),
            'time': float(v2[::-1] + '.' + v2[-1::]),
            'input_consumption': float(v3[::-1] + '.' + v3[-1::]),
        }
    else:
        return {
            'output_voltage': float(v1[::-1] + '.' + v1[-1::]),
            'output_current': float(v2[::-2] + '.' + v2[-2::]),
            'output_power': float(v3[::-1] + '.' + v3[-1::]),
        }

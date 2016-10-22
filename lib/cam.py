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


offset = {
    'x': 108+55,
    'y': 85-21,
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

        # save
        # cv2.imwrite("cam.jpg", img)


def save(img):
    cv2.imwrite("cam.jpg", img)


def bound(im):
    idx = 0
    parsed = []
    for rect in rectangles:
        idx += 1
        x = offset['x'] + rect['x']
        y = offset['y'] + rect['y']
        w = rect['width']
        h = rect['height']
        roi = im[y:y + h, x:x + w]
        cv2.imwrite('box-' + str(idx) + '.jpg', roi)
        r, buf = cv2.imencode('.jpg', roi)
        proc = Popen(
            ["ssocr -d -1 -T -t 90 -n 5 -f white -b black rgb_threshold -"],
            stdin = PIPE,
            stderr = PIPE,
            stdout = PIPE,
            shell = True
        )
        out, err = proc.communicate(bytearray(buf))
        parsed.append(out)
        proc.stdin.close()
        proc.stderr.close()
        proc.stdout.close()
        proc.wait()
        #print proc.returncode, err
    return parsed

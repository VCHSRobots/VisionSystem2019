import cv2
import time
import imutils
from imutils.video import VideoStream

def test(maxnum):
    vs = [cv2.VideoCapture(num) for num in range(maxnum)]
    time.sleep(4)
    try:
        while True:
            for ind, v in enumerate(vs):
                print(v.grab(), ind)
                cv2.waitKey(20)
                time.sleep(.4)
    finally:
        for v in vs:
            v.release()

def releasetest(maxnum):
    inds = list(range(maxnum))
    try:
        while True:
            for ind in inds:
                v = cv2.VideoCapture(ind)
                time.sleep(.1)
                print(v.grab(), ind)
                v.release()
    finally:
        v.release()

def readcam(num):
    v = cv2.VideoCapture(num)
    try:
        while True:
            print(v.grab(), num)
            cv2.waitKey(1)
    finally:
        v.release()

def getThreads(maxnum):
    for num in range(maxnum):
        yield VideoStream(src=num)

def imtest(maxnum):
    threads = getThreads(maxnum)
    for thread in threads:
        thread.start()
    while True:
        for ind, thread in enumerate(threads):
            print(stream.read(), ind)

if __name__ == "__main__":
    test(1)

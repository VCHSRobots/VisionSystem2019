#threads.py: Handles threading for paralell image processing
#1/29/2019 HP

#import comsock
import threading
import cv2
from queue import Queue

"""
class SocketThread(threading.Thread):
  def __init__(self, threadID, name, counter, timeout = 180):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.timeout = timeout

  def run(self):
    comsock.mainloop(self.timeout)
"""

class VideoThread(threading.Thread):
  def __init__(self, camnum, threadID=0, counter=0, name=""):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.timeout = timeout
    self.camera = cv2.VideoCapture(camnum)
    self.queue = Queue(100000)

  def run(self):
    while True:
      img = self.camera.read()
      img = self.processImg(img)
      if not self.queue.full():
        self.queue.put(img)

  def processImg(self, img):
    img = imutils.resize(img, width = camvals["width"], height = camvals["height"])
    img = cv2.cvtColor(img, camvals["color"])
    img = Image.fromarray(img)
    imgbytes = io.BytesIO()
    img.save(imgbytes, format = "JPEG", quality=camvals["quality"])
    imgbytes = imgbytes.getvalue()
    imgbytes = zlib.compress(imgbytes, camvals["compression"])
    return imgbytes

#threads.py: Handles threading for paralell image processing
#1/29/2019 HP

#import comsock
import threading
import cv2
import imutils
import time
import io
import zlib
from queue import Queue
from PIL import Image
from networktables import NetworkTables as nt

RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
dwidth = 400
dheight = 400
defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}
intvals = ["width", "height", "compression", "quality"]
failure_tolerance = 4
timeout = .05
nt.startClient("frc_4415_roborio.local")
connected = nt.isConnected()
table = nt.getTable("/vision")

#Unused in favor of NetworkTables
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
  def __init__(self, camnum, camind, camqueue, msgqueue, threadID=0, counter=0, name=""):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.timeout = timeout
    self.camnum = camnum
    self.camera = cv2.VideoCapture(camind)
    self.camqueue = camqueue
    self.msgqueue = msgqueue
    self.lastqueuesize = 0
    self.lasttimesent = 0
    self.failures = 0

  def run(self):
    self.lasttimesent = time.perf_counter()
    while True:
      if self.failures >= failure_tolerance:
        break
      msg = readQueueWithTimeout(self.msgqueue)
      if msg == b"stop":
        break
      camvals = self.pollCamVars()
      if camvals["isactive"] and (time.perf_counter()-self.lasttimesent) >= 1/camvals["framerate"]:
        if self.failures > 0:
          self.failures = 0
        ret, img = self.camera.read()
        if ret:
          img = self.processImg(img, camvals)
          if not self.camqueue.full():
            self.camqueue.put(img)
            self.lasttimesent = time.perf_counter()
        else:
          self.failures += 1
    self.shutdown()
    
  def shutdown(self):
    self.camera.release()
    self.msgqueue.put(b"dead")
    
  def processImg(self, img, camvals):
    img = imutils.resize(img, width = camvals["width"], height = camvals["height"])
    img = cv2.cvtColor(img, camvals["color"])
    img = Image.fromarray(img)
    imgbytes = io.BytesIO()
    img.save(imgbytes, format = "JPEG", quality=camvals["quality"])
    imgbytes = imgbytes.getvalue()
    imgbytes = zlib.compress(imgbytes, camvals["compression"])
    return imgbytes
    
  def pollCamVars(self):
    """
    Recieves NetworkTables variables for the specified camera number
    """
    vals = self.pollTableVals()
    if vals["color"] == True:
      vals["color"] = RGB
    elif vals["color"] == False:
      vals["color"] = GRAY
    else:
      vals["color"] = RGB
    for key in intvals:
      vals[key] = int(vals[key])
    return vals
  
  def pollTableVals(self):
    """
    Gets camera values for given camnum from NetworkTables
    """
    vals = {}
    for key in defaultcamvals:
      valtype = type(defaultcamvals[key])
      if valtype == int or valtype == float:
        vals[key] = table.getNumber("{}{}".format(self.camnum, key), defaultcamvals[key])
      elif valtype == bool:
        vals[key] = table.getBoolean("{}{}".format(self.camnum, key), defaultcamvals[key])
    return vals
  
def readQueueWithTimeout(queue):
  try:
    item = queue.get(timeout=.05)
    return item
  except queue.Empty:
    return b""
  

def readQueueNoWait(queue):
  try:
    item = queue.get_nowait(timeout=.05)
    return item
  except queue.Empty:
    return b""

#threads.py: Handles threading for paralell image processing
#1/29/2019 HP

#import comsock
import threading
import cv2
import time
from queue import Queue

defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}
failure_tolerance = 4

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
  def __init__(self, camnum, queue, threadID=0, counter=0, name=""):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.timeout = timeout
    self.camnum = camnum
    self.camera = cv2.VideoCapture(camnum)
    self.queue = queue
    self.lastqueuesize = 0
    self.lasttimesent = 0
    self.failures = 0

  def run(self):
    self.lasttimesent = time.perf_counter()
    while True:
      if self.failures >= failure_tolerance:
        break
      if self.queue.qsize() > self.lastqueuesize:
        msg = readQueueWithTimeout(self.queue)
        if msg == b"stop":
          break
      camvals = processImg(img, defaultcamvals)
      if camvals["isactive"] and (time.perf_counter()-self.lasttimesent) >= 1/camvals["framerate"]:
        if self.failures > 0:
          self.failures = 0
        ret, img = self.camera.read()
        if ret:
          img = self.processImg(img)
          if not self.queue.full():
            self.queue.put(img)
            self.lasttimesent = time.perf_counter()
        else:
          self.failures += 1
    self.shutdown()
    
  def shutdown(self):
    self.camera.release()
    self.queue.put(b"dead")
    
  def processImg(self, img, camvals):
    img = imutils.resize(img, width = camvals["width"], height = camvals["height"])
    img = cv2.cvtColor(img, camvals["color"])
    img = Image.fromarray(img)
    imgbytes = io.BytesIO()
    img.save(imgbytes, format = "JPEG", quality=camvals["quality"])
    imgbytes = imgbytes.getvalue()
    imgbytes = zlib.compress(imgbytes, camvals["compression"])
    return imgbytes
    
  def pollCamVars(camnum):
    """
    Recieves NetworkTables variables for the specified camera number
    """
    vals = pollTableVals(self.camnum, defaultcamvals)
    if vals["color"] == True:
      vals["color"] = RGB
    elif vals["color"] == False:
      vals["color"] = GRAY
    else:
      vals["color"] = RGB
    for key in intvals:
      vals[key] = int(vals[key])
    return vals
  
def pollTableVals(camnum, keys):
  """
  Gets camera values for given camnum from NetworkTables
  """
  vals = {}
  for key in keys:
    valtype = type(keys[key])
    if valtype == int or valtype == float:
      vals[key] = table.getNumber("{0}{1}".format(camnum, key), keys[key])
    elif valtype == bool:
      vals[key] = table.getBoolean("{0}{1}".format(camnum, key), keys[key])
  return vals
  
def readQueueWithTimeout(queue):
  try:
    item = queue.get(timeout=.05)
    return item
  except queue.Empty:
    return b""
  

#multi.py: Multiprocessing based paralell image processing which uses all processor cores
#2/17/2019 HP

import time
import cv2
import socket
import imutils
import io
import zlib
import queue as queuelib
from PIL import Image
from networktables import NetworkTables as nt
from multiprocessing import Process
from PIL import Image
from queue import Queue
from networktables import NetworkTables as nt

#Globals
RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
dwidth = 400
dheight = 400
cliip = "10.44.15.5"
defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}
intvals = ["width", "height", "compression", "quality"]
failure_tolerance = 8
timeout = .05
nt.startClient("frc_4415_roborio.local")
connected = nt.isConnected()
table = nt.getTable("/vision")

def makeVideoProcess(camnum, camind, camqueue, msgqueue):
  process = Process(target=runVideoProcess, args=(camnum, camind, camqueue, msgqueue))
  return process
  
def makeVideoSenderProcess(camnum, camind, msgqueue):
  process = Process(target=runVideoSender, args=(camnum, camind, msgqueue))
  return process
  
def runVideoProcess(camnum, camind, camqueue, msgqueue):
    lasttimesent = time.perf_counter()
    failures = 0
    paused = False
    camera = cv2.VideoCapture(camind)
    while True:
      if failures >= failure_tolerance:
        break
      msg = readQueueWithTimeout(msgqueue)
      if msg == b"stop":
        break
      elif msg == b"pause":
        paused = True
      elif msg == b"go":
        paused = False
      if paused:
        continue
      camvals = pollCamVars(camnum)
      if True: #camvals["isactive"] and (time.perf_counter()-lasttimesent) >= 1/camvals["framerate"]:
        ret, img = camera.read()
        print(ret, img)
        if ret:
          if failures > 0:
            failures = 0
          img = processImage(img, camvals)
          if not camqueue.full():
            camqueue.put(img)
            lasttimesent = time.perf_counter()
        else:
          failures += 1
    camera.release()
    msgqueue.put(b"dead")
    
def runVideoSender(camnum, camind, msgqueue):
  lasttimesent = time.perf_counter()
  failures = 0
  paused = False
  camera = cv2.VideoCapture(camind)
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    while True:
      if failures >= failure_tolerance:
        break
      msg = readQueueWithTimeout(msgqueue)
      if msg == b"stop":
        break
      elif msg == b"pause":
        paused = True
      elif msg == b"go":
        paused = False
      if paused:
        continue
      camvals = pollCamVars(camnum)
      if True: #camvals["isactive"] and (time.perf_counter()-lasttimesent) >= 1/camvals["framerate"]:
        ret, img = camera.read()
        time.sleep(failures/4)
        print(ret, failures)
        if ret:
          print(ret, img)
          if failures > 0:
            failures = 0
          img = processImage(img, camvals)
          size = sock.sendto(img, (cliip, 5800+camnum))
        else:
          failures += 1
  finally:
     camera.release()
     msgqueue.put(b"dead")

def pollCamVars(camnum):
  """
  Recieves NetworkTables variables for the specified camera number
  """
  vals = pollTableVals(camnum)
  if vals["color"] == True:
    vals["color"] = RGB
  elif vals["color"] == False:
    vals["color"] = GRAY
  else:
    vals["color"] = RGB
  for key in intvals:
    vals[key] = int(vals[key])
  return vals

def pollTableVals(camnum):
  """
  Gets camera values for given camnum from NetworkTables
  """
  vals = {}
  for key in defaultcamvals:
    valtype = type(defaultcamvals[key])
    if valtype == int or valtype == float:
      vals[key] = table.getNumber("{}{}".format(camnum, key), defaultcamvals[key])
    elif valtype == bool:
      vals[key] = table.getBoolean("{}{}".format(camnum, key), defaultcamvals[key])
  return vals

def processImage(img, camvals):
  img = imutils.resize(img, width = camvals["width"], height = camvals["height"])
  img = cv2.cvtColor(img, camvals["color"])
  img = Image.fromarray(img)
  imgbytes = io.BytesIO()
  img.save(imgbytes, format = "JPEG", quality=camvals["quality"])
  imgbytes = imgbytes.getvalue()
  imgbytes = zlib.compress(imgbytes, camvals["compression"])
  return imgbytes

def readQueueWithTimeout(queue):
  try:
    item = queue.get(timeout=.05)
    return item
  except queuelib.Empty:
    return b""
  
def readQueueNoWait(queue):
  try:
    item = queue.get_nowait()
    return item
  except queuelib.Empty:
    return b""
    

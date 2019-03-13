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

from camconfig import makeConfigedCamera as makeCamera

#Globals
RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
dwidth = 320
dheight = 240
cliip = "10.44.15.5"
ip = "10.44.15.6"
defaultcamvals = {"isactive": True, "width": dwidth, "height": dheight, "color": True, "quality": 24}
intvals = ["width", "height", "compression", "quality"]
failure_tolerance = 8
timeout = .05
nt.startClient("frc_4415_roborio.local")
connected = nt.isConnected()
table = nt.getTable("/vision")

def videoProcess(camera, camnum, msgqueue):
  process = Process(target=processVideo, args=(camera, camnum, msgqueue))

def makeVideoProcess(camnum, camind, camqueue, msgqueue):
  process = Process(target=runVideoProcess, args=(camnum, camind, camqueue, msgqueue))
  return process
  
def makeVideoSenderProcess(camnum, camind, msgqueue):
  process = Process(target=runVideoSender, args=(camnum, camind, msgqueue))
  return process
  
def processVideo(camera, camnum, msgqueue):
  properties = {"quality": 28}
  failures = 0
  paused = False
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  while True:
    if failures >= failure_tolerance:
      break
    #Processes messages from parent
    msg = readQueueWithTimeout(msgqueue)
    #If the parent told the child to stop or a related child died
    if msg == b"":
      pass
    elif msg == b"stop" or msg == b"dead":
      break
    elif msg == b"pause":
      paused = True
    elif msg == b"go":
      paused = False
    else:
      words = msg.decode().split()
      if words[0] == "set":
        if words[1] in properties:
          properties[words[1]] = convert(words[2])
    if paused:
      continue
    camvals = pollCamVars(camnum)
    if True:
      ret, img = camera.read()
      if ret:
        if failures > 0:
          failures = 0
        img = processImage(img, properties)
        sock.sendto(img, (cliip, 5800+camnum))
      else:
        failures += 1
  msgqueue.put(b"dead")

def convert(obj):
  if obj.lower() == "true":
    return True
  elif obj.lower() == "false":
    return False
  else:
    try:
      return float(obj)
    except ValueError:
      return obj

def runVideoProcess(camnum, camind, camqueue, msgqueue):
    lasttimesent = time.perf_counter()
    failures = 0
    paused = False
    camera = makeCamera(camind)
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
  camera = makeCamera(camind)
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
  img = Image.fromarray(img)
  imgbytes = io.BytesIO()
  img.save(imgbytes, format = "JPEG", quality=camvals["quality"])
  imgbytes = imgbytes.getvalue()
  #imgbytes = zlib.compress(imgbytes, camvals["compression"])
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
    

#camconfig.py: Process which configures given cameras and listens on a socket for configuration updates
#2/17/2019 HP

import cv2
import queue as queuelib
from networktables import Networktables as nt
from multiprocessing import Process

properties = ["quality", "compression"]
camsettings = ["width", "height", "framerate", "color"]

def connectToNetworkTables():
  while not nt.isConnected:
    nt.startClient("roboRIO-4415-frc.local")

def makeConfigProcess(cams, queues):
  process = Process(target = configCams, args = (cams, queues))
  return process

def configCams(cams, queues):
  connectToNetworkTables()
  lastcamvals = {num: {} for num in cams}
  while True:
    for num in cams:
      camvals = pollCamVars(num)
      newvals = excludeDictOverlap(camvals, lastcamvals[num])
      for val in newvals:
        if val in properties:
          queues[num].put("set {} {}".format(val, newvals[val]).encode())
        elif val in camsettings:
          if val == "width":
            cams[num].set(3, convert(newvals[val], True))
          elif val == "height":
            cams[num].set(4, convert(newvals[val], True))
          elif val == "framerate":
            cams[num].set(5, convert(newvals[val], True))
          elif val == "color":
            cams[num].set(16, convert(newvals[val]))
  for num in cams:
    cams[num].release()
    queues[num].put(b"stop")

def convert(obj, intbias=False):
  if obj.lower() == "true":
    return True
  elif obj.lower() == "false":
    return False
  else:
    try:
      if intbias:
        return int(obj)
      else:
        return float(obj)
    except ValueError:
      return obj

def excludeDictOverlap(dict1, dict2):
  #Removes all values in dict1 which have duplicates in dict2
  keys = list(dict1.keys())
  for key in keys:
    if key in dict2:
      if dict1[key] == dict2[key]:
        dict1.pop(key)
  return dict1

def makeConfigedCamera(ind, width=320, height=240, fps=25, color=1):
  camera = cv2.VideoCapture(ind)
  setResolution(camera, width, height)
  setFps(camera, fps)
  setColor(camera, color)
  return camera

def setResolution(camera, width, height):
  camera.set(3, width)
  camera.set(4, height)

def setFps(camera, fps):
  camera.set(5, fps)

def setColor(camera, rgb):
  camera.set(16, rgb)

def readQueueWithTimeout(queue, timeout = .05):
  try:
    item = queue.get(timeout=timeout)
    return item
  except queuelib.Empty:
    return b""
  
def writeToQueue(queue, item, timeout = .05):
  if not queue.full():
    try:
      queue.put(item, timeout=timeout)
      return True
    except queuelib.Full:
      return False
  else:
    return False

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

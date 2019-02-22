#pinet.py: Minimalistic version of the Vision System for loading on the pi
#2/20/2019 HP

#Module Imports
import time
import socket
import imutils
import zlib
import cv2
import io
import sys
import queue as queuelib
import numpy as np
from PIL import Image
from networktables import NetworkTables as nt

import stdreader

#Globals
TCP = socket.SOCK_STREAM
UDP = socket.SOCK_DGRAM
RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
#Driver station must be configured to 10.44.15.5
cliip = "10.44.15.5"
piip = "10.44.15.6"
myadr = (piip, 5800)
dwidth = 400
dheight = 400
defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}
default_match_time = 180
#Camera value keys which need to be cast to integers
intvals = ["width", "height", "compression", "quality"]
robotip = "roborio-4415-frc.local"
nt.initialize(robotip)
table = nt.getTable("/vision")

def setupSenderSocket(socktype = UDP, timeout = .05):
  """
  Sets up and returns a ready to use socket bound to the ip and port arguments
  """
  sock = socket.socket(socket.AF_INET, socktype)
  sock.bind(myadr)
  sock.settimeout(.05)
  return sock

def setupListenerSocket(socktype = UDP, timeout = .05):
  """
  Sets up and returns a ready to use socket bound to the ip and port arguments
  """
  sock = socket.socket(socket.AF_INET, socktype)
  sock.settimeout(.05)
  return sock
  
def runSingleMatch(camnum):
  sock = setupListenerSocket()
  try:
    camera = configSingle(listener=socket)
  finally:
    sock.close()
  sock = setupSenderSocket()
  exportCamStream(sock, camnum, camera)
  
def exportCamStream(sock, camnum, camera, socktype = UDP, time = 180):
  """
  Exports a stream of images from the given camera
  """
  starttime = time.perf_counter()
  lastimesent = 0
  #The last time since diagnostic data was printed
  lastimesincediag = 0
  framesent = 0
  totalsize = 0
  while time.perf_counter()-starttime <= time:
    camvals = pollCamVars(camnum)
    #Casts certain numerical camera values to integer
    for key in intvals:
      camvals[key] = int(camvals[key])
    if camvals["isactive"] and time.perf_counter()-lastimesent >= 1/camvals["framerate"]: #If camera is active and framerate time has passed
      size = exportImage(camera=camera, camnum=num, sock=sock, camvals=camvals, ip=ip)
      if size == -1:
        continue
      totalsize += size
      framesent += 1
      lastimesent = time.perf_counter()
    if time.perf_counter()-lastimesincediag >= 10:
      bytespersec = totalsize/10
      fps = framesent/10
      print("{0} frames sent at {1}fps. Average image size: {2}".format(framesent, fps, bytespersec*8/1000000))
      framesent = 0
      totalsize = 0
      lastimesincediag = time.perf_counter()
  if cv2.waitKey(1) == 0:
    break
  if timeout:
    if time.perf_counter()-starttime > timeout:
      break
        
def exportImage(camera, camnum, sock, camvals=defaultcamvals, ip=cliip):
  """
  Reads, sterilizes, and exports an image from the OpenCV camera
  """
  isworking, frame = camera.read()
  if not isworking:
    return -1
  frame = processImg(frame, camvals)
  #Checks if size of image is bigger than the reciever buffer can handle
  if sys.getsizeof(frame) > table.getNumber("{0}size".format(camnum), 50000):
    defaultsize = table.getNumber("{0}size".format(camnum), 50000)
    sizedif = sys.getsizeof(frame)-defaultsize
    table.putNumber("{0}overflow".format(camnum), sizedif) #Warns client about NetworkTables update if about to send an image larger than the default buffer
    return #Skip sending frame until client confirms it can recieve the larger size
  return sock.sendto(frame, (cliip, camnum+5800))
        
def processImg(img, camvals):
  """
  Processes an image from numpy array format to jpeg bytes blob
  """
  img = imutils.resize(img, width = camvals["width"], height = camvals["height"])
  img = cv2.cvtColor(img, camvals["color"])
  img = Image.fromarray(img)
  imgbytes = io.BytesIO()
  img.save(imgbytes, format = "JPEG", quality=camvals["quality"])
  imgbytes = imgbytes.getvalue()
  imgbytes = zlib.compress(imgbytes, camvals["compression"])
  return imgbytes
  
def configSingle(listener):
  #Assumes only one camera is plugged in
  camera = testCameraInd(0)
  sockmessage = b""
  started = False
  while not started and camera != None:
    camnums = stdreader.scanForCameras()
    if camera == None and camnums:
      camera = testCamnum(len(camnums)-1)
    elif not camnums and type(camera) == cv2.VideoCapture:
      #If the camera was unplugged but the object still registers
      camera = None
    elif type(camera) == cv2.VideoCapture:
      #Otherwise, test if camera is alive
      if not testCamera(camera):
        camera = None
    sockmessage = recvWithTimeout(listener)
    started = sockmessage == b"start"
  return camera
  
def testCameraInd(camnum):
  camera = cv2.VideoCapture(camnum)
  if camera.grab():
    return camera
  else:
    return None
  
def testCamera(camera):
  if camera.grab():
    return True
  else:
    return False
    
def pollCamVars(camnum):
  """
  Recieves NetworkTables variables for the specified camera number
  """
  vals = pollTableVals(camnum, defaultcamvals)
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
  #Note: Keys should be key: default pairs
  vals = {}
  for key in keys:
    valtype = type(keys[key])
    if valtype == int or valtype == float:
      vals[key] = table.getNumber("{0}{1}".format(camnum, key), keys[key])
    elif valtype == bool:
      vals[key] = table.getBoolean("{0}{1}".format(camnum, key), keys[key])
  return vals
  

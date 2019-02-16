#ntpinet.py: Reappreciated version of pinet with networktables
#11/17/2018 HP

#Module Imports
import time
import socket
import imutils
import zlib
import cv2
import io
import sys
import numpy as np
from PIL import Image
from networktables import NetworkTables as nt

import stdreader

#Globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM
RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
#Ip is configured to Holiday's laptop and pi... change if neccecary!
cliip = "10.44.15.5"
piip = "10.44.15.6"
myadr = (piip, 5800)
dwidth = 400
dheight = 400
defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}
#Camera value keys which need to be cast to integers
intvals = ["width", "height", "compression", "quality"]
robotip = "roborio-4415-frc.local"
nt.initialize(robotip)
table = nt.getTable("/vision")

def setupSenderSocket(socktype = UTP, timeout = .05):
  """
  Sets up and returns a ready to use socket bound to the ip and port arguments
  """
  sock = socket.socket(socket.AF_INET, socktype)
  sock.bind(myadr)
  sock.settimeout(.05)
  #Not Complete Yet
  #if socktype == TCP:
  #   sock.listen()
  return sock

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
  return sendWithTimeout(sock, frame, (cliip, camnum+5800))

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

def makeCam(camnum):
  """
  Tries to make a camera, fails if it doesn't work
  """
  camera = cv2.VideoCapture(camnum)
  ret, _ = camera.read()
  if ret:
    return camera
  else:
    return False

def findCam(numrange = (0, 100)):
  """
  Scans through numbers within numrange and returns the first unexcluded camera
  """
  cam = False
  for num in range(numrange[0], numrange[1]):
    cam = makeCam(num)
    if cam != False:
      return num, cam

def scanForCams(numrange = (0, 100)):
  """
  Scans through numbers within numrange and returns all found cameras
  """
  cams = {}
  for num in range(numrange[0], numrange[1]):
    cam = makeCam(num)
    if cam != False:
      cams[num] = cam
  return cams

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

def exportManagedStream(sock, cams, ip = cliip, numrange = (0, 10), socktype = UTP, port = 1024, timeout = 0):
  """
  Exports a stream of images with each camera individually managed by its NetworkTables values
  """
  #cams = scanForCams(numrange=(0,10)) #Gets a dict of avalible cams within the number range
  starttime = time.perf_counter()
  timerecords = [[starttime, 0]] * len(cams) #Makes records of when the time was last recorded and how long it's been since the frame was last updated for each camera in (lasttime, framediff) order
  #The last time since diagnostic data was printed
  lastimesincediag = 0
  framesent = 0
  totalsize = 0
  while True:
    for ind, num in enumerate(cams):
      camvals = pollCamVars(num)
      #Casts certain numerical camera values to integer
      for key in intvals:
        camvals[key] = int(camvals[key])
      timerecords[ind][1] += time.perf_counter()-timerecords[ind][0] #Compares current time to time since the last time update to see how much time has passed
      timerecords[ind][0] = time.perf_counter()
      if camvals["isactive"] and timerecords[ind][1] > 1/camvals["framerate"]: #If camera is active and framerate time has passed
        size = exportImage(camera=cams[num], camnum=num, sock=sock, camvals=camvals, ip=ip)
        if size == -1:
            continue
        totalsize += size
        timerecords[ind][1] = 0
        framesent += 1
      if time.perf_counter()-lastimesincediag >= 10:
        bytespersec = totalsize/10
        fps = framesent/10
        print("{0} frames sent at {1}fps. Average image size: {2}".format(framesent, fps, bytespersec*8/1000000))
        framesent = 0
        totalsize = 0
        lastimesincediag = time.perf_counter()
    if cv2.waitKey(20) == 0:
      break
    if timeout:
      if time.perf_counter()-starttime > timeout:
        break

def exportTestStream(sock, cams):
  """
  Exports a single image from each camera in the test stream
  """
  badcams = []
  for num in cams:
    camvals = pollCamVars(num)
    for key in intvals:
      camvals[key] = int(camvals[key])
    if exportImage(cams[num], camnum=num, sock=sock, camvals=camvals) == -1:
      badcams.append(num)
  return badcams

def configMode(sock):
  message = b""
  camdict = {}
  indsused = 0
  while message != b"start":
    #Scans for active cameras and posts them to NetworkTables
    cams = stdreader.scanForCameras()
    badcams = exportTestStream(sock, camdict)
    for camnum in cams:
      table.putBoolean("{0}isactive".format(camnum), True)
      if (not camnum in camdict):
        camdict[camnum] = cv2.VideoCapture(indsused)
        indsused += 1
    print(camdict, indsused)
    for badcam in badcams:
      cam = camdict.pop(badcam)
      cam.release()
      indsused -= 1
    message = recvWithTimeout(sock)
  return camdict

def recvWithTimeout(sock):
  """
  Recieves a message from the given socket and catches error if socket times out
  """
  try:
    message = sock.recv(128)
  except socket.error:
      message = b""
      print("loop passed")
  return message

def sendWithTimeout(sock, msg, adr):
    try:
        return sock.sendto(msg, adr)
    except socket.timeout:
        return -1

def runMatch(time=180):
  sock = setupSenderSocket()
  #Runs in configuration mode until recieving start signal
  try:
    cams = configMode(sock)
    #Exports vision system stream
    exportManagedStream(sock, cams, ip=cliip, timeout=time)
  finally:
    sock.close()
    for camnum in cams:
      cams[camnum].release()

def test(time=180):
  """
  Safe test function of the vision system
  """
  sock = setupSenderSocket()
  #Scans for active cameras and posts them to NetworkTables
  cams = scanForCams(numrange=(0,9))
  for camnum in cams:
    print(table.putBoolean("{0}isactive".format(int(camnum)), True))
    print("Camnum: ", camnum)
    exportImage(cams[camnum], camnum, sock = sock)
  #Exports vision system stream
  try:
    exportManagedStream(sock, cams, ip=cliip, timeout=time)
  finally:
    for camnum in cams:
      cams[camnum].release()

if __name__ == "__main__":
    runMatch()

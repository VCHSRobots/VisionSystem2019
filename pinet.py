#pinet.py: Hosts socket for pi camera using UTP or TCP
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

#Globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM
RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
#Ip is configured to Holiday's laptop and pi... change if neccecary!
ip = "10.44.15.41"
piip = "10.44.15.59"
dwidth = 400
dheight = 400
defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}
#Camera value keys which need to be cast to integers
intvals = ["width", "height", "compression", "quality"]
robotip = "roborio-4415-frc.local"
nt.initialize(robotip)
table = nt.getTable("/vision")

def setupServerSocket(socktype = UTP):
  """
  Sets up and returns a ready to use socket bound to the ip and port arguments. Only needed for tcp
  """
  sock = socket.socket(socket.AF_INET, socktype)
  #Not Complete Yet
  #if socktype == TCP:
  #   sock.listen()
  return sock

def exportImage(camera, camnum, sock, camvals=defaultcamvals, table=None):
  """
  Reads, sterilizes, and exports an image from the OpenCV camera
  """
  _, frame = camera.read()
  frame = processImg(frame, camvals)
  #Checks if size of image is bigger than the reciever buffer can handle
  if table:
    size = sys.getsizeof(frame)
    if sys.getsizeof(frame) > table.getNumber("{0}maxsize".format(camnum), 50000):
      table.putNumber("{0}maxsize".format(camnum), size)
      sock.sendto(b"{0}overload".format(camnum), (ip, 5809)) #Warns client about NetworkTables update if about to send an image larger than the default buffer
  return sock.sendto(frame, (ip, camnum+5800))

def processImg(img, camvals):
  """
  Processes an image from numpy array format to jpeg bytes blob
  """
  img = imutils.resize(img, width = camvals["width"], height = camvals["height"])
  img = cv2.cvtColor(img, camvals["color"])
  img = Image.fromarray(img)
  imgbytes = io.BytesIO()
  img.save(imgbytes, format = "JPEG") #, quality=camvals["quality"])
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

def exportManagedStream(sock, cams, ip = ip, numrange = (0, 10), socktype = UTP, port = 1024, timeout = 0):
  """
  Exports a stream of images with each camera individually managed by its NetworkTables values
  """
  #cams = scanForCams(numrange=(0,10)) #Gets a dict of avalible cams within the number range
  starttime = time.perf_counter()
  timerecords = [[starttime, 0]] * len(cams) #Makes records of when the time was last recorded and how long it's been since the frame was last updated for each camera in (lasttime, framediff) order
  #The last time since diagnostic data was printed
  lastimesincediag = 0
  framesent = 0
  sizes = []
  while True:
    for num in cams:
      camvals = pollCamVars(num)
      #Casts certain numerical camera values to integer
      for key in intvals:
        camvals[key] = int(camvals[key])
      timerecords[num][1] += time.perf_counter()-timerecords[num][0] #Compares current time to time since the last time update to see how much time has passed
      timerecords[num][0] = time.perf_counter()
      if camvals["isactive"] and timerecords[num][1] > 1/camvals["framerate"]: #If camera is active and framerate time has passed
        print("Sent")
        size = exportImage(camera=cams[num], camnum=num, sock=sock, camvals=camvals)
        sizes.append(size)
        timerecords[num][1] = 0
        framesent += 1
      if time.perf_counter()-lastimesincediag >= 10:
        if sizes:
          avgsize = sum(sizes)/len(sizes)
        else:
          avgsize = 0
        fps = framesent/10
        print("{0} frames sent at {1}fps. Average image size: {2}".format(framesent, fps, avgsize))
        sizes.clear()
        framesent = 0
        lastimesincediag = time.perf_counter()
    if cv2.waitKey(1) == 0:
      sock.close()
      break
    if timeout:
      if time.perf_counter()-starttime > timeout:
        sock.close()
        break

def runMatch(time=180):
  sock = setupServerSocket()
  #Scans for active cameras and posts them to NetworkTables
  cams = scanForCams(numrange=(0,9))
  for camnum in cams:
    table.putBoolean("{0}isactive".format(camnum), True)
    exportImage(cams[camnum], camnum, sock = sock, table = table)
  #Opens bound socket and listens for start signal
  listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  listener.bind((piip, 5800))
  listener.recv(1) #Listens for any byte
  listener.close()
  #Exports vision system stream
  exportManagedStream(sock, cams, ip=ip, timeout=time)
  for camnum in cams:
    cams[camnum].release()

def test(time=180):
  """
  Safe test function of the vision system
  """
  sock = setupServerSocket()
  #Scans for active cameras and posts them to NetworkTables
  cams = scanForCams(numrange=(0,9))
  for camnum in cams:
    print(table.putBoolean("{0}isactive".format(int(camnum)), True))
    print("Camnum: ", camnum)
    exportImage(cams[camnum], camnum, sock = sock, table = table)
  #Exports vision system stream
  try:
    exportManagedStream(sock, cams, ip=ip, timeout=time)
  finally:
    for camnum in cams:
      cams[camnum].release()

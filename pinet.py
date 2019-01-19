#pinet.py: Hosts socket for pi camera using UTP or TCP
#11/17/2018 HP

#Module Imports
import time
import socket
import imutils
import zlib
import cv2
import io
import numpy as np
from PIL import Image
from networktables import NetworkTables as nt

#Globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM
RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY
#Ip is configured to Holiday's pi... change if neccecary!
ip = "10.44.15.59"
dwidth = 400
dheight = 400
defaultcamvals = {"isactive": False, "width": dwidth, "height": dheight, "color": True, "framerate": 10, "quantization": 8, "compression": 9, "quality": 95}

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
  Reads, pickles, and exports an image from the OpenCV camera
  """
  _, frame = camera.read()
  frame = processImg(frame, camvals)
  size = sock.sendto(frame, (ip, camnum+5800))
  if table:
    table.putNumber("{0}size".format(camnum), size)


def processImg(img, camvals):
  """
  Processes an image from numpy array format to jpeg butes blob
  """
  img = imutils.resize(width = camvals["width"], height = camvals["height"])
  img = cv2.cvtColor(img, camvals["color"])
  img = Image.fromarray(img)
  #Quantization may or may not be used, since tests proved it might be ineffective at reducing image size
  #img.quantize(camvals["quantization"])
  imgbytes = io.BytesIO()
  img.save(imgbytes, format = "JPEG") #, quality=camvals["quality"])
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

def setupNetworkTable(tablename = "/vision"):
  """
  Sets up networktable client with the specified ip and returns the specified table
  """
  ip = "roborio-4415-frc.local"
  nt.initialize(ip)
  table = nt.getTable(tablename)
  return table

def pollCamVars(camnum, table):
  """
  Recieves NetworkTables variables for the specified camera number
  """
  vals = pollTableVals(camnum, defaultcamvals, table)
  if vals["color"] == True:
    color = RGB
  elif vals["color"] == False:
    color = GRAY
  else:
    color = RGB
  return vals

def pollTableVals(camnum, keys, table):
  #Note: Keys should be key: default pairs
  vals = {}
  for key in keys:
    valtype = type(keys[key])
    if valtype == int or valtype == float:
      vals[key] = table.getNumber("{camnum}{key}".format(camnum, key), keys[key])
    elif valtype == bool:
      vals[key] = table.getBoolean("{camnum}{key}".format(camnum, key), keys[key])
  return vals

"""
#Test Code
def exportStream(camnum, ip, socktype = UTP, port = 1024):

    Starts a stream of pickled images from the camera connected to external port camnum in the specified ip and network port

    sock = setupSocket(ip, socktype, port)
    cam = findCam()
    while True:
        exportImg(cam, sock, port)
        if cv2.waitKey(1) == 0:
            break
"""

def exportManagedStream(sock, cams, table, ip = ip, numrange = (0, 10), socktype = UTP, port = 1024, timeout = 0):
  """
  Exports a stream of images with each camera individually managed by its NetworkTables values
  """
  #cams = scanForCams(numrange=(0,10)) #Gets a dict of avalible cams within the number range
  starttime = time.perf_counter()
  timerecords = [[starttime, 0]] * len(cams) #Makes records of when the time was last recorded and how long it's been since the frame was last updated for each camera in (lasttime, framediff) order
  while True:
    for num in cams:
      camvals = pollCamVars(num, table)
      timerecords[num][1] += time.perf_counter()-timerecords[num][1] #Compares current time to time since the last time update to see how much time has passed
      if active and timerecords[num][1] > 1/camvals["framerate"]: #If camera is active and framerate time has passed
        exportImage(camera=cams[num], camnum=num, socket=sock, camvals=camvals table=table)
    if cv2.waitKey(1) == 0:
      sock.close()
      break
    if timeout:
      if time.perf_counter()-starttime > timeout:
        sock.close()
        break

def runMatch(time=180):
  sock = setupServerSocket()
  #Sets up networktables
  table = setupNetworkTable("/vision")
  #Scans for active cameras and posts them to NetworkTables
  cams = scanForCams(numrange=(0,10))
  for camnum in cams:
    table.putBoolean("{0}isactive".format(camnum), True)
    exportImage(cams[camnum], camnum, sock = sock, table = table)
  #Opens bound socket and listens for start signal
  listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  listener.bind((ip, 5800))
  listener.recv(1) #Listens for any byte
  listener.close()
  #Exports vision system stream
  exportManagedStream(sock, cams, table=table, ip=ip, timeout=time)

def test(time=180):
  camnum = 0
  sock = setupServerSocket()
  #Sets up networktables
  table = setupNetworkTable("/vision")
  #Scans for active cameras and posts them to NetworkTables
  cams = scanForCams(numrange=(0,10))
  for camnum in cams:
    table.putBoolean("{0}isactive".format(camnum), True)
    print("Camnum: ", camnum)
    exportImage(cams[camnum], camnum, sock = sock, table = table)
  #Exports vision system stream
  exportManagedStream(sock, cams, table=table, ip=ip, timeout=time)


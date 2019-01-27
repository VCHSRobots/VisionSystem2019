import imutils
import cv2
import pickle
import socket
import zlib
import io
import time
import numpy as np
from PIL import Image
from networktables import NetworkTables as nt

#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
piip = "10.44.15.59"
adr = (ip, 4000)
piadr = (piip, 4000)
nt.initialize("roborio-4415-frc.local")
table = nt.getTable("/vision")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
maxsize = 100000

def pitest():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  active = False
  camnum = 0
  while not active:
    cam = cv2.VideoCapture(camnum)
    active, _ = cam.read()
    if camnum > 10:
      raise OSError("No Camera Found")
    camnum += 1
  try:
    while True:
      _, frame = cam.read()
      frame = Image.fromarray(frame)
      framebytes = processImg(frame)
      size = sock.sendto(framebytes, adr)
  except KeyboardInterrupt:
    print("Action Interrupted By User")
    raise
  except OSError:
    print("OS Issues encountered!")
    raise
  finally:
    cam.release()

def processImg(img):
  imgbytes = io.BytesIO()
  img.save(imgbytes, format = "JPEG")
  imgbytes = imgbytes.getvalue()
  imgbytes = zlib.compress(imgbytes, 9)
  return imgbytes

def ping():
  sock.bind(adr)
  starttime = time.perf_counter()
  sock.sendto(b"Hello World", piadr)
  d = sock.recv(20)
  endtime = time.perf_counter()
  print("{0}, time = {1}".format(d, endtime-starttime))

def pingback():
  sock.bind(piadr)
  d = sock.recv(20)
  sock.sendto(d, adr)

def clitest():
  #Size variable can be eliminated: recv reads to end of buffer
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(adr)
  framespast = 0
  startime = time.perf_counter()
  try:
    while True:
      image = sock.recv(maxsize)
      table.putBoolean("0isread", True)
      image = zlib.decompress(image)
      image = io.BytesIO(image)
      image = Image.open(image)
      image = np.asarray(image)
      cv2.imshow("img", image)
      cv2.waitKey(1)
      framespast += 1
      print("fps: {0}".format(framespast/(time.perf_counter()-startime)))
  except KeyboardInterrupt:
    print("Action Interrupted By User")
  except OSError:
    print("Windows OS issues encountered!")
    raise
  finally:
    sock.close()
    cv2.destroyAllWindows()


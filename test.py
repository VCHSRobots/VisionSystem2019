import imutils
import cv2
import pickle
import socket
import zlib
import io
import numpy as np
from PIL import Image, ImageTk
from networktables import NetworkTables as nt

#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
adr = (ip, 4000)
nt.initialize("roborio-4415-frc.local")
table = nt.getTable("/vision")

def pitest():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  cam = cv2.VideoCapture(0)
  while True:
    _, frame = cam.read()
    frame = Image.fromarray(frame)
    frame.quantize(8)
    framebytes = io.BytesIO()
    frame.save(framebytes, quality=95)
    framebytes = framebytes.getvalue()
    framebytes = zlib.compress(framebytes, 9)
    size = sock.sendto(framebytes, adr)
    table.putNumber("0size", size)

def clitest():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(adr)
  try:
    while True:
      size = int(table.getNumber("0size", 0))
      if size:
        image = sock.recv(size)
        image = zlib.decompress(image)
        image = io.BytesIO(image)
        image = Image.open(image)
        image = np.asarray(image)
        print(image)
        cv2.imshow("img", image)
        cv2.waitKey(1)
  except KeyboardInterrupt:
    print("Action Interrupted By User")
  finally:
    sock.close()


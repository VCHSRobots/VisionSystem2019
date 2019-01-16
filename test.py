import imutils
import cv2
import pickle
import socket
from networktables import NetworkTables as nt

ntip = "10.44.15.1"
adr = ("10.44.15.41", 4000)
nt.initialize(ntip)
table = nt.getTable("/vision")

def pitest():
  sock = socket.socket(socket.AF_INET, socket.AF_DGRAM)
  cam = cv2.videoCapture(0)
    while True:
      _, frame = cam.read()
      frame = pickle.dumps()
      size = sock.sendto(frame, adr)
      table.putNumber("0size", size)
      if cv2.waitKey(1) == 1:
          break

def clitest():
  sock = socket.socket(socket.AF_INET, socket.AF_DGRAM)
  sock.bind(adr)
  while True:
    size = table.getNumber("0size", 0)
    if size:
      image = sock.recv(size)
      image = pickle.loads(image)
      cv2.imshow("img", image)
      cv2.waitKey(1)


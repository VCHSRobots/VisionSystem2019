import imutils
import cv2
import pickle
import socket
import zlib
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
    frame = pickle.dumps(frame)
    size = sock.sendto(frame, adr)
    table.putNumber("0size", size)
    cv2.waitKey(1)

def clitest():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(adr)
  try:
    while True:
      size = int(table.getNumber("0size", 0))
      if size:
        image = sock.recv(size)
        image = zlib.decompress(image)
        image = pickle.loads(image)
        print(image)
        cv2.imshow("img", image)
        cv2.waitKey(1)
  except KeyboardInterrupt:
    print("Action Interrupted By User")
  finally:
    sock.close()


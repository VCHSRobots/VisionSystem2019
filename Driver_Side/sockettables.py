#sockettables.py: The api for a socket-based NetworkTables Substitute
#1/29/2019 HP

import socket
import threading
import comsock

from visglobals import myadr, internadr
#Myadr is the address of the running client
#Internadr is this api's address

UDP = socket.SOCK_DGRAM
TCP = socket.SOCK_STREAM

class SocketTable:
  def __init__(self, socktype = UDP):
    self.socket = socket.socket(socket.AF_INET, socktype)
    self.socket.bind(interadr)
    
  def startSocketTables():
    thread = threading.thread(comsock.mainloop)
    thread.run()
    
  def putValue(self, key, value):
    self.socket.sendto(b"put {}: {}".format(key, number), myadr)
    
  def putTable(self, name):
    pass
    
  def getString(self, key):
    self.socket.sendto(key.encode(), myadr)
    bytestring = self.socket.recv(254)
    return str(bytestring)
    
  def getNumber(self, decimal = True):
    self.socket.sendto(key.encode(), myadr)
    bytestring = self.socket.recv(254)
    if decimal:
      number = double(bytestring)
    else:
      number = int(bytestring)
    return number
    
  def setMaxSize(self, size):
    self.socket.sendto(b"set maxsize: {}".format(size), myadr)
    

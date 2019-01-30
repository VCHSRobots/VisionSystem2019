#sockettables.py: The api for a socket-based NetworkTables Substitute
#1/29/2019 HP

#Module Imports
import socket
import logs
import sys

#Local Imports
import threads

myip = "10.44.15.62"
deskip = "10.44.15.41"
myadr = (myip, 5809)
internadr = (myip, 5810)
deskadr = (deskip, 5809)
timeout = 180

UDP = socket.SOCK_DGRAM
TCP = socket.SOCK_STREAM

class SocketTable:
  def __init__(self, socktype = UDP):
    self.socket = socket.socket(socket.AF_INET, socktype)
    self.socket.bind(internadr)
    self.thread = threads.SocketThread(1, "", 1, timeout = timeout)

  def startSocketTables(self):
    self.thread.start()
    
  def putNumber(self, key, value):
    string = "put {}: {}".format(key, value).encode()
    print(string, myadr)
    return self.socket.sendto(string, myadr)
    
  def putString(self, key, value):
    string = "put {}: {}".format(key, value).encode()
    print(string, myadr)
    return self.socket.sendto(string, myadr)

  def putBoolean(self, key, value):
    string = "put {}: {}".format(key, value).encode()
    print(string, myadr)
    return self.socket.sendto(string, myadr)
  
  def putTable(self, name):
    pass
    
  def getString(self, key, default = ""):
    self.socket.sendto(key.encode(), myadr)
    bytestring = self.socket.recv(1024)
    return bytestring.decode()
    
  def getNumber(self, key, default = 0, decimal = True):
    self.socket.sendto(key.encode(), myadr)
    bytestring = self.socket.recv(1024) #No foreseeable message will excede this size!
    try:
      if decimal:
        number = float(bytestring.decode())
      else:
        number = int(bytestring.decode())
    except ValueError:
      number = default
    return number

  def getBoolean(self, key, default = False):
    self.socket.sendto(key.encode(), myadr)
    string = self.socket.recv(1024).decode()
    if string == "True":
      return True
    elif string == "False":
      return False
    else:
      return default

  def getTable(self, key):
    pass
    
  def setMaxSize(self, size):
    self.socket.sendto(b"set maxsize: {}".format(size), myadr)
  


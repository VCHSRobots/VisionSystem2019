#sockettables.py: The api for a socket-based NetworkTables Substitute
#1/29/2019 HP

import socket
import threads
import queue

from visglobals import myadr, internadr
#Myadr is the address of the running client
#Internadr is this api's address

timeout = 180

UDP = socket.SOCK_DGRAM
TCP = socket.SOCK_STREAM

class SocketTable:
  def __init__(self, socktype = UDP):
    # self.socket = socket.socket(socket.AF_INET, socktype)
    # self.socket.bind(internadr)
    self.q = queue.Queue()
    self.thread = threads.SocketThread(1, "", 1, timeout = timeout)

  def startSocketTables(self):
    self.thread.start()
    
  def putNumber(self, key, value):
    string = "put {}: {}".format(key, value).encode()
    print(string, myadr)
    self.q.sendto(string, myadr)
    
  def putString(self, key, value):
    string = "put {}: {}".format(key, value).encode()
    print(string, myadr)
    self.q.sendto(string, myadr)

  def putBoolean(self, key, value):
    string = "put {}: {}".format(key, value).encode()
    print(string, myadr)
    self.q.sendto(string, myadr)
  
  #Queue implementing left off here
  def putTable(self, name):
    pass
    
  def getString(self, key, default = ""):
    self.q.sendto(key.encode(), myadr)
    bytestring = self.q.recv(1024)
    return bytestring.decode()
    
  def getNumber(self, key, default = 0, decimal = True):
    self.q.sendto(key.encode(), myadr)
    bytestring = self.q.recv(1024) #No foreseeable message will excede this size!
    try:
      if decimal:
        number = float(bytestring.decode())
      else:
        number = int(bytestring.decode())
    except ValueError:
      number = default
    return number

  def getBoolean(self, key, default = False):
    self.qq.sendto(key.encode(), myadr)
    string = self.q.recv(1024).decode()
    if string == "True":
      return True
    elif string == "False":
      return False
    else:
      return default

  def getTable(self, key):
    pass
    
  def setMaxSize(self, size):
    self.q.sendto(b"set buffersize: {}".format(size))
    
def test():
  table = SocketTable()
  table.startSocketTables()
  print("Here")
  table.putString("Hello", "World")
  print(table.getString("Hello", "World"))

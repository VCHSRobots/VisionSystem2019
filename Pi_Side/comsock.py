#comsock.py: Manages the pi side of the two-way communications socket between the pi and computer because NetworkTables malfunctioned
#1/26/2019 HP

#Module Imports
import socket
import zlib

myip = "10.44.15.62"
internip = ""
deskip = "10.44.15.41"
myadr = (myip, 5809)
internadr = (internip, 4000)
deskadr = (deskip, 5809)

#This library is usually run in a thread which communicates by socket to the main library

#Determines how many bytes both sides listen for
maxmsglength = 254

def makeComSock():
  comsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  comsock.bind(myadr)
  return comsock

def sendValuePair(comsock, key, val, adr = deskadr):
  bytestring = b"{}: {}".format(key, val)
  sendString(comsock, bytestring, adr)

def getValuePair(splitstring):
  key = splitstring[0][:len(splitstring[0])], 
  value = splitstring[1]
  return key, value
  
def sendString(comsock, string, adr = deskadr):
  bytestring = string.encode()
  comsock.sendto(bytestring, comsock)

def recvString(comsock):
  global messages
  bytestring = comsock.recv(maxmsglength)
  string = str(bytestring)
  return string
  
def getMsgLen(comsock, adr = deskadr):
  len = int(echo(comsock, adr))
  return int(len)
  
def echo(comsock, adr = deskadr):
  msg = comsock.recvfrom(maxmsglength)
  comsock.sendto(msg, adr)
  return msg

def mainloop():
  messages = {}
  comsock = makeComSock()
  getMsgLen()
  while True:
    string = recvString(comsock)
    splitstring = string.split()
    #If the string is a request for a value from the internal server
    if len(splitstring) == 1:
      if string in messages:
        comsock.sendto(messages[string].encode(), internadr)
      else:
        comsock.sendto(b"", internadr)
    elif len(splitstring) == 2:
      #If string is a key-value assignment pair
      key, value = getValuePair(splitstring)
      messages[key] = value
    elif len(splitstring) == 3:
      #If the string is a key pair assignment from the internal system which needs to be echoed to the desktop
      #EX "put key: val"
      key, value = getValuePair(splitstring[1:])
      sendValuePair(comsock, key, value)
      messages[key] = value
      

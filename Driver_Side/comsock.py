#comsock.py: Manages the two-way communications socket between the pi and computer because NetworkTables malfunctioned
#1/26/2019 HP

#Module Imports
import socket
import sys

#Local Imports
from visglobals import myadr, piadr, internadr

#This library is usually run in a thread which communicates by socket to the main library

#Determines how many bytes both sides listen for
maxmsglength = 254
#Confirms pi knows how long a message can be sent
confsize = 254

def makeComSock():
  comsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  comsock.bind(myadr)
  return comsock

def sendValuePair(comsock, key, val, adr = piadr):
  bytestring = b"{}: {}".format(key, val)
  sendString(comsock, bytestring, adr)

def getValuePair(splitstring):
  key = splitstring[0][:len(splitstring[0])], 
  value = splitstring[1]
  return key, value

def sendString(comsock, string, adr = piadr):
  bytestring = string.encode()
  comsock.sendto(bytestring, adr)

def recvString(comsock):
  global messages
  bytestring = comsock.recv(maxmsglength)
  string = str(bytestring)
  return string

def sendMsgLength(comsock):
  global confsize
  comsock.sendto(b"maxsize: {}".format(maxmsglength), piadr)
  try:
    comsock.setblocking(False)
    recieved = comsock.recv(maxmsglength)
    comsock.setblocking(True)
    confsize = int(recieved)
  except socket.error:
    comsock.setblocking(True)
  
def splitPath(pathstring):
  path = []
  lastind = 0
  for ind, char in enumerate(pathstring):
    if char == "/":
      path.append(lastind, ind)
      lastind = ind+1
  if lastind == 0:
    path.append(pathstring)
  return path
  
def addPath(path, table, clobber = False):
  if len(path) == 1:
    return table[path[-1]]
  else:
    pass
  
def mainloop():
  messages = {}
  comsock = makeComSock()
  sendMsgLength(comsock)
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
      #If string is a key-value assignment pair from another client
      key, value = getValuePair(splitstring)
      messages[key] = value
    elif "/" in splitstring[0]:
      #If the string requests a directory path
      #EX: "table/path"
      #TODO: Currently Incomplete
      path = splitstring[0]
      if "!" in path:
        #An ! at the path end indicates the path should be clobbered if it exists
        #Only the last key will be clobbered if this is set to true
        clobber = True
        path = path[:-1]
      else:
        clobber = False
      path = splitPath(splitstring[0])
      messages = addPath(path, messages, clobber)
    elif splitstring[0] == "put":
      #If the string is a key pair assignment from the internal system which needs to be echoed to the desktop
      #EX "put key: val" or "put key: val /path/to/dict/with/key"
      key, value = getValuePair(splitstring[1:])
      sendValuePair(comsock, key, value)
      messages[key] = value
    elif splitstring[0] == "set":
      #If a tables setting is sent
      putSetting(splitstring[1:])
      

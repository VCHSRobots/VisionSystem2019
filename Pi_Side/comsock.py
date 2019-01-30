#comsock.py: Manages the pi side of the two-way communications socket between the pi and computer because NetworkTables malfunctioned
#1/26/2019 HP

#Module Imports
import socket
import logs
import sys
import time

myip = "10.44.15.62"
deskip = "10.44.15.41"
myadr = (myip, 5809)
internadr = (myip, 5810)
deskadr = (deskip, 5809)

#This library is usually run in a thread which communicates by socket to the main library

settings = {"buffersize": 254}
#Determines how many bytes both sides listen for

def makeComSock():
  comsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  comsock.bind(myadr)
  return comsock

def sendValuePair(comsock, key, val, adr = deskadr):
  bytestring = "{}: {}".format(key, val)
  sendString(comsock, bytestring, adr)

def getValuePair(splitstring):
  key = splitstring[0][:-1]
  value = splitstring[1]
  return key, value

def sendString(comsock, string, adr = deskadr):
  """
  Encodes and sends a string to the specified address
  """
  bytestring = string.encode()
  if sys.getsizeof(bytestring) <= settings["buffersize"]:
    comsock.sendto(bytestring, adr)
  else:
    comsock.sendto(b"", adr)
    logs.log("Message '{}' would have overflowed buffer of size {}. Sending aborted.".format(bytestring.decode(), settings["buffersize"]))

def recvString(comsock):
  print("recieving string")
  try:
    bytestring = comsock.recv(settings["buffersize"])
    string = bytestring.decode()
    return string
  except socket.error as e:
    logs.log("The following socket error was passed over - {}".format(e))

def configure(comsock, setting, value, timeout = .5):
  message = "changed {}: {}".format(setting, value).encode()
  comsock.sendto(message, deskadr)
  try:
    comsock.settimeout(timeout)
    recieved = comsock.recv(settings["buffersize"])
    if recieved == message:
      comsock.setblocking(True)
      return False
    else:
      comsock.setblocking(True)
      return False
  except socket.error:
    logs.log("Unable to confirm setting {} to value {} with peer client with timeout {}".format(setting, value, timeout))
    comsock.setblocking(True)
    return False

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

def changeSetting(setting, value):
  global settings
  if value.isdigit():
    settings[setting] = int(value)
  else:
    settings[setting] = value

def mainloop(timeout):
  print(myadr)
  messages = {}
  comsock = makeComSock()
  #sendMsgLength(comsock)
  starttime = time.perf_counter()
  while starttime - time.perf_counter() < timeout:
    string = recvString(comsock)
    splitstring = string.split()
    if not string:
      continue
    #If the string is a request for a value from the internal server
    if len(splitstring) == 1:
      #Get command is implied if no other arguments
      if string in messages:
        comsock.sendto(messages[string].encode(), internadr)
      else:
        comsock.sendto(b"", internadr)
    elif splitstring[0] == "get":
      #If given an explicit 'get' command
      if splitstring[1] in messages:
        comsock.sendto(messages[splitstring[1]].encode(), internadr)
      else:
        comsock.sendto(b"", internadr)
    elif splitstring[0] == "put":
      #If the string is a key pair assignment from the internal system which needs to be echoed to the desktop
      key, value = getValuePair(splitstring[1:])
      sendValuePair(comsock, key, value)
      messages[key] = value
    elif ":" in splitstring[0]:
      #If string is a key-value assignment pair
      key, value = getValuePair(splitstring)
      messages[key] = value
    elif splitstring[0] == "set":
      #Assume the only thing to be set is the message length
      setting = splitstring[1]
      value = splitstring[2]
      if configure(comsock, setting, value):
        changeSetting(setting, value)
    elif splitstring[0] == "changed":
      comsock.sendto(string.encode(), deskadr)
      setting = splitstring[1]
      value = splitstring[2]
      changeSetting(setting, value)

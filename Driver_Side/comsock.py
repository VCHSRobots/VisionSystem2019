#comsock.py: Manages the two-way communications socket between the pi and computer because NetworkTables malfunctioned
#1/26/2019 HP

#Module Imports
import socket
import zlib

#Local Imports
from visglobals import myadr, piadr, internadr

#This library is usually run in a thread which communicates by socket to the main library

#Determines how many bytes both sides listen for
maxmsglength = 254
#Whether or not messages are compress. Most messages aren't long enough to need this. Off by default
compressed = False
#Confirms that the pi has recieved the compression siginal
confcompressed = False
messages = {}

def makeComSock():
  comsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  comsock.bind(myadr)
  return comsock

def sendString(comsock, str):
  bytestring = bytearray(str)
  if compressed and confcompressed:
    bytestring = zlib.compress(bytestring)
  comsock.sendto(bytestring, comsock)

def recvString(comsock):
  global messages
  bytestring = comsock.recv(maxmsglength)
  if compressed and confcompressed:
    bytestring = zlib.decompress(bytestring)
  string = str(bytestring)
  return string
  

def sendCompressedStatus(comsock):
  global confcompressed
  comsock.sendto(b"compressed: {}".format(), piadr)
  try:
    comsock.setblocking(False)
    recieved = comsock.recv(maxmsglength)
  except socket.error:
    comsock.setblocking(True)
    return
  comsock.setblocking(True)
  confcompressed = bool(recieved)

def mainloop():
  comsock = makeComSock()
  sendCompressedStatus(comsock)
  while True:
    string = recvString(comsock)
    #If string is a key-value pair from the pi
    if len(string) > 1:
      label, value = string.split()
      messages[label[len(label)-1]] = value
    else:
      #If the string is a request for a value
      if string in messages:
        comsock.sendto(bytes(messages[string]), internadr)
      else:
        comsock.sendto(b"no value", internadr)


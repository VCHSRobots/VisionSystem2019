#setvals.py: Configuration program for vision system

import json
from networktables import NetworkTables as nt

table = nt.getTable("/vision")

def tryToConnect():
  while not nt.isConnected():
    print(">> Unable to connect to NetworkTables. Try again?")
    inp = input(">> ")
    if "y" in inp.lower():
      nt.startClient("10.44.15.2")
    else:
      print(">> Abort?")
      inp = input(">> ")
      if "y" in inp.lower():
        exit(0)
  print(">> Vision Setter succesfully connected to NetworkTables")

def autoConnect():
  while not nt.isConnected():
    nt.startClient("10.44.15.2")

def getJson(filename):
  f = open("Nt_Values/{}".format(filename))
  value = json.load(f)
  f.close()
  return value

def loadFile(values, cameras = [0, 1, 2, 3]):
  for camera in cameras:
    for value in values:
      if type(values[value]) == int or type(values[value]) == float:
        table.putNumber("{}{}".format(camera, value), values[value])
      elif type(values[value]) == str:
        table.putString("{}{}".format(camera, value), values[value])
      elif type(values[value]) == bool:
        table.putBoolean("{}{}".format(camera, value), values[value])

def setValue(key, value, camera):
  if value.lower() == "true":
    value = True
  elif value.lower() == "false":
    value = False
  else:
    try:
      value = float(value)
    except ValueError:
      pass
  if type(value) == int or type(value) == float:
    table.putNumber("{}{}".format(camera, key), value)
  elif type(value) == str:
    table.putString("{}{}".format(camera, key), value)
  elif type(value) == bool:
    table.putBoolean("{}{}".format(camera, key), value)

def setGlobalValue(key, value):
  if value.lower() == "true":
    value = True
  elif value.lower() == "false":
    value = False
  else:
    try:
      value = float(value)
    except ValueError:
      pass
  if type(value) == int or type(value) == float:
    table.putNumber(key, value)
  elif type(value) == str:
    table.putString(key, value)
  elif type(value) == bool:
    table.putBoolean(key, value)

def getValue(key, camera):
  number = table.getNumber("{}{}".format(camera, key), None)
  string = table.getNumber("{}{}".format(camera, key), None)
  boolean = table.getBoolean("{}{}".format(camera, key), None)
  if number != None:
    return number
  elif string != None:
    return string
  elif boolean != None:
    return boolean
  else:
    return None

def getGlobalValue(key):
  number = table.getNumber(key, None)
  string = table.getNumber(key, None)
  boolean = table.getBoolean(key, None)
  if number != None:
    return number
  elif string != None:
    return string
  elif boolean != None:
    return boolean
  else:
    return None

def getCamNums(nums):
  cameras = []
  for camnum in nums:
    try:
      cameras.append(int(camnum))
    except ValueError:
      print(">> Invalid camera number {}".format(camnum))
  return cameras

commands = ["get", "set", "load"]
nt.startClient("10.44.15.2")
autoConnect()

if __name__ == "__main__":
  while True:
    if not nt.isConnected():
      autoConnect()
    inp = input(">> ")
    if not inp:
      continue
    words = inp.split()
    command = words[0]
    args = words[1:]
    if command == "load":
      if not args:
        print(">> No arguments provided")
        continue
      filename = args[0]
      cameras = getCamNums(args[:1])
      if not cameras:
        print(">> No valid cameras provided")
        continue
      try:
        values = getJson(filename)
      except FileNotFoundError:
        print(">> No file named {} exists in this directory".format(filename))
        continue
      loadFile(values, cameras)
    elif command == "set":
      if not args:
        print(">> No arguments provided")
        continue
      key = args[0]
      if len(args) == 1:
        print(">> No value provided")
        continue
      value = args[1]
      cameras = getCamNums(args[2:])
      if not cameras:
        setGlobalValue(key, value)
      for camera in cameras:
        setValue(key, value, camera)
    elif command == "get":
      if not args:
        print(">> No arguments provided")
        continue
      key = args[0]
      cameras = getCamNums(args[1:])
      if not cameras:
        value = getGlobalValue(key)
        if value == None:
          print(">> Value '{}' does not exist in global scope".format(key))
        else:
          print(">> {}".format(value))
        continue
      for camera in cameras:
        value = getValue(key, camera)
        if value == None:
          print(">> Value '{}' does not exist for camera {}".format(key, camera))
        else:
          print(">> {}: {}".format(camera, value))
    elif command == "quit":
      exit(0)
    else:
      print(">> {} is not recognized as a command".format(command))

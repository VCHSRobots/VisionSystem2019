#stdreader.py: Parses input from bash lsusb to track hot plugging of cameras
#2/12/2019 HP

import time
import subprocess as sub

def openBashScript(scriptname):
  f = open(scriptname+".sh")
  script = f.read()
  f.close()
  return script

def getStdOutput(script):
  """
  Gets raw encoded stdout output from the given script file
  """
  script = openBashScript(script)
  process = sub.Popen(script, shell=True, executable="/bin/bash", stdout=sub.PIPE)
  #Gives process time to print
  time.sleep(.025)
  output = process.stdout.read()
  return output

def scanForCameras():
  tree = getStdOutput(script="getusbs").decode()
  manufacts = getStdOutput(script="getmans").decode()
  cams = []
  for camnum in range(4):
    if scanForCam(camnum, tree, manufacts):
      cams.append(camnum)
  return cams

def scanForCam(cam, tree, manufacts):
  tree = tree.splitlines()
  #Device number
  dnum = findDeviceInCamPort(cam, tree)
  if dnum == -1:
    return False
  manufact = getDeviceManufacturer(dnum, manufacts)
  if manufact == "045e" or manufact == "05a3":
    return True
  else:
    return False

def getDeviceManufacturer(dnum, manufacts):
  manufact = ""
  deviceid = "Device {:03}".format(int(dnum))
  for line in manufacts.splitlines():
    if deviceid in line:
      manufact = line.split()[5][:4]
      break
  return manufact

def findDeviceInCamPort(cam, tree):
  dnum = -1
  #Checks for a device in the appropriate port
  if cam == 0:
    initsearch = "{} Port 2".format(getPrefix(indents=3))
  elif cam == 1:
    initsearch = "{} Port 3".format(getPrefix(indents=3))
  elif cam == 2:
    initsearch = "{} Port 3".format(getPrefix(indents=2))
  elif cam == 3:
    initsearch = "{} Port 2".format(getPrefix(indents=2))
  for line in tree:
    #Checks if a device is plugged into the port
    if initsearch == line[:len(initsearch)]:
      dnum = line.split()[4][:-1]
      #Checks if the device is a camera with proper specs
      if (not "Class=Video" in line and not "Class=Audio" in line) or (not "480M" in line):
        return -1
  return dnum

def getPrefix(indents):
  """
  Gets the lsusb prefix for the given number of indents
  """
  prefix = "{}|__".format("    "*indents)
  return prefix

#stdreader.py: Parses input from bash lsusb to track hot plugging of cameras
#2/12/2019 HP

import time
import subprocess as sub

#Globals
devNumNames = {6: "Front", 7: "Back", 8: "Left", 9: "Right"}

def openBashScript(scriptname):
  f = open(scriptname+".bat")
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
  time.sleep(.05)
  output = process.stdout.read()
  return output

ttree = """/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=dwc_otg/1p, 480M
    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/4p, 480M
        |__ Port 1: Dev 3, If 0, Class=Hub, Driver=hub/3p, 480M
            |__ Port 1: Dev 7, If 0, Class=Vendor Specific Class, Driver=lan78xx, 480M
            |__ Port 2: Dev 5, If 0, Class=Video, Driver=uvcvideo, 480M
            |__ Port 2: Dev 5, If 1, Class=Video, Driver=uvcvideo, 480M
            |__ Port 2: Dev 5, If 2, Class=Audio, Driver=snd-usb-audio, 480M
            |__ Port 2: Dev 5, If 3, Class=Audio, Driver=snd-usb-audio, 480M
            |__ Port 3: Dev 6, If 0, Class=Video, Driver=uvcvideo, 480M
            |__ Port 3: Dev 6, If 3, Class=Audio, Driver=snd-usb-audio, 480M
            |__ Port 3: Dev 6, If 1, Class=Video, Driver=uvcvideo, 480M
            |__ Port 3: Dev 6, If 2, Class=Audio, Driver=snd-usb-audio, 480M
        |__ Port 2: Dev 4, If 0, Class=Human Interface Device, Driver=usbhid, 1.5M"""

tmanus = """Bus 001 Device 004: ID 046d:c05a Logitech, Inc. M90/M100 Optical Mouse
Bus 001 Device 006: ID 045e:0779 Microsoft Corp. LifeCam HD-3000
Bus 001 Device 005: ID 045e:0779 Microsoft Corp. LifeCam HD-3000
Bus 001 Device 007: ID 0424:7800 Standard Microsystems Corp.
Bus 001 Device 003: ID 0424:2514 Standard Microsystems Corp. USB 2.0 Hub
Bus 001 Device 002: ID 0424:2514 Standard Microsystems Corp. USB 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub"""

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
  if manufact == "045e":
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
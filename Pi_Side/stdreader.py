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
  time.sleep(.1)
  output = process.stdout.read()
  return output

def scanForCameras():
  output = getStdOutput(script="getusbs").decode()
  cams = []
  for camnum in range(4):
    if scanForCam(camnum, output):
      cams.append(camnum)
  return cams

def scanForCam(cam, lsout):
  lsout = lsout.splitlines()
  foundind = -1
  if cam == 0:
    initsearch = "{} Port 2".format(getPrefix(indents=3))
  elif cam == 1:
    initsearch = "{} Port 3".format(getPrefix(indents=3))
  elif cam == 2:
    initsearch = "{} Port 3".format(getPrefix(indents=2))
  elif cam == 3:
    initsearch = "{} Port 2".format(getPrefix(indents=2))
  for ind, line in enumerate(lsout):
    if initsearch == line[:len(initsearch)]:
      foundind = ind
      break
  if foundind == -1:
    return False
  for line in lsout[foundind:foundind+4]:
    if not initsearch in line:
      return False
    if (not "Class=Video" in line and not "Class=Audio" in line) or (not "480M" in line):
      return False
  return True

def getPrefix(indents):
  """
  Gets the lsusb prefix for the given number of indents
  """
  prefix = "{}|__".format("    "*indents)
  return prefix
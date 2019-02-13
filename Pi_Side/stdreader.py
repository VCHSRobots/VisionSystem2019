#stdreader.py: Parses input from bash lsusb to track hot plugging of cameras
#2/12/2019 HP

import time
import subprocess as sub

def openBashScript(scriptname):
  f = open(scriptname+".bat")
  script = f.read()
  f.close()
  return script

def getStdOutput(script):
  script = openBashScript("getusbs")
  process = sub.Popen(script, shell=True, executable="/bin/bash", stdout=sub.PIPE)
  #Gives process time to print
  time.sleep(.1)
  output = process.stdout.read().decode()
  return output
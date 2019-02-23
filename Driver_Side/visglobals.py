#globals.py: Stores globals all files can access
#HP 1/21/2019

import json
import socket
import time
from networktables import NetworkTables as nt

competitioninterface = "onecam"

def openGuiFile(name):
  print(name)
  guifile = open("./Guis/{0}.gui".format(name))
  gui = json.load(guifile)
  guifile.close()
  return gui

def openStackFile(name):
  print(name)
  guifile = open("./Guis/{0}.stack".format(name))
  gui = json.load(guifile)
  guifile.close()
  return gui

def openSetupFile(name):
  print(name)
  guifile = open("./Guis/{0}.setup".format(name))
  gui = json.load(guifile)
  guifile.close()
  return gui

def null():
  pass

#Ip is configured to Holiday's laptop and pi... change if neccecary!
ip = "10.44.15.5"
piip = "10.44.15.6"
piadr = (piip, 5800)
myadr = (ip, 5800)
#Global communications socket
comsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#List of valid widget types
widgettypes = ["camera", "localcamera", 
              "button", "entry", 
              "checkbox", "listbox", 
              "radiobutton", "combobox", 
              "text", "scale"]

#Menu Guis
mapnames = ["mainmenu", "settings", 
            "onecammatch", "multiview", 
            "test", "splitcam",
            "onecam", "fourcam"]

#Loads span parameters for column griding
stacknames = ["configurable"]
guimaps = {name: openGuiFile(name) for name in mapnames}
stackmaps = {name: openStackFile(name) for name in stacknames}

#Loads files which define the contents of a window's stack cache widgets which are gridded accoring to the above stack rules
setupnames = ["splitcam", "onecam", "fourcam"]
setups = {name: openSetupFile(name) for name in setupnames}

#Camera numbers by their name
camnamenums = {"Front": 0, "Back": 1, "Left": 2, "Right": 3}

#NetworkTables
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")

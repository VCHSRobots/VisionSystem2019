#globals.py: Stores globals all files can access
#HP 1/21/2019

import json
import socket
import time
from networktables import NetworkTables as nt

def openGuiFile(name):
  guifile = open("./Guis/{0}.gui".format(name))
  gui = json.load(guifile)
  guifile.close()
  return gui

def null():
  pass

#Ip is configured to Holiday's laptop and pi... change if neccecary!
ip = "10.44.15.41"
piip = "10.44.15.62"
piadr = (piip, 5809)
myadr = (ip, 5809)
internadr = (ip, 5810)
#Global communications socket
comsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#List of valid widget types
widgettypes = ["camera", "localcamera", "button", "entry", "checkbox", "listbox", "radiobutton", "combobox", "textbox" "scale"]

#Menu Guis
mainmenu = openGuiFile("mainmenu")
settingsgui = openGuiFile("settings")
onecammatch = openGuiFile("onecammatch")
guimaps = {"mainmenu": mainmenu, "settings": settingsgui, "onecammatch": onecammatch}

#NetworkTables
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")

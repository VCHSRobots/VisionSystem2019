#configuration.py: Configures the given window with the widgets it depends on
#HP 1/21/2019

import json
import socket
import time

import tkwin as win
import commands
import menus
import visglobals
from visglobals import guimaps, visiontable, camnamenums

#Global dictionary of menu configuration functions
global configwascalled #Tracks which configuration functions have been called
configwascalled = {"mainmenu": False, "settings": False, "match": False, "onecammatch": False, "multiview": False, "test": False}
#Arguments which need to be converted from integers to be passed to getWidgetFromName
intargs = ["camnum", "length", "height", "start?", "end?"]
global commandfuncs

#Interface Configuration Functions
def configureMainMenu(self):
  global configwascalled
  self.addButton(text = "Start Match!", command = self.switchUi, partialarg = "multiview", interface = "mainmenu")
  self.addButton(text = "Exit", command = self.root.quit, interface = "mainmenu")
  configwascalled["mainmenu"] = True

def configureSettingsMenu(self):
  global configwascalled
  configwascalled["settings"] = True

def configureTest(self):
  global configwascalled
  neededcams = [0, 1, 2, 3]
  addCams(self, neededcams=neededcams, interface="test")
  configwascalled["test"] = True

def configureOneCamMatch(self):
  #Configuration only to be called by configureMatchInterfaces
  global configwascalled
  self.addButton("Switch Cam", commands.swapOutCam, partialarg = win.SELF, interface = "onecammatch")
  self.addEntry(interface = "onecammatch")
  configwascalled["onecammatch"] = True

def configureMultiview(self):
  global configwascalled
  # Adds cameras to a 'match' interface then copies them to the proper interface
  # so their duplicate Camera widgets don't try to reinitialize identical sockets
  configureMatchCameras(self)
  copyMatchCameras(self, interface="multiview")
  self.addButton("Select Front", commands.stageFrontCam, interface = "multiview")
  self.addButton("Select Back", commands.stageBackCam, interface = "multiview")
  self.addButton("Select Left", commands.stageLeftCam, interface = "multiview")
  self.addButton("Select Right", commands.stageRightCam, interface = "multiview")
  self.addButton("Select All", commands.stageAllCams, interface = "multiview")
  self.addButton("Select Mains", commands.stageMainCams, interface = "multiview")
  self.addButton("Select Sides", commands.stageSubCams, interface = "multiview")
  self.addButton("Deactivate Cameras", commands.toggleActivity, interface = "multiview")
  self.addButton("Framerate Up", commands.increaseFramerate, interface = "multiview")
  self.addButton("Framerate Down", commands.decreaseFramerate, interface = "multiview")
  self.addButton("Increase Quality", commands.increaseQuality, interface = "multiview")
  self.addButton("Decrease Quality", commands.decreaseQuality, interface = "multiview")
  self.addButton("Black & White", commands.toggleColor, interface = "multiview")
  self.addText("All Cameras Staged", interface = "multiview")
  self.addText("The staged cameras are active", interface = "multiview")
  self.addText("Quality: 4\n(274x365 for main cameras and 137x182 for side cameras)", interface = "multiview")
  self.addText("Color Mode: RGB", interface = "multiview")
  self.addText("Framerate: 4\n(17 for main cameras and 11 for side cameras)", interface = "multiview")
  self.addText("Debug Console", interface = "multiview")
  self.addText("Adjust Framerate", interface = "multiview")
  self.addText("Adjust Quality", interface = "multiview")
  self.addText("EPIC ROBOTZ Vision System: Crowded Interface Edition!", interface = "multiview")
  self.vars["staged"] = self.cameras["multiview"]
  self.vars["isstaged"] = [0, 1, 2, 3]
  self.vars["isactive"] = True
  self.vars["color"] = True
  self.vars["quality"] = 4
  self.vars["framerate"] = 4
  configwascalled["multiview"] = True

def configureMatchCameras(self, neededcams = (0, 1, 2, 3), recams=False):
  """
  Configures the four cameras needed for match interfaces
  """
  #For the most part, an alias of addCams(self, neddedcams=(0,1,2,3), interface='match')
  if recams:
    cams = addCams(self, neededcams=neededcams, interface="match", recams=True) #Though there are many match interfaces, most functions dealing directly with cameras use the global "match" interface
    return cams
  else:
    addCams(self, neededcams, interface="match")

def copyMatchCameras(self, interface):
  self.cameras[interface] = []
  for camera in self.cameras["match"]:
    self.cameras[interface].append(camera)

def configureFourCam(self):
  self.vars["bandwidthreduced"] = False

def configureSplitCam(self):
  self.vars["staged"] = self.cameras["match"][0]
  self.vars["isstaged"] = [0]
  self.vars["bandwidthreduced"] = False

def configureOneCam(self):
  self.vars["staged"] = self.cameras["match"][0]
  self.vars["isstaged"] = [0]
  self.vars["bandwidthreduced"] = False

def configureFromSetup(self, setup):
  commandfuncs = {"toggleBandwidth": commands.toggleBandwidth, "frontCam": commands.frontCam, "backCam": commands.backCam, "leftCam": commands.leftCam, "rightCam": commands.rightCam}
  self.stacks = {}
  self.stacks["buttons"] = []
  interface = setup["interface"]
  buttons = setup["buttons"]
  configureMatchCameras(self, recams=True)
  copyMatchCameras(self, interface)
  #Caches nedded widgets in their proper stack locations
  for buttonargs in buttons:
    button = self.addButton(command=commandfuncs[buttonargs["command"]], interface=interface)
    self.stacks["buttons"].append(button)
  configfunctions[interface]()

configfunctions = {"mainmenu": configureMainMenu, "settings": configureSettingsMenu, "multiview": configureMultiview, "test": configureTest, "fourcam": configureFourCam, "splitcam": configureSplitCam, "onecam": configureOneCam, "configurable": configureFromSetup}

#Supplementary Configuration Functions
def shareMatchCameras(self):
  matchinters = ["onecammatch", "multiview"]
  try:
    for inter in matchinters:
      self.cameras[inter] = self.cameras["match"]
  except KeyError:
    print("'match' key does not exist. Were any cameras connected on the pi side?")

def addAvalibleCameras(self, interface, maxind = 9):
  cams = commands.getActiveCams(maxind)
  for camnum in cams:
    self.addCam(camnum=camnum, interface=interface)

def addCams(self, neededcams, interface, recams=False):
  #cams = [commands.isCamActive(cam) for cam in neededcams]
  if recams:
    cams = []
  else:
    cams = None
  for camnum in neededcams:
    if recams:
      cams.append(self.addCamera(camnum=camnum, interface=interface, recam=True))
    else:
      self.addCamera(camnum=camnum, interface=interface)
  return cams

def convertIntArgs(args):
  for arg in intargs:
        if arg in args:
          if "?" in arg:
            if args[arg].isdigit():
              args[arg] = int(args[arg])
          else:
            args[arg] = int(args[arg])
  return args

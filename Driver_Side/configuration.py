#configuration.py: Configures the given window with the widgets it depends on
#HP 1/21/2019

import json
import socket
import time

import tkwin as win
import commands
import menus
import visglobals
from visglobals import guimaps, visiontable, camnamenums, setups, competitioninterface

#Global dictionary of menu configuration functions
global configwascalled #Tracks which configuration functions have been called
configwascalled = {"mainmenu": False, "settings": False, "match": False, "onecammatch": False, "multiview": False, "test": False, "splitcam": False}
#Arguments which need to be converted from integers to be passed to getWidgetFromName
intargs = ["camnum", "length", "height", "start?", "end?"]
camerasmade = False
global commandfuncs

#Interface Configuration Functions
def configureMainMenu(self):
  global configwascalled
  self.addButton(text = "Start Match!", command = commands.startMatch, interface = "mainmenu")
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
  self.vars["staged"] = [0, 1, 2, 3]
  self.vars["isactive"] = True
  self.vars["color"] = True
  self.vars["quality"] = 4
  self.vars["framerate"] = 4
  configwascalled["multiview"] = True

def configureFourCam(self):
  configureStacks(self, "fourcam")
  self.vars["bandwidthreduced"] = False
  self.vars["staged"] = [0, 1, 2, 3]

def configureSplitCam(self):
  global configwascalled
  configureStacks(self, "splitcam")
  self.vars["staged"] = [0]
  self.vars["bandwidthreduced"] = False
  configwascalled["splitcam"] = True

def configureOneCam(self):
  configureStacks(self, "onecam")
  self.vars["staged"] = [0]
  self.vars["bandwidthreduced"] = False

def configureStacks(self, interface):
  setup = setups[interface]
  commandfuncs = {"toggleBandwidth": commands.toggleBandwidth, "showFront": commands.frontCam, 
                  "showBack": commands.backCam, "showLeft": commands.leftCam, 
                  "showRight": commands.rightCam, "splitToMains": commands.splitToMains,
                  "splitToSides": commands.splitToSides, "splitToAll": commands.splitToAll,
                  "startMatch": commands.sendStartSignal}
  self.stacks = {}
  self.vars["namedwidgets"] = {}
  self.stacks["buttons"] = []
  buttons = setup["buttons"]
  configureMatchCameras(self, recams=True)
  copyMatchCameras(self, interface)
  #Caches nedded widgets in their proper stack location
  for buttonargs in buttons:
    print(self.stacks)
    if not buttonargs["command"] in commandfuncs:
      continue
    button = self.addButton(text = buttonargs["text"], command=commandfuncs[buttonargs["command"]], interface=interface, rewidget=True)
    self.stacks["buttons"].append(button)
    #Uses the the function's name as a string by which the widget can be referred to
    self.vars["namedwidgets"][buttonargs["command"]] = button


configfunctions = {"mainmenu": configureMainMenu, "settings": configureSettingsMenu, 
                  "multiview": configureMultiview, "test": configureTest, 
                  "fourcam": configureFourCam, "splitcam": configureSplitCam, 
                  "onecam": configureOneCam}

#Supplementary Configuration Functions
def configureMatchCameras(self, neededcams = (0, 1, 2, 3), recams=False):
  """
  Adds the four cameras needed for most match interfaces to window.cameras["match"]
  """
  #For the most part, an alias of addCams(self, neddedcams=(0,1,2,3), interface='match')
  if self.camerasconfiged:
    return
  if recams:
    cams = addCams(self, neededcams=neededcams, interface="match", recams=True) #Though there are many match interfaces, most functions dealing directly with cameras use the global "match" interface
    self.camerasconfiged = True
    return cams
  else:
    addCams(self, neededcams, interface="match")
    self.camerasconfiged = True

def copyMatchCameras(self, interface):
  """
  Copies the cameras in the match interface to the specified interface
  """
  self.cameras[interface] = []
  for camera in self.cameras["match"]:
    self.cameras[interface].append(camera)

#Depreciated
def shareMatchCameras(self):
  """
  Copies match interface cameras to two specific interfaces which won't be used in competition
  """
  matchinters = ["onecammatch", "multiview"]
  try:
    for inter in matchinters:
      self.cameras[inter] = self.cameras["match"]
  except KeyError:
    print("'match' key does not exist. Were any cameras connected on the pi side?")

def addAvalibleCameras(self, interface, maxind = 9):
  """
  Adds all cameras stated to be avalible over NetworkTables to the given interface within range(maxind)
  """
  cams = commands.getActiveCams(maxind)
  for camnum in cams:
    self.addCam(camnum=camnum, interface=interface)

def addCams(self, neededcams, interface, recams=False):
  """
  Adds a specific list of cameras to a specfied window interface
  """
  #cams = [commands.isCamActive(cam) for cam in neededcams]
  if recams:
    cams = []
  else:
    cams = None
  for camnum in neededcams:
    if recams:
      cams.append(self.addCamera(camnum=camnum, interface=interface, rewidget=True))
    else:
      self.addCamera(camnum=camnum, interface=interface)
  return cams

def convertIntArgs(args):
  """
  Converts arguments which are strings due to json constraints to integers
  """
  for arg in intargs:
        if arg in args:
          if "?" in arg:
            if args[arg].isdigit():
              args[arg] = int(args[arg])
          else:
            args[arg] = int(args[arg])
  return args

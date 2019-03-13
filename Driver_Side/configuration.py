#configuration.py: Configures the given window with the widgets it depends on
#HP 1/21/2019

import json
import socket
import time

import tkwin as win
import commands
import menus
import visglobals
from visglobals import guimaps, visiontable, setups, competitioninterface

#Global dictionary of menu configuration functions
global configwascalled #Tracks which configuration functions have been called
configwascalled = {"mainmenu": False, "settings": False, "match": False, "onecammatch": False, "multiview": False, "test": False, "splitcam": False, "plaincomp": False}
#Arguments which need to be converted from integers to be passed to getWidgetFromName
intargs = ["camnum", "length", "height", "start?", "end?"]
camerasmade = False
global commandfuncs

#Interface Configuration Functions
#Adds needed widgets into the given window
#Not all of these work due to constant updates
def configureMainMenu(self):
  global configwascalled
  self.addButton(text = "Start Match!", command = self.startMatchInterface, interface = "mainmenu")
  configwascalled["mainmenu"] = True

def configureTest(self):
  global configwascalled
  neededcams = [0, 1, 2, 3]
  addCams(self, neededcams=neededcams, interface="test")
  configwascalled["test"] = True

def configureOneCamMatch(self):
  #Configuration only to be called by configureMatchInterfaces
  global configwascalled
  setupMatchCameras(self, interface="onecammatch")
  self.addButton("Switch Cam", commands.swapOutCam, partialarg = win.SELF, interface = "onecammatch")
  self.addEntry(interface = "onecammatch")
  configwascalled["onecammatch"] = True

def configureMultiview(self):
  global configwascalled
  # Adds cameras to a 'match' interface then copies them to the proper interface
  # so their duplicate Camera widgets don't try to reinitialize identical sockets
  setupMatchCameras(self, interface="multiview")
  self.addButton("Select Front", self.stageFrontCam, interface = "multiview")
  self.addButton("Select Back", self.stageBackCam, interface = "multiview")
  self.addButton("Select Left", self.stageLeftCam, interface = "multiview")
  self.addButton("Select Right", self.stageRightCam, interface = "multiview")
  self.addButton("Select All", self.stageAllCams, interface = "multiview")
  self.addButton("Select Mains", self.stageMainCams, interface = "multiview")
  self.addButton("Select Sides", self.stageSubCams, interface = "multiview")
  self.addButton("Deactivate Cameras", self.toggleActivity, interface = "multiview")
  self.addButton("Framerate Up", self.increaseFramerate, interface = "multiview")
  self.addButton("Framerate Down", self.decreaseFramerate, interface = "multiview")
  self.addButton("Increase Quality", self.increaseQuality, interface = "multiview")
  self.addButton("Decrease Quality", self.decreaseQuality, interface = "multiview")
  self.addButton("Black & White", self.toggleColor, interface = "multiview")
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
  global configwascalled
  #Creates and sets up widgets that can connect to the four expected cameras
  setupMatchCameras(self, "fourcam")
  #Sets up the buttons specified in the *guiname*.setup file
  configureStacks(self, "fourcam")
  #Initiates some setting variables to prevent KeyErrors
  self.vars["bandwidthreduced"] = False
  self.vars["staged"] = [0, 1, 2, 3]
  configwascalled["multiview"] = True

def configureSplitCam(self):
  global configwascalled
  #Creates and sets up widgets that can connect to the four expected cameras
  setupMatchCameras(self, "splitcam")
  #Sets up the buttons specified in the *guiname*.setup file
  configureStacks(self, "splitcam")
  #Initiates some setting variables to prevent KeyErrors
  self.vars["staged"] = [0]
  self.vars["bandwidthreduced"] = False
  configwascalled["splitcam"] = True

def configureOneCam(self):
  global configwascalled
  #Creates and sets up widgets that can connect to the four expected cameras
  setupMatchCameras(self, "onecam")
  #Sets up the buttons specified in the *guiname*.setup file
  configureStacks(self, "onecam")
  #Initiates some setting variables to prevent KeyErrors
  self.vars["staged"] = []
  self.vars["bandwidthreduced"] = False
  commands.frontCam(self)
  configwascalled["onecam"] = True

def configurePlainComp(self):
  global configwascalled
  #Gets the camera active at launch
  firstcamnum = int(visiontable.getNumber("isactive", 0))
  #Places the camera in the 'active' part of the system
  self.vars["staged"] = [firstcamnum]
  #Adds the camera widget to the window
  self.addCamera(firstcamnum)
  self.copyMatchCameras("plaincomp")
  self.vars["bandwidthreduced"] = False
  configwascalled["plaincomp"] = True

#Not a specific configuration function
#Part of the configuring process which allows buttons to be easily added in a stack
def configureStacks(self, interface):
  setup = setups[interface]
  commandfuncs = {"toggleBandwidth": commands.toggleBandwidth, "showFront": commands.frontCam, 
                  "showBack": commands.backCam, "showLeft": commands.leftCam, 
                  "showRight": commands.rightCam, "splitToMains": self.splitToMains,
                  "splitToSides": self.splitToSides, "splitToAll": self.splitToAll,
                  "startMatch": self.startMatchInterface, "configSystem": self.configSystem,
                  "sendStartSiginal": self.sendSignal, "saveImage": self.saveImage}
  self.stacks = {}
  self.vars["namedwidgets"] = {}
  self.stacks["buttons"] = []
  buttons = setup["buttons"]
  #Caches nedded widgets in their proper stack location
  for buttonargs in buttons:
    if not buttonargs["command"] in commandfuncs:
      continue
    button = self.addButton(text = buttonargs["text"], command=commandfuncs[buttonargs["command"]], interface=interface, rewidget=True)
    self.stacks["buttons"].append(button)
    #Uses the the function's name as a string by which the widget can be referred to
    self.vars["namedwidgets"][buttonargs["command"]] = button

#Also part of general configuration process
def setupMatchCameras(self, interface):
  configureMatchCameras(self, recams=True)
  self.copyMatchCameras(interface)

configfunctions = {"mainmenu": configureMainMenu, "multiview": configureMultiview,
                  "test": configureTest,          "fourcam": configureFourCam, 
                  "splitcam": configureSplitCam,  "onecam": configureOneCam, 
                  "plaincomp": configurePlainComp}

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

#Unused by main interfaces
#Copy of copyMatchCameras
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

#configuration.py: Configures the given window with the widgets it depends on
#HP 1/21/2019

import json
import socket
import time

import tkwin as win
import commands
import configuration as config
import menus
import visglobals
from visglobals import guimaps, visiontable

#Global dictionary of menu configuration functions
global configwascalled #Tracks which configuration functions have been called
configwascalled = {"mainmenu": False, "settings": False, "match": False, "onecammatch": False, "multiview": False}

#Interface Configuration Functions
def configureMainMenu(self):
    global configwascalled
    self.addButton(text = "Start Match!", command = startMultiviewMatch, partialarg = win.SELF, interface = "mainmenu")
    self.addButton(text = "Exit", command = self.root.quit, interface = "mainmenu")
    configwascalled["mainmenu"] = True

def configureSettingsMenu(self):
    global configwascalled
    configwascalled["settings"] = True

def configureMatchInterfaces(self):
    """
    Configures all match interfaces
    """
    global configwascalled
    cams = commands.getActiveCams(9)
    for camnum in cams:
        self.addCamera(widget = cams[camnum], interface="match") #Though there are many match interfaces, most functions dealing directly with cameras use the global "match" interface
    shareMatchCameras(self) #Copies the camera objects to other interfaces so they can be gridded
    configureOneCamMatch(self)
    configureMultiViewMatch(self)
    configwascalled["match"] = True

def configureOneCamMatch(self):
    #Configuration only to be called by configureMatchInterfaces
    global configwascalled
    self.addButton("Switch Cam", commands.swapOutCam, partialarg = win.SELF, interface = "onecammatch")
    self.addEntry(interface = "onecammatch")
    configwascalled["onecammatch"] = True

def configureMultiViewMatch(self):
    global configwascalled
    self.addButton("Select Front", commands.stageFrontCam, interface = "multiview")
    self.addButton("Select Back", commands.stageBackCam, interface = "multiview")
    self.addButton("Select Left", commands.stageLeftCam, interface = "multiview")
    self.addButton("Select Right", commands.stageRightCam, interface = "multiview")
    self.addButton("Select All", commands.stageAllCams, interface = "multiview")
    self.addButton("Select Mains", commands.stageMainCams, interface = "multiview")
    self.addButton("Select Sides", commands.stageSubCams, interface = "multiview")
    self.addButton("Deactivate", commands.toggleActivity, interface = "multiview")
    self.addButton("Framerate Up", commands.increaseFramerate, interface = "multiview")
    self.addButton("Framerate Down", commands.decreaseFramerate, interface = "multiview")
    self.addButton("Increase Quality", commands.increaseQuality, interface = "multiview")
    self.addButton("Decrease Quality", commands.decreaseQuality, interface = "multiview")
    self.addButton("Black & White", commands.toggleColor, interface = "multiview")
    self.addText("All Cameras Staged", interface = "multiview")
    self.addText("All Cameras Active", interface = "multiview")
    self.addText("Quality Level: Default", interface = "multiview")
    self.addText("Color Mode: RGB", interface = "multiview")
    self.addText("15 FPS", interface = "multiview")
    self.addText("Adjust Framerate", interface = "multiview")
    self.addText("Adjust Quality", interface = "multiview")
    self.addText("EPIC ROBOTZ Vision System: Crowded Interface Edition!", interface = "multiview")
    configwascalled["multiview"] = True

configfunctions = {"mainmenu": configureMainMenu, "settings": configureSettingsMenu, "match": configureMatchInterfaces}

#Supplementary Configuration Functions
def shareMatchCameras(self):
    matchinters = ["onecammatch", "multiview"]
    for inter in matchinters:
        if not inter in self.cameras:
            self.cameras[inter] = []
    for camera in self.cameras["match"]:
        for inter in matchinters:
            self.cameras[inter].append(camera)

def startMultiviewMatch(self):
    menus.matchMenu(self)



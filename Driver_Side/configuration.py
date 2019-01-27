#configuration.py: Configures the given window with the widgets interfaces depend on
#HP 1/21/2019

import json
import socket
import time
import tkwin as win

import commands
import visglobals
from visglobals import visiontable, guimaps

#Global dictionary of menu configuration functions
global configwascalled #Tracks which configuration functions have been called
configwascalled = {"mainmenu": False, "settings": False, "match": False, "onecammatch": False, "multiview": False}

#Interface Configuration Functions
def configureMainMenu(self):
    global configwascalled
    self.addButton(text = "Start Match!", command = commands.startMatch, partialarg = win.SELF, interface = "mainmenu")
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
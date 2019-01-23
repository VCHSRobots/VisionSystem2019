#configuration.py: Configures the given window with the widgets interfaces depend on
#HP 1/21/2019

import json
import socket
import time
import tkwin as win

import commands
import globals
from globals import visiontable, guimaps

#Global dictionary of menu configuration functions
global configwascalled #Tracks which configuration functions have been called
configwascalled = {"mainmenu": False, "settings": False, "match": False, "onecammatch": False, "multiview": False}

#Interface Configuration Functions
def configureMainMenu(self):
    global configwascalled
    self.addButton("Start Match!", commands.startMatch, interface="mainmenu")
    self.addButton("Exit", self.root.quit, partialarg=win.NOARG, interface="mainmenu")
    configwascalled["mainmenu"] = True

def configureSettingsMenu(self):
    global configwascalled
    self.add
    configwascalled["settings"] = True

def configureMatchInterfaces(self):
    """
    Configures all match interfaces
    """
    global configwascalled
    cams = commands.getActiveCams(9)
    for camnum in cams:
        self.addCam(cams[camnum], interface="match") #Though there are many match interfaces, most functions dealing directly with cameras use the global "match" interface
    shareMatchCameras(self) #Copies the camera objects to other interfaces so they can be gridded
    configureOneCamMatch(self)
    configureMultiViewMatch(self)
    configwascalled["match"] = True

def configureOneCamMatch(self):
    global configwascalled
    cams = commands.getActiveCams(9)
    for camnum in cams:
        self.addCam(cams[camnum], interface="onecammatch")
    self.addButton("Switch Cam", commands.swapOutCam, interface="onecammatch")
    self.addEntry(interface="onecammatch")
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
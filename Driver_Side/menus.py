#interfaces.py: Manages which user interface is active
#HP 1/21/2019

import json
import socket
import time
import tkwin as win

import visglobals
import commands
import configuration as config
from visglobals import visiontable, guimaps

#Global settings dict
global settings
settings = {"matchtype": "multiview"}
global currentinterface
currentinterface = "mainmenu"
matchtime = 180

#Functions to be called when a menu is invoked
def mainMenu(self):
    """
    Main Menu Interface
    """
    global currentinterface
    while currentinterface == "mainmenu":
        pass

def settingsMenu(self):
    """
    Main Menu Interface
    """
    global currentinterface
    while currentinterface == "settings":
        pass

def matchMenu(self):
    """
    Main Menu Interface
    """
    global currentinterface
    if not config.configwascalled["match"]:
        config.configureMatchInterfaces(self)
    if settings["matchtype"] == "multiview":
        switchUi(self, "multiview")
    elif settings["matchtype"] == "onecammatch":
        switchUi(self, "onecammatch")
    commands.startMatch(self)
    if settings["matchtype"] == "multiview":
        multiviewMenu(self)

def multiviewMenu(self):
    """
    Multiview Menu Interface
    """
    global currentinterface
    starttime = time.perf_counter()
    commands.setupMultiview(self)
    timeleft = 180
    while timeleft < 0:
        timepassed = time.perf_counter()-starttime
        timeleft = matchtime-timepassed
        commands.setRemainingTime(self, timeleft)
        commands.matchLoop(self)


#Ui Management Functions
def switchUi(self, guiname):
    """
    Configures the window for the given the guifile to be setup and any stray widgets to clear
    """
    global currentinterface
    self.tearDown()
    #Configures window for the new gui
    if not config.configwascalled[guiname]:
        config.configfunctions[guiname](self)
    #Grids gui widgets
    self.processGuiMap(guimaps[guiname], guiname)
    currentinterface = guiname
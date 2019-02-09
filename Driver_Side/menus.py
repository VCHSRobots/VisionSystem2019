#interfaces.py: Manages which user interface is active
#HP 1/21/2019

import json
import socket
import time
import tkwin as win

import visglobals
import commands
import configuration as config
from visglobals import visiontable, guimaps, null

#Global settings dict
global settings
settings = {"matchtype": "multiview"}
currentinterface = "mainmenu"
matchtime = 180

#Functions to be called when a menu is invoked
def mainMenu(self):
    """
    Main Menu Interface
    """
    while self.interface == "mainmenu":
        pass

def settingsMenu(self):
    """
    Main Menu Interface
    """
    while self.interface == "settings":
        pass

def matchMenu(self):
    """
    Main Menu Interface
    """
    if not config.configwascalled["match"]:
        config.configureMatchInterfaces(self)
    if settings["matchtype"] == "multiview":
        switchUi(self, "multiview")
    elif settings["matchtype"] == "onecammatch":
        switchUi(self, "onecammatch")
    commands.startMatch(self)
    if settings["matchtype"] == "multiview":
        self.interface = "multiview"
        multiviewMenu(self)

def multiviewMenu(self):
    """
    Multiview Menu Interface
    """
    starttime = time.perf_counter()
    commands.setupMultiview(self)
    timeleft = 180
    lastmatchcams = self.cameras["match"]
    while self.interface == "multiview":
        if timeleft < 0:
            timepassed = time.perf_counter()-starttime
            timeleft = matchtime-timepassed
            commands.setRemainingTime(self, timeleft)
            commands.matchLoop(self, lastmatchcams)
            lastmatchcams = self.cameras["match"]
        else:
            #TODO: Make this do something appropriate when the match ends
            timeleft = 180

def testMenu(self):
    """
    Multi camera test interface
    """
    print(self.cameras)
    lastmatchcams = self.cameras["test"]
    while self.interface == "test":
        commands.matchLoop(self, lastmatchcams, interface="test")
        lastmatchcams = self.cameras["test"]
        print("here")

matchfunctions = {"mainmenu": mainMenu, "settings": mainMenu, "onecammatch": null, "multiview": multiviewMenu, "test": testMenu}

#Ui Management Functions
def switchUi(self, guiname):
    """
    Configures the window for the given the guifile to be setup and any stray widgets to clear
    """
    print(0)
    self.tearDown()
    time.sleep(5)
    print(1)
    #Configures window for the new gui
    if not config.configwascalled[guiname]:
        config.configfunctions[guiname](self)
        print(2)
    #Grids gui widgets
    self.processGuiMap(guimaps[guiname], guiname)
    print(3)
    self.interface = guiname
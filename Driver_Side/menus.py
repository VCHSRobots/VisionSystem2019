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
    self.switchUi("match")
    commands.startMatch(self)
    while currentinterface == "match":
        pass

def multiviewMenu(self):
    """
    Multiview Menu Interface
    """
    global currentinterface
    while currentinterface == "multiview":
        pass

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

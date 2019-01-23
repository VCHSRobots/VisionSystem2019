#interfaces.py: Manages which user interface is active
#HP 1/21/2019

import json
import socket
import time
import tkwin as win

import globals
import configuration as config
from globals import visiontable, guimaps

#Global settings dict
global settings
settings = {"matchtype": "multiview"}
global currentinterface
currentinterface = "mainmetu"

#Functions to be called when a menu is invoked
def mainMenu(self):
    """
    Main Menu Interface
    """
    global currentinterface
    while currentinterface == "mainmenu":
        self.entries["mainmenu"][0] = 

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
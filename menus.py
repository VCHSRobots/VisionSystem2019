#menus.py: User interface menu management
#HP 1/21/2019

import json
import socket
import time
import tkwin as win
from networktables import NetworkTables as nt

def openGuiFile(name):
    guifile = open("{0}.gui".format(name))
    gui = json.load(guifile)
    guifile.close()
    return gui

#Globals
#Ip is configured to Holiday's laptop and pi... change if neccecary!
ip = "10.44.15.41"
piip = "10.44.15.59"
piadr = (piip, 5809)
myadr = (ip, 5809)
#Global Menus
mainmenu = openGuiFile("mainmenu")
settingsgui = None #openGuiFile("settings")
onecammatch = openGuiFile("onecammatch")
guimaps = {"mainmenu": mainmenu, "settings": settingsgui, "onecammatch": onecammatch}
global currentgui
#Global to append to whenever adding widgets not tracked by the gui file
global straywidgets
straywidgets = {}
currentgui = mainmenu
#Global socket
global comsock
#NetworkTables
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")
#Global settings dict
global settings


#Interface Configuration Functions
def configureMainMenu(self):
    self.addButton("Start Match!", startMatch)
    self.addButton("Exit", self.root.quit, partialarg=win.NOARG)

def configureSettingsMenu(self):
    pass

def configureOneCamMatch(self):
    camnums = getActiveCams(9)
    self.addCam(camnums[0])
    self.addButton("End Match", sendStopSignal, partialarg=comsock)
    self.addEntry()
    
#Global dictionary of menu configuration functions
configfunctions = {"mainmenu": configureMainMenu, "settings": configureSettingsMenu, "onecammatch": configureOneCamMatch}

#Commands
def startMatch(self):
    """
    Starts Vision System for a competition match
    """
    #This commmand is called from multiple sources, not just by menus
    #Creates a socket for two-way communication with the pi
    global comsock
    comsock = makeSocket(myadr)
    sendStartSignal(comsock)
    matchLoop(self)
    comsock.close()

def testMatch():
    """
    Test Vision System without some competiton features active
    """
    pass

def sendStopSignal(sock):
    sock.sendto(b"end", piadr)

#Supplemetary functions to Commands
def getActiveCams(numrange):
    """
    Polls NetworkTables to check which cameras are active
    """
    actives = []
    for num in range(numrange):
        isactive = visiontable.getBoolean("{0}isactive".format(num), False)
        print(isactive)
        if isactive:
            actives.append(num)
    return actives

def makeSocket(adr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(adr)
    return sock

def sendStartSignal(sock):
    sock.sendto(b"i", piadr)

def matchLoop(self, timeout=180):
    starttime = time.perf_counter()
    while time.perf_counter()-starttime < 180:
        if self.active:
            activecams = getActiveCams(len(self.cameras))
            for activeind in activecams:
                self.cameras[activeind].updateImgOnLabel()

def null():
    pass

#Functions to be called when a menu changes
def mainMenu(self):
    """
    Main Menu Interface
    """
    pass

def settingsMenu(self):
    pass

def matchMenu(self):
    """
    Function to be called upon the start of a match
    """
    global straywidgets
    switchUi(self, "onecammatch", straywidgets)

#Ui Management Functions
def switchUi(self, guiname, straywidgets=straywidgets):
    """
    Configures the window for the given the guifile to be setup and any stray widgets to clear
    """
    global currentgui
    self.tearDown(currentgui)
    #Clears any widgets which weren't managed directly by the guifile
    #Stored as [(Widget) or (Widget, Option)]
    for stray in straywidgets:
        #If the widget had an option attached to it
        if len(stray) > 1:
            stray[0].ungrid(stray[1])
        else:
            stray[0].ungrid()
    #Configures window for the new gui
    configfunctions[guiname](self)
    #Grids gui widgets
    self.processGuiMap(guimaps[guiname])
    currentgui = guimaps[guiname]

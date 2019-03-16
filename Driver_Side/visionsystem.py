#visionsystem.py: High level vision system interface
#HP 1/8/2019

import tkwin
import json
import socket
import time
import tkinter as tk
from cProfile import run
from networktables import NetworkTables as nt

import autoload
import menus
import tkwin
import configuration
import threads
import commands
import visglobals
from commands import sendIP
from visglobals import myip, piip, null, myadr, comsock, visiontable, rioip, competitioninterface

#Non-blocking attempt to connect to NetworkTables. This often doesn't work on the first try
nt.startClient(rioip)

def startSystem():
    """
    Initiates the vision system application for the 2019 First Robotics Competition
    """
    print("Starting Vision System...")
    #Sends computer ip to the pi to keep from having to assign a static ip
    ip = sendIP()
    #menustructure = {"Mode": {"Send Start Signal": tkwin.sendStartSignal, "Configure System": tkwin.configSystem}}
    #Creates the window to be displayed
    win = tkwin.SwitchingWindow("Vision System", ip=ip)
    #Sets camera values based on default json values
    autoload.loadValues()
    #Sets the function to be called when window is initated
    systemthread = makeSystemThread(win)
    win.setThread(systemthread)
    #Sets up the main menu
    win.startMatchInterface()
    win.runWin()
    #Tries to connect to NetworkTables if it failed before
    forceConnectNetworkTables()

def forceConnectNetworkTables():
    """
    Attemps to connect to NetworkTables
    Blocks until successful
    """
    while not nt.isConnected():
        nt.startClient(rioip)
    print("Connected to networktables")

def makeSystemThread(win):
    """
    Thread fucntion to be called by the tkinter class
    """
    thread = threads.SystemThread(win)
    return thread

#Unused camera-related functions
def getActiveCams(numrange):
    """
    Polls NetworkTables to check which cameras are active
    """
    actives = []
    for num in range(numrange):
        isactive = visiontable.getBoolean("{0}isactive".format(num), False)
        if isactive:
            actives.append(num)
    return actives

#Test code which no longer works
def testLoop(self):
    """
    Thread fucntion to be called by the tkinter class
    """
    while True:
        while self.active:
            activecams = getActiveCams(len(self.cameras))
            for activeind in activecams:
                self.cameras[activeind].updateImgOnLabel()

def testSystem():
    """
    A simple test of the vision system involving only one camera
    """
    win = tkwin.TkWin("Test")
    camnums = getActiveCams(10)
    for camnum in camnums:
        win.addCamera(camnum)
    win.setThread(testLoop)
    guifile = open("test.gui")
    print(win.cameras)
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap("mainmenu")
    try:
        win.runWin()
    finally:
        win.emergencyShutdown()


def otherTestingLoop(self):
    while True:
        while self.active:
            self.localcameras[0].updateCam()
            print(True)

def testGrid():
    """
    A test of the gridding function in the TkWin class
    """
    win = tkwin.TkWin("Test")
    win.addLocalCam(0)
    guifile = open("test.gui")
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap("mainmenu")
    win.setThread(otherTestingLoop)
    print(win.thread)
    win.runWin()

if __name__ == "__main__":
    startSystem()
#visionsystem.py: High level vision system interface
#HP 1/8/2019

import tkwin
import json
import socket
import time
import tkinter as tk
from networktables import NetworkTables as nt

import menus
import configuration
import visglobals
from visglobals import ip, piip, null, myadr, comsock, visiontable

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
    win.setThreadLoop(testLoop)
    guifile = open("test.gui")
    print(win.cameras)
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap(guimap, "mainmenu")
    try:
        win.runWin()
    finally:
        win.emergencyShutdown()

def systemThread(self):
    """
    Thread fucntion to be called by the tkinter class
    """
    pass

def startSystem():
    """
    Initiates the vision system application for the 2019 First Robotics Competition
    """
    menustructure = {"Test": {"Do Nothing": null, "Switch Menus_*self*": menus.matchMenu}}
    win = tkwin.TkWin("Vision System", menustructure=menustructure)
    #Sets the function to be called when window is initated
    win.setThreadLoop(systemThread)
    #Sets up the main menu
    configuration.configureMainMenu(win)
    win.processGuiMap(visglobals.guimaps["mainmenu"], "mainmenu")
    win.runWin()


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

def sendStartSignal():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b"i", (piip, 5800))
    sock.close()

def alphaLoop(self):
    while True:
        while self.active:
            self.localcameras[0].updateCam()
            print(True)

def testGrid():
    win = tkwin.TkWin("Test")
    win.addLocalCam(0)
    guifile = open("test.gui")
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap(guimap, "mainmenu")
    win.setThreadLoop(alphaLoop)
    print(win.threadloop)
    win.runWin()
#visionsystem.py: High level vision system interface
#HP 1/8/2019

import tkwin
import json
import socket
import time
import tkinter as tk
from networktables import NetworkTables as nt

#Ip is configured to Holiday's laptop and pi... change if neccecary!
ip = "10.44.15.41"
piip = "10.44.15.59"
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")

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
        win.addCam(camnum)
    win.setThreadLoop(testLoop)
    guifile = open("test.gui")
    print(win.cameras)
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap(guimap)
    try:
        win.runWin()
    finally:
        win.emergencyShutdown()

def systemThread(self):
    """
    Thread fucntion to be called by the tkinter class
    """
    #TODO: Make bound socket listener in case a socket gets overloaded
    matchstarted = False
    while not matchstarted:
        pass
    matchLoop(self)
    

def matchLoop(self):
    """
    Initiates the main vision system
    """
    sendStartSignal()
    while True:
        while self.active:
            activecams = getActiveCams(len(self.cameras))
            for activeind in activecams:
                self.cameras[activeind].updateImgOnLabel()

def startSystem():
    """
    Initiates the vision system application for the 2019 First Robotics Competition
    """
    win = tkwin.TkWin("Vision System")
    camnums = getActiveCams(9)
    for camnum in camnums:
        win.addCam(camnum)
    win.setThreadLoop(systemThread)
    #TODO: Choose Gui files based on selecttion options such as avalible cameras
    guifile = open("test.gui")
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap(guimap)
    win.runWin()

def configButton(root, text, command):
    """
    Adds a button to the given root
    """

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
    win.processGuiMap(guimap)
    win.setThreadLoop(alphaLoop)
    print(win.threadloop)
    win.runWin()
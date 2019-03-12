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
import configuration
import threads
import commands
import visglobals
from visglobals import myip, piip, null, myadr, comsock, visiontable, rioip, competitioninterface

nt.startClient(rioip)

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

def startSystem():
    """
    Initiates the vision system application for the 2019 First Robotics Competition
    """
    print("Starting Vision System...")
    ip = sendIP()
    menustructure = {"Mode": {"Send Start Signal_*self*": commands.sendSignal, "Configure System_*self*": commands.configSystem}}
    win = tkwin.TkWin("Vision System", menustructure=menustructure, ip=ip)
    #Sets camera values based on default json values
    autoload.loadValues()
    #Sets the function to be called when window is initated
    systemthread = makeSystemThread(win)
    win.setThread(systemthread)
    #Sets up the main menu
    win.switchUi(competitioninterface)
    commands.sendStartSignal(comsock)
    win.runWin()
    #forceConnectNetworkTables()

def sendIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("10.44.15.1", 80))
    ip = sock.getsockname()[0]
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.sendto(ip.encode(), (piip, 5800))
    return ip

def forceConnectNetworkTables():
    while not nt.isConnected():
        nt.startClient(rioip)
    print("Connected to networktables")

def makeSystemThread(win):
    """
    Thread fucntion to be called by the tkinter class
    """
    thread = threads.SystemThread(win)
    return thread

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

def forceNtConnection():
    while not nt.isConnected():
        nt.startClient(rioip)
        print("Connected to networktables")

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
    win.processGuiMap("mainmenu")
    win.setThread(alphaLoop)
    print(win.thread)
    win.runWin()

if __name__ == "__main__":
    run("startSystem()")
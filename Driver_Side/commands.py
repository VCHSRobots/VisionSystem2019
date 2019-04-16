#commands.py: Button commands called by interfaces
#1/21/2019 HP

import time
import json
import socket

import visglobals
import configuration as config
from visglobals import comsock, piip, piadr, visiontable, competitioninterface

#TODO: Reorganize these and make some of them class functions

camnames = {0: "Front", 1: "Rear", 2: "Left", 3: "Right"}

#Globally used commands
def sendIP():
    #Creates a throwaway socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #Dummy connection to radio to make the computer reveal its own ip adress
    sock.connect(("10.44.15.1", 80))
    ip = sock.getsockname()[0]
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #Sends ip to pi
    sender.sendto(ip.encode(), (piip, 5800))
    return ip

#Unused
def swapOutCam(self, replacedcam, newcam):
    """
    Swaps out a gridded camera for another camera in the same location
    """
    row, column, columnspan, rowspan = replacedcam.ungrid()
    newcam.grid(row, column, columnspan, rowspan)

#Unused
def matchLoop(self, lastmatchcams, interface = "match"):
    """
    Updates all cameras and checks if any failed cameras reconnected
    """
    updateCams(self, interface=interface)
    if lastmatchcams != self.cameras[interface]:
        config.shareMatchCameras(self)

#Testing
def updateCams(self, interface="match"):
    """
    Updates all cameras on an interface
    """
    activecams = getActiveCams(len(self.cameras[interface]))
    for activeind in activecams:
        camera = self.cameras[interface][activeind]
        if camera in self.gridded:
            camera.updateImgOnLabel()

#Unused
def turnOffUngridedCams(self):
    """
    Turns off any cameras which aren't on the grid but are sending images to the computer
    """
    for interface in self.cameras:
        for camera  in interface:
            if not camera.location:
                camera.active = False
                camera.updateCamOverNetwork()

#Multiview Commands were migrated to tkwin

#Splitcam functions were migrated to tkwin
        
#Universal Competition Functions
def toggleBandwidth(self):
    if self.vars["bandwidthreduced"]:
        normalBandwidthMode(self)
        self.vars["namedwidgets"]["toggleBandwidth"].setText("Reduce Bandwidth")
    else:
        lowBandwidthMode(self)
        self.vars["namedwidgets"]["toggleBandwidth"].setText("Return To Normalcy!")

def normalBandwidthMode(self):
    cameras = self.cameras["match"]
    for camera in cameras:
        increaseBandwidth(camera)
    self.vars["bandwidthreduced"] = False

def lowBandwidthMode(self):
    cameras = self.cameras["match"]
    for camera in cameras:
        reduceBandwidth(camera)
    self.vars["bandwidthreduced"] = True

def reduceBandwidth(camera):
    camera.quality = 7
    camera.framerate = 24
    camera.updateOverNetwork()

def increaseBandwidth(camera, main=True):
    camera.quality = 28
    camera.framerate = 24
    camera.updateOverNetwork()

def updateStagedCams(self):
    staged = getStagedCams(self)
    for cam in staged:
        cam.updateImgOnLabel()

def sendStartSignal(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b"start", piadr)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def getStagedCams(self):
    staged = []
    for num in self.vars["staged"]:
        staged.append(self.cameras["match"][num])
    return staged

#Supplemetary functions to Commands
def getActiveCams(numrange = 0, *args):
    """
    Polls NetworkTables to check which cameras are active. Accepts a range or specific values
    """
    actives = []
    if args:
        isactive = visiontable.getBoolean("{0}isactive".format(numrange), False)
        if isactive:
            actives.append(numrange)
        for num in args:
            isactive = visiontable.getBoolean("{0}isactive".format(num), False)
            if isactive:
                actives.append(num)
    else:
        for num in range(numrange):
            isactive = visiontable.getBoolean("{0}isactive".format(num), False)
            if isactive:
                actives.append(num)
    return actives

def isCamActive(camnum):
    return visiontable.getBoolean("{0}isactive".format(camnum), False)

def getColorCams(numrange = 0, *args):
    """
    Polls NetworkTables to check which cameras are active. Accepts a range or specific values
    """
    color = []
    if args:
        iscolor = visiontable.getBoolean("{0}color".format(numrange), False)
        if iscolor:
            color.append(numrange)
        for num in args:
            iscolor = visiontable.getBoolean("{0}color".format(num), False)
            if iscolor:
                color.append(num)
    else:
        for num in range(numrange):
            iscolor = visiontable.getBoolean("{0}color".format(num), False)
            if iscolor:
                color.append(num)
    return color

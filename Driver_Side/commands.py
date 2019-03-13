#commands.py: Button commands called by interfaces
#1/21/2019 HP

import time
import json
import socket

import visglobals
import configuration as config
from visglobals import comsock, piadr, visiontable, competitioninterface

#TODO: Reorganize these and make some of them class functions

camnames = {0: "Front", 1: "Rear", 2: "Left", 3: "Right"}

#Globally used commands
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

#The following four functions are unused, as they are better replaced by the switchCamNum methods on cameras themselves
def switchCam(self, camnum):
    """
    Duplicate of TkWin.replaceWidget()
    """
    ungridStaged(self)
    camera = self.cameras["match"][camnum]
    self.gridWidget(camera, defaultlocation[0], defaultlocation[1], defaultlocation[2], defaultlocation[3])
    self.vars["staged"] = [camnum]

def getStagedCam(self):
    """
    Gets staged camera from networktables and responds accordingly
    """
    staged = visiontable.getNumber("activecam", 0)
    if self.vars["staged"][0] != staged:
        visiontable.putBoolean("{}isactive".format(staged), True)
        switchCam(self, staged)

def frontCam(self):
    visiontable.putNumber("activecam", 0)
    visiontable.putBoolean("0isactive", True)
    switchCam(self, 0)

def backCam(self):
    visiontable.putNumber("activecam", 1)
    visiontable.putBoolean("1isactive", True)
    switchCam(self, 1)

def leftCam(self):
    visiontable.putNumber("activecam", 2)
    visiontable.putBoolean("2isactive", True)
    switchCam(self, 2)

def rightCam(self):
    visiontable.putNumber("activecam", 3)
    visiontable.putBoolean("3isactive", True)
    switchCam(self, 3)

def saveImage(self):
    for camnum in self.vars["staged"]:
        self.cameras["match"][camnum].save = True
        
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

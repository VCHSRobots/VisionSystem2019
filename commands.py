#commands.py: Button commands called by interfaces
#1/21/2019 HP

import time

import globals
from globals import comsock, visiontable

def startMatch(self):
    """
    Starts Vision System for a competition match
    """
    #This commmand is called from multiple sources, not just by menus
    #Creates a socket for two-way communication with the pi
    sendStartSignal(comsock)
    matchLoop(self)
    comsock.close()

def swapOutCam(self):
    """
    Swaps out a gridded camera for another camera in the same location
    """
    cams = self.cams["match"]
    cam = None
    for camera in cams:
        if camera in self.gridded:
            cam = camera
    location = cam.location
    nextcamind = self.cams["match"].index(cam)+1
    numofcams = len(self.cams["match"])
    nextcam = self.cams["match"][nextcamind%numofcams]
    self.gridded.pop(cam)
    cam.ungrid()
    self.gridWidget(widget=nextcam, column=location[0], row=location[1], columnspan=location[2], rowspan=location[3])

def sendStartSignal(sock):
    sock.sendto(b"i", globals.piadr)

def matchLoop(self, timeout=180):
    starttime = time.perf_counter()
    while time.perf_counter()-starttime < 180:
        if self.active:
            activecams = getActiveCams(len(self.cameras["match"]))
            for activeind in activecams:
                self.cameras["match"][activeind].updateImgOnLabel()

def updateCams(self):
    activecams = getActiveCams(len(self.cameras["match"]))
    for activeind in activecams:
        camera = self.cameras["match"][activeind]
        if camera in self.gridded:
            camera.updateImgOnLabel()

def turnOffUngridedCams(self):
    """
    Turns off any cameras which aren't on the grid but are sending images to the computer
    """
    pass

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

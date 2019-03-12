#commands.py: Button commands called by interfaces
#1/21/2019 HP

import time
import json
import socket

import visglobals
import configuration as config
from visglobals import comsock, piadr, visiontable, competitioninterface

camnames = {0: "Front", 1: "Rear", 2: "Left", 3: "Right"}

#Globally used commands

def configSystem(self):
    visiontable.putBoolean("config", True)

def sendSignal(self):
    sendStartSignal(comsock)

def startMatchInterface(self):
    """
    Sends the Vision System start signal for a competition match
    """
    self.switchUi(competitioninterface)
    sendStartSignal(comsock)

def swapOutCam(self, replacedcam, newcam):
    """
    Swaps out a gridded camera for another camera in the same location
    """
    row, column, columnspan, rowspan = replacedcam.ungrid()
    newcam.grid(row, column, columnspan, rowspan)

def matchLoop(self, lastmatchcams, interface = "match"):
    """
    Updates all cameras and checks if any failed cameras reconnected
    """
    updateCams(self, interface=interface)
    if lastmatchcams != self.cameras[interface]:
        config.shareMatchCameras(self)

def updateCams(self, interface="match"):
    """
    Updates all cameras on an interface
    """
    activecams = getActiveCams(len(self.cameras[interface]))
    for activeind in activecams:
        camera = self.cameras[interface][activeind]
        if camera in self.gridded:
            camera.updateImgOnLabel()

def turnOffUngridedCams(self):
    """
    Turns off any cameras which aren't on the grid but are sending images to the computer
    """
    for interface in self.cameras:
        for camera  in interface:
            if not camera.location:
                camera.active = False
                camera.updateCamOverNetwork()
#Setup Commands
entries = ["interface", "mainframes", "sideframes", "mainwidth", "mainheight", "sidewidth", "sideheight", "mainjpegquality", "sidejpegquality"]
interfaces = {"Four Camera View": "fourcam", "Two Camera View (Swapable)": "twocam", "One Camera View (Swapable)": "onecam"}

#Multiview Commands
mains = [0, 1]
sides = [2, 3]

def putToDash(self, textbox, value):
    if textbox == "staged":
        staged = ""
        #Lists staged cameras in a gramatically correct manner
        for ind, val in enumerate(value):
            if ind == 0:
                if len(value) > 2:
                    staged += camnames[val] + ", "
                elif len(value) == 1:
                    staged += camnames[val]
                else:
                    staged += camnames[val] + " "
            elif ind == len(value)-1:
                staged += "and " + camnames[val]
            else:
                staged += camnames[val] + ", "
        if len(self.vars["staged"]) > 1:
            text = "The {} cameras are staged".format(staged)
        else:
            text = "The {} camera is staged".format(staged)
        self.textboxes["multiview"][0].setValue(text)
    elif textbox == "active":
        if value == True:
            active = "active"
        elif value == False:
            active = "not active"
        plural = len(self.vars["staged"]) > 1
        if plural:
            text = "The staged cameras are {}".format(active)
        else:
            text = "The staged camera is {}".format(active)
        self.textboxes["multiview"][1].setValue(text)
        if value:
            if plural:
                self.buttons["multiview"][7].setText("Deactivate Cameras")
            else:
                self.buttons["multiview"][7].setText("Deactivate Camera")
        else:
            if plural:
                self.buttons["multiview"][7].setText("Activate Cameras")
            else:
                self.buttons["multiview"][7].setText("Activate Camera")
    elif textbox == "quality":
        #Finds whether main, side, or both hierarchies of camera are staged
        stagedhierarchies = stagedCamHierarchies(self)
        resolutions = ""
        if stagedhierarchies[0] and stagedhierarchies[1]:
            resolutions += "\n({}x{} for main cameras and {}x{} for side cameras)".format(int(480*(value/7)), int(640*(value/7)), int(480*(value/14)), int(640*(value/14)))
        elif stagedhierarchies[0] and (not stagedhierarchies[1]):
            resolutions += "\n({}x{} for main cameras)".format(int(480*(value/7)), int(640*(value/7)))
        elif (not stagedhierarchies[0]) and stagedhierarchies[1]:
            resolutions += "\n({}x{} for side cameras)".format(int(480*(value/14)), int(640*(value/14)))
        else:
            raise ValueError("Staged camera index is empty")
        text = "The current quality preset is {} {}".format(value, resolutions)
        self.textboxes["multiview"][2].setValue(text)
    elif textbox == "color":
        if value:
            color = "RGB"
            self.buttons["multiview"][12].setText("Black & White")
        else:
            color = "B&W"
            self.buttons["multiview"][12].setText("Color")
        text = "Color: {}".format(color)
        self.textboxes["multiview"][3].setValue(text)
    elif textbox == "framerate":
        stagedhierarchies = stagedCamHierarchies(self)
        framerates = ""
        if stagedhierarchies[0] and (not stagedhierarchies[1]):
            framerates += "\n({}fps for main cameras)".format(int(30*(value/7)))
        elif (not stagedhierarchies[0]) and stagedhierarchies[1]:
            framerates += "\n({}fps for side cameras)".format(int(30*(value/7)))
        elif stagedhierarchies[0] and stagedhierarchies[1]:
            framerates += "\n({}fps for main cameras and {}fps for side cameras)".format(int(30*(value/7)), int(20*(value/7)))
        else:
            raise ValueError("Staged camera index is empty")
        text = "The current framerate preset is {} {}".format(value, framerates)
        self.textboxes["multiview"][4].setValue(text)
    elif textbox == "diagnostic":
        self.textboxes["multiview"][5].setValue(text)

def setRemainingTime(self, time):
    text = "Match Currently running \n{} seconds remaning".format(time)
    putToDash(self, "diagnostic", text)

def stagedCamHierarchies(self):
    staged = self.vars["staged"]
    stagedhierarchies = [False, False]
    if (0 in staged) or (1 in staged):
        stagedhierarchies[0] = True
    if (2 in staged) or (3 in staged):
        stagedhierarchies[1] = True
    return stagedhierarchies

def stageFrontCam(self):
    #The staged (active) camera objects
    self.vars["staged"] = [0]
    resetToggles(self, 0)
    visiontable.putNumber("activecam", 0)
    putToDash(self, "staged", self.vars["staged"])

def stageBackCam(self):
    self.vars["staged"] = [1]
    visiontable.putNumber("activecam", 1)
    resetToggles(self, 1)
    putToDash(self, "staged", self.vars["staged"])

def stageLeftCam(self):
    self.vars["staged"] = [2]
    visiontable.putNumber("activecam", 2)
    resetToggles(self, 2)
    putToDash(self, "staged", self.vars["staged"])

def stageRightCam(self):
    self.vars["staged"] = [3]
    visiontable.putNumber("activecam", 3)
    resetToggles(self, 3)
    putToDash(self, "staged", self.vars["staged"])

def stageAllCams(self):
    self.vars["staged"] = [0, 1, 2 ,3]
    resetToggles(self, "all")
    putToDash(self, "staged", self.vars["staged"])

def stageMainCams(self):
    self.vars["staged"] = [0, 1]
    resetToggles(self, "main")
    putToDash(self, "staged", self.vars["staged"])

def stageSubCams(self):
    self.vars["staged"] = [2, 3]
    resetToggles(self, "sub")
    putToDash(self, "staged", self.vars["staged"])

def resetToggles(self, staged):
    resetActivity(self, staged)
    resetColor(self, staged)

def toggleActivity(self):
    """
    Toggles wether the staged cameras are active or not
    """
    self.vars["isactive"] = not self.vars["isactive"]
    if self.vars["isactive"]:
        activateStaged(self)
    else:
        deactivateStaged(self)
    putToDash(self, "active", self.vars["isactive"])


def activateStaged(self):
    staged = getStagedCams(self)
    for camera in staged:
        activate(camera)

def deactivateStaged(self):
    staged = getStagedCams(self)
    for camera in staged:
        deactivate(camera)

def activate(camera):
    camera.active = True
    camera.updateOverNetwork()

def deactivate(camera):
    camera.active = False
    camera.updateOverNetwork()

def increaseFramerate(self):
    #Checks if framerate preset is at or above maximum
    if self.vars["framerate"] >= 7:
        return
    self.vars["framerate"] += 1
    updateToFramerate(self)
    putToDash(self, "framerate", self.vars["framerate"])

def decreaseFramerate(self):
    #Checks if framerate preset is at or below minimum
    if self.vars["framerate"] <= 1:
        return
    self.vars["framerate"] -= 1
    updateToFramerate(self)
    putToDash(self, "framerate", self.vars["framerate"])

def updateToFramerate(self):
    """
    Updates all cameras to the class framerate preset
    """
    staged = getStagedCams(self)
    preset = self.vars["framerate"]
    for ind in self.vars["staged"]:
        camera = staged[ind]
        if ind in mains:
            updateCamToFramerate(camera, preset, main=True)
        elif ind in sides:
            updateCamToFramerate(camera, preset, main=False)
        else:
            raise ValueError("Staged Index {} out of known range".format(self.vars["staged"][ind]))

def updateCamToFramerate(camera, preset, main = True):
    """
    Updates a single camera to one of the preset framerate values
    """
    #Framerate will be higher for main cameras since they are more important
    if main:
        framerate = int(30*(preset/7))
    else:
        framerate = int(20*(preset/7))
    camera.framerate = framerate
    camera.updateOverNetwork()


def increaseQuality(self):
    if self.vars["quality"] >= 7:
        return
    self.vars["quality"] += 1
    updateToQuality(self)
    putToDash(self, "quality", self.vars["quality"])

def decreaseQuality(self):
    if self.vars["quality"] <= 1:
        return
    self.vars["quality"] -= 1
    updateToQuality(self)
    putToDash(self, "quality", self.vars["quality"])

def updateToQuality(self):
    """
    Updates all cameras the class quality preset
    """
    staged = getStagedCams(self)
    preset = self.vars["quality"]
    for ind in self.vars["staged"]:
        camera = staged[ind]
        if ind in mains:
            updateCamToQuality(camera, preset, main=True)
        elif ind in sides:
            updateCamToQuality(camera, preset, main=False)
        else:
            raise ValueError("Staged Index {} out of known range".format(self.vars["staged"][ind]))

def updateCamToQuality(camera, preset, main = True):
    """
    Updates a single camera to one of the preset quality values
    """
    if main:
        quality = (int(480*(preset/7)), int(640*(preset/7)))
    else:
        quality = (int(480*(preset/14)), int(640*(preset/14)))
    camera.width = quality[1]
    camera.height = quality[0]
    camera.updateOverNetwork()

def toggleColor(self):
    """
    Toggles the entire class's color from/to color
    """
    staged = getStagedCams(self)
    self.vars["color"] = not self.vars["color"]
    for camera in staged:
        setCamColor(camera, self.vars["color"])
    putToDash(self, "color", self.vars["color"])

def setCamColor(camera, color):
    """
    Sets a single camera to color/BW
    """
    camera.color = color
    camera.updateOverNetwork()

def resetActivity(self, staged):
    if staged == "all":
            if getActiveCams(4):
                #If any cameras are active
                active = True
            else:
                active = False
    if staged == "main":
        if getActiveCams(2):
            #If any cameras are active
            active = True
        else:
            active = False
    if staged == "sub":
        if getActiveCams(3, 4):
            #If any cameras are active
            active = True
        else:
            active = False
    else:
        if visiontable.getBoolean("{}isactive".format(staged), False):
            active = True
        else:
            active = False
    self.vars["isactive"] = active

def resetColor(self, staged):
    if staged == "all":
        if getColorCams(4):
            #If any cameras are in color mode
            color = True
        else:
            color = False
    if staged == "main":
        if getColorCams(2):
            #If any main cameras are in color mode
            color = True
        else:
            color = False
    if staged == "sub":
        if getColorCams(3, 4):
            #If any sub cameras are in color mode
            color = True
        else:
            color = False
    else:
        if visiontable.getBoolean("{}color".format(staged), False):
            color = True
        else:
            color = False
    self.vars["color"] = color

#Splitcam functions
defaultlocation = (1, 1, 16, 16)

def splitCamInTwo(self, cams, horizontal=True):
    ungridStaged(self)
    if horizontal:
        rows = defaultlocation[0], int((defaultlocation[2]-defaultlocation[0])/2)+2
        columns = defaultlocation[1], defaultlocation[1]
        rowspans = int(defaultlocation[2]/2), int(defaultlocation[2]/2)
        columnspans = defaultlocation[3], defaultlocation[3]
    else:
        rows = defaultlocation[0], defaultlocation[0]
        columns = defaultlocation[1], int((defaultlocation[3]-defaultlocation[1])/2)
        rowspans = defaultlocation[2], defaultlocation[2]
        columnspans = int(defaultlocation[3]/2), int(defaultlocation[3]/2)
    for ind in range(2):
        self.gridWidget(self.cameras["match"][cams[ind]], rows[ind], columns[ind], rowspans[ind], columnspans[ind])
    self.vars["staged"] = cams

def splitToMains(self):
    splitCamInTwo(self, cams=[0, 1])

def splitToSides(self):
    splitCamInTwo(self, cams=[2, 3])

def splitCamInFour(self, order=[0,1,2,3]):
    ungridStaged(self)
    rows = (defaultlocation[0], int((defaultlocation[2]-defaultlocation[0])/4)+2, 
            defaultlocation[0], int((defaultlocation[2]-defaultlocation[0])/4)+2)
    columns = (defaultlocation[1], defaultlocation[1],
            int((defaultlocation[3]-defaultlocation[1])/4)+2, int((defaultlocation[3]-defaultlocation[1])/4)+2)
    rowspans = int(defaultlocation[2]/4), int(defaultlocation[2]/4), int(defaultlocation[2]/4), int(defaultlocation[2]/4)
    columnspans = int(defaultlocation[3]/4), int(defaultlocation[3]/4), int(defaultlocation[3]/4), int(defaultlocation[3]/4)
    for ind in range(4):
        self.gridWidget(self.cameras["match"][order[ind]], rows[ind], columns[ind], rowspans[ind], columnspans[ind])
    self.vars["staged"] = order

def splitToAll(self):
    splitCamInFour(self)

def ungridStaged(self):
    staged = getStagedCams(self)
    for camera in staged:
        self.ungridWidget(camera)

#Onecam functions
def switchCam(self, camnum):
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

#commands.py: Button commands called by interfaces
#1/21/2019 HP

import time
import json

import visglobals
import configuration as config
from visglobals import comsock, piadr, visiontable

camnames = {0: "Front", 1: "Rear", 2: "Left", 3: "Right"}

#Globally used commands
def startMatch(self):
    """
    Sends the Vision System start siginal for a competition match
    """
    sendStartSignal(comsock)
    comsock.close()

def swapOutCam(self, replacedcam, newcam):
    """
    Swaps out a gridded camera for another camera in the same location
    """
    row, column, columnspan, rowspan = replacedcam.ungrid()
    newcam.grid(row, column, columnspan, rowspan)

def sendStartSignal(sock):
    sock.sendto(b"i", piadr)

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
interfaces = {"Four Camera View": "fourcam", "Two Camera View (Swapable)": "twocam", "One Camera View (Swapable": "onecam"}

#Multiview Commands
mains = [0, 1]
sides = [2, 3]

def putToDash(self, textbox, value):
    if textbox == "staged":
        staged = ""
        #Lists staged cameras in a gramatically correct manner
        for ind, val in enumerate(value):
            print(ind, len(value))
            if ind == 0:
                if len(value) > 2:
                    staged += camnames[val] + ", "
                elif len(value) == 1:
                    staged += camnames[val]
                else:
                    staged += camnames[val] + " "
            elif ind == len(value)-1:
                print("Here")
                staged += "and " + camnames[val]
            else:
                staged += camnames[val] + ", "
        if len(self.vars["isstaged"]) > 1:
            text = "The {} cameras are staged".format(staged)
        else:
            text = "The {} camera is staged".format(staged)
        print(text)
        print(self.textboxes)
        self.textboxes["multiview"][0].setValue(text)
    elif textbox == "active":
        if value == True:
            active = "active"
        elif value == False:
            active = "not active"
        plural = len(self.vars["isstaged"]) > 1
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
        print(stagedhierarchies)
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
    staged = self.vars["isstaged"]
    stagedhierarchies = [False, False]
    if (0 in staged) or (1 in staged):
        stagedhierarchies[0] = True
    if (2 in staged) or (3 in staged):
        stagedhierarchies[1] = True
    return stagedhierarchies

def stageFrontCam(self):
    #The staged (active) camera objects
    self.vars["staged"] = self.cameras["multiview"][0]
    #List of the indices of staged cameras
    self.vars["isstaged"] = [0]
    resetToggles(self, 0)
    putToDash(self, "staged", self.vars["isstaged"])

def stageBackCam(self):
    self.vars["staged"] = self.cameras["multiview"][1]
    self.vars["isstaged"] = [1]
    resetToggles(self, 1)
    putToDash(self, "staged", self.vars["isstaged"])

def stageLeftCam(self):
    self.vars["staged"] = self.cameras["multiview"][2]
    self.vars["isstaged"] = [2]
    resetToggles(self, 2)
    putToDash(self, "staged", self.vars["isstaged"])

def stageRightCam(self):
    self.vars["staged"] = self.cameras["multiview"][3]
    self.vars["isstaged"] = [3]
    resetToggles(self, 3)
    putToDash(self, "staged", self.vars["isstaged"])

def stageAllCams(self):
    self.vars["staged"] = self.cameras["multiview"]
    self.vars["isstaged"] = [0, 1, 2 ,3]
    resetToggles(self, "all")
    putToDash(self, "staged", self.vars["isstaged"])

def stageMainCams(self):
    self.vars["staged"] = self.cameras["multiview"][:2]
    self.vars["isstaged"] = [0, 1]
    resetToggles(self, "main")
    putToDash(self, "staged", self.vars["isstaged"])

def stageSubCams(self):
    self.vars["staged"] = self.cameras["multiview"][2:]
    self.vars["isstaged"] = [2, 3]
    resetToggles(self, "sub")
    putToDash(self, "staged", self.vars["isstaged"])

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
    if type(self.vars["staged"]) == list:
        for camera in self.vars["staged"]:
            activate(camera)
    else:
        camera = self.vars["staged"]
        activate(camera)

def deactivateStaged(self):
    if type(self.vars["staged"]) == list:
        for camera in self.vars["staged"]:
            deactivate(camera)
    else:
        camera = self.vars["staged"]
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
    preset = self.vars["framerate"]
    if type(self.vars["staged"]) == list:
        for ind, camera in enumerate(self.vars["staged"]):
            if self.vars["isstaged"][ind] in mains:
                updateCamToFramerate(camera, preset, main=True)
            elif self.vars["isstaged"][ind] in sides:
                updateCamToFramerate(camera, preset, main=False)
            else:
                raise ValueError("Staged Index {} out of known range".format(self.vars["isstaged"][ind]))
    else:
        camera = self.vars["staged"]
        if self.vars["isstaged"][0] in mains:
            updateCamToFramerate(camera, preset, main=True)
        elif self.vars["isstaged"][0] in sides:
            updateCamToFramerate(camera, preset, main=False)
        else:
            raise ValueError("Staged Index {} out of known range".format(self.vars["isstaged"][0]))

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
    preset = self.vars["framerate"]
    if type(self.vars["staged"]) == list:
        for ind, camera in enumerate(self.vars["staged"]):
            if self.vars["isstaged"][ind] in mains:
                updateCamToQuality(camera, preset, main=True)
            elif self.vars["isstaged"][ind] in sides:
                updateCamToQuality(camera, preset, main=False)
            else:
                raise ValueError("Staged Index {} out of known range".format(self.vars["isstaged"][ind]))
    else:
        camera = self.vars["staged"]
        if self.vars["isstaged"][0] in mains:
            updateCamToQuality(camera, preset, main=True)
        elif self.vars["isstaged"][0] in sides:
            updateCamToQuality(camera, preset, main=False)
        else:
            raise ValueError("Staged Index {} out of known range".format(self.vars["isstaged"][0]))

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
    self.vars["color"] = not self.vars["color"]
    if type(self.vars["staged"]) == list:
        for camera in self.vars["staged"]:
            setCamColor(camera, self.vars["color"])
    else:
        camera = self.vars["staged"]
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

def stageOneCam(self, camnum):
    camera = self.cameras["match"][camnum]
    self.replace(self.vars["staged"], camera)
    self.vars["staged"] = camera

def splitCamInTwo(self, cams, horizontal=True):
    if type(self.vars["staged"]) == list:
        for camera in self.vars["staged"]:
            camera.ungrid()
    else:
        self.vars["staged"].ungrid()
    if horizontal:
        rows = defaultlocation[0], int((defaultlocation[2]-defaultlocation[0])/2)
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
    self.vars["staged"] = [self.cameras["match"][cams[0]], self.vars["match"][cams[1]]]

def splitToMains(self):
    splitCamInTwo(self, cams=[0, 1])

def splitToSides(self):
    splitCamInTwo(self, cams=[2, 3])

def splitCamInFour(self, order=[0,1,2,3]):
    rows = defaultlocation[0], defaultlocation[0], int((defaultlocation[2]-defaultlocation[0])/2), int((defaultlocation[2]-defaultlocation[0])/2)
    columns = defaultlocation[1], int((defaultlocation[3]-defaultlocation[1])/2), defaultlocation[1], int((defaultlocation[3]-defaultlocation[1])/2)
    rowspans = int(defaultlocation[2]/2), int(defaultlocation[2]/2)
    columnspans = int(defaultlocation[3]/2), int(defaultlocation[3]/2)
    for ind in range(4):
        self.gridWidget(self.cameras["match"][order[ind]], rows[ind], columns[ind], rowspans[ind], columnspans[ind])
    self.vars["staged"] = [self.cameras["match"][order[0]], self.vars["match"][order[1]], [self.cameras["match"][order[2]], self.vars["match"][order[3]]]]

def splitToAll(self):
    splitCamInFour(self)

def ungridStaged(self):
    if type(self.vars["staged"]) == list:
        for camera in self.vars["staged"]:
            self.ungridWidget(camera)
    else:
        self.ungridWidget(self.vars["staged"])

#Onecam functions
def switchCam(self, camnum):
    ungridStaged(self)
    camera = self.cameras["match"][camnum]
    self.gridWidget(camera, defaultlocation[0], defaultlocation[1], defaultlocation[2], defaultlocation[3])
    self.vars["staged"] = camera

def switchOneCam(self, camnum):
    camera = self.cameras["match"][camnum]
    self.replaceWidget(self.vars["staged"], camera)
    self.vars["staged"] = camera

def frontCam(self):
    switchCam(self, 0)

def backCam(self):
    switchCam(self, 1)

def leftCam(self):
    switchCam(self, 2)

def rightCam(self):
    switchCam(self, 3)

#Universal Competition Functions
def toggleBandwidth(self):
    print(self)
    if self.vars["bandwidthreduced"]:
        normalBandwidthMode(self)
        self.vars["namedwidgets"]["toggleBandwidth"].setText("Reduce Bandwidth")
    else:
        lowBandwidthMode(self)
        self.vars["namedwidgets"]["toggleBandwidth"].setText("Return To Normalcy!")

def normalBandwidthMode(self):
    if type(self.vars["staged"]) == list:
        for ind in self.vars["isstaged"]:
            camera = self.cameras["match"][ind]
            main = ind in mains
            increaseBandwidth(camera, main)
    else:
        main = self.vars["isstaged"][0] in mains
        increaseBandwidth(self.vars["staged"], main)
    self.vars["bandwidthreduced"] = False

def lowBandwidthMode(self):
    if type(self.vars["staged"]) == list:
        for ind in self.vars["isstaged"]:
            camera = self.cameras["match"][ind]
            main = ind in mains
            reduceBandwidth(camera, main)
    else:
        main = self.vars["isstaged"][0] in mains
        reduceBandwidth(self.vars["staged"], main)
    self.vars["bandwidthreduced"] = True

def reduceBandwidth(camera, main=True):
    if main:
        camera.framerate = 10
        camera.width = 91
        camera.height = 68
        camera.quality = 40
    else:
        camera.framerate = 8
        camera.width = 34
        camera.height = 45
        camera.quality = 40
    camera.updateOverNetwork()

def increaseBandwidth(camera, main=True):
    if main:
        camera.framerate = 20
        camera.width = 365
        camera.height = 274
        camera.quality = 95
    else:
        camera.framerate = 15
        camera.width = 137
        camera.height = 182
        camera.quality = 95
    camera.updateOverNetwork()

def updateStagedCams(self):
    for cam in self.vars["staged"]:
        cam.updateImgOnLabel()

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

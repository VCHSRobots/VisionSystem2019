#commands.py: Button commands called by interfaces
#1/21/2019 HP

import time

import visglobals
from visglobals import comsock, piadr, visiontable

#Globally used commands
def startMatch(self):
    """
    Starts Vision System for a competition match
    """
    #This commmand is called from multiple sources, not just by menus
    #Creates a socket for two-way communication with the pi
    sendStartSignal(comsock)
    matchLoop(self)
    comsock.close()

def swapOutCam(self, replacedcam, newcam):
    """
    Swaps out a gridded camera for another camera in the same location
    """
    row, column, columnspan, rowspan = replacedcam.ungrid()
    newcam.grid(row, column, columnspan, rowspan)

def sendStartSignal(sock):
    sock.sendto(b"i", piadr)

def matchLoop(self): #, timeout=180):
    """
    Updates all cameras on an interface
    """
    #starttime = time.perf_counter()
    #while time.perf_counter()-starttime < 180:
    #if self.active:
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
    for interface in self.cameras:
        for camera  in interface:
            if not camera.location:
                camera.active = False
                camera.updateCamOverNetwork()

#Multiview Commands
mains = [0, 1]
sides = [2, 3]

def setupMultiview(self):
    stageAllCams(self)
    self.vars["isactive"] = True
    self.vars["color"] = True
    self.vars["quality"] = 4
    self.vars["fps"] = 4

def putToDash(self, textbox, value):
    if textbox == "staged":
        value = convertCamIndsToNames(value)
        staged = ""
        #Lists staged cameras in a gramatically correct manner
        for ind, camname in enumerate(value):
            if ind < camname-1:
                staged += camname + ", "
            elif ind != 0:
                staged += "and " + camname
            else:
                staged = camname
        text = "The {} cameras are staged".format(staged)
        self.textboxes["multiview"][0] = text
    elif textbox == "active":
        if value == True:
            active = "active"
        elif value == False:
            active = "not active"
        if len(self.vars["isstaged"]) > 1:
            text = "The staged cameras are {}".format(active)
        else:
            text = "The staged camera is {}".format(active)
        self.textboxes["multiview"][1] = text
        if value:
            self.buttons["multiview"].text = "Deactivate Cameras"
        else:
            self.buttons["multiview"].text = "Activate Cameras"
    elif textbox == "quality":
        #Finds whether main, side, or both hierarchies of camera are staged
        stagedhierarchies = stagedCamHierarchies(self)
        resolutions = ""
        if stagedhierarchies[0] and (not stagedhierarchies[1]):
            resolutions += "({}x{} for main cameras)".format(int(480*(value/7)), int(640*(value/7)))
        elif (not stagedhierarchies[0]) and stagedhierarchies[1]:
            resolutions += "({}x{} for side cameras)".format(int(480*(value/14)), int(640*(value/14)))
        elif stagedhierarchies[0] and stagedhierarchies[1]:
            resolutions += "({}x{} for main cameras and {}x{} for side cameras)".format(int(480*(value/7)), int(640*(value/7)), int(480*(value/14)), int(640*(value/14)))
        else:
            raise ValueError("Staged camera index is empty")
        text = "The current quality preset is {} {}".format(value, resolutions)
        self.textboxes["multiview"][2] = text
    elif textbox == "color":
        if value:
            color = "RGB"
        else:
            color = "B&W"
        text = "Color: {}".format(color)
        self.textboxes["multiview"][3] = text
    elif textbox == "framerate":
        stagedhierarchies = stagedCamHierarchies(self)
        framerates = ""
        if stagedhierarchies[0] and (not stagedhierarchies[1]):
            framerates += "({}fps for main cameras)".format(int(30*(value/7)))
        elif (not stagedhierarchies[0]) and stagedhierarchies[1]:
            framerates += "({}fps for side cameras)".format(int(30*(value/7)))
        elif stagedhierarchies[0] and stagedhierarchies[1]:
            framerates += "({}fps for main cameras and {}fps for side cameras)".format(int(30*(value/7)), int(20*(value/7)))
        else:
            raise ValueError("Staged camera index is empty")
        text = "The current framerate preset is {} {}".format(value, framerates)
        self.textboxes["multiview"][3] = text
    elif textbox == "diagnostic":
        self.textboxes["multiview"][4] = value

def setRemainingTime(self, time):
    text = "Match Currently running \n{} seconds remaning".format(time)
    putToDash(self, "diagnostic", text)

def convertCamIndsToNames(value):
    indnames = {0: "Front", 1: "Rear", 2: "Left", 3: "Right"}
    names = []
    if type(value) == list:
        for camnum in value:
            names.append(indnames[camnum])
    elif type(value) == int or type(value) == float:
        names = [value]
    else:
        raise TypeError("Invalid type passed: {}".format(str(type(value))))
    return names

def stagedCamHierarchies(self):
    staged = self.vars["isstaged"]
    stagedhierarchies = [False, False]
    if (0 in staged) or (1 in staged):
        stagedhierarchies[0] = True
    elif (2 in staged) or (3 in staged):
        stagedhierarchies[0] = True
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
    if self.vars["framerate"] <= 7:
        pass
    self.vars["framerate"] += 1
    updateToFramerate(self)
    putToDash(self, "framerate", self.vars["framerate"])

def decreaseFramerate(self):
    #Checks if framerate preset is at or below minimum
    if self.vars["framerate"] <= 1:
        pass
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
        pass
    self.vars["quality"] += 1
    updateToQuality(self)
    putToDash(self, "quality", self.vars["quality"])

def decreaseQuality(self):
    if self.vars["quality"] <= 1:
        pass
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
    camera.framerate = quality
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

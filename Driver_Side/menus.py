#interfaces.py: Manages which user interface is active
#HP 1/21/2019

import time

import commands
from visglobals import visiontable, null

#Global settings dict
global settings
settings = {"matchtype": "multiview"}
currentinterface = "mainmenu"
matchtime = 180

#Functions to be called when a menu is invoked
def mainMenu(self):
    """
    Main Menu Loop
    Does nothing
    """
    while self.interface == "mainmenu":
        pass

def multiviewMenu(self):
    """
    Multiview Menu Loop
    Updates cameras and keeps a timer running on them
    """
    starttime = time.perf_counter()
    timeleft = 180
    lastmatchcams = self.cameras["match"]
    while self.interface == "multiview":
        if timeleft < 0:
            timepassed = time.perf_counter()-starttime
            timeleft = matchtime-timepassed
            self.setRemainingTime(timeleft)
            commands.matchLoop(self, lastmatchcams)
            lastmatchcams = self.cameras["match"]
        else:
            #TODO: Make this do something appropriate when the match ends
            timeleft = 180

def splitcamMenu(self):
    """
    Splitcam Menu Interface
    Allows the user to split one camera display into several smaller camera displays
    """
    timeleft = 180
    while self.interface == "splitcam":
        if timeleft > 0:
            commands.updateStagedCams(self)
            timeleft = self.timer.updateTime()
        else:
            #TODO: Make this do something appropriate when the match ends
            self.timer.reset()

def onecamMenu(self):
    """
    Onecam Menu Interface
    Displays one camera that can be swapped out
    Plaincomp is much more efficent at this
    """
    while self.interface == "onecam":
        commands.updateStagedCams(self)

def fourcamMenu(self):
    while self.interface == "fourcam":
        commands.updateStagedCams(self)

def testMenu(self):
    """
    Multi camera test interface
    """
    print(self.cameras)
    lastmatchcams = self.cameras["test"]
    while self.interface == "test":
        commands.matchLoop(self, lastmatchcams, interface="test")
        lastmatchcams = self.cameras["test"]
        print("here")

def plaincompMenu(self):
    #Time when the last connected signal was sent
    lastsendtime = 0
    camera = self.cameras["match"][0]
    while self.interface == "plaincomp":
        success = camera.updateImgOnLabel()
        if success:
            currenttime = time.perf_counter()
            if currenttime-lastsendtime >= 1/camera.framerate:
                self.sendConnectedMessage()
                lastsendtime = currenttime
        else:
            #If camera cannot retrieve an image, send a connection siginal at a metered rate
            if time.perf_counter()-lastsendtime >= .2:
                commands.sendIP()
                lastsendtime = time.perf_counter()
            #Checks if camera object changed to FailedCamera
            camera = self.cameras["match"][0]

matchfunctions = {"mainmenu": mainMenu, "settings": mainMenu, 
                "onecammatch": null, "multiview": multiviewMenu,   
                "test": testMenu, "splitcam": splitcamMenu,
                "onecam": onecamMenu, "fourcam": fourcamMenu,
                "plaincomp": plaincompMenu}

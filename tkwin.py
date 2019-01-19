#tkwin.py: A class to manage tkinter's interaction with FRC networktables
#1/8/2019 HP

#Module Imports
import threading
import networktables
import re #Used for string processing
import tkinter as tk
from networktables import NetworkTables as nt

#Local Imports
import labels

#Globals
#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")

class TkWin:
    def __init__(self, name, width = 100, height = 100):
        #TODO width and height are magic numbers
        self.name = name
        self.root = tk.Tk()
        self.root.title = name #Sets the title of the window as the user sees it
        self.root.geometry("{0}x{1}".format(width, height))
        #Lists of different types of labels
        self.cameras = []
        self.localcameras = []
        self.buttons = []
        self.textboxes = []
        self.entries = []
        self.active = True
        #List of all filled points on the window's grid
        self.filled = []
        self.threadloop = null

    def runWin(self):
        """
        Initiates the tkinter window while running the instance's set thread function
        """
        thread = threading.Thread(target=self.threadLoop)
        thread.start()
        self.root.mainloop()

    def setThreadLoop(self, func):
        """
        Sets the function to be run when self.runWin is called
        """
        self.threadloop = func

    def threadLoop(self):
        self.threadloop(self)

    def addCam(self, camnum):
        """
        Tries to add a remote camera to the window; returns False if it fails
        """
        if visiontable.getBoolean("{0}isactive".format(camnum), False):
            self.cameras.append(labels.Camera(camnum, self.root))
            return True
        return False
        
    def setCamColor(self, camind, color):
        """
        Sets the color of the camera's socket output
        """
        self.localcameras[camind].color = color
    
    def addLocalCam(self, camnum):
        """
        Local variant of addCam
        """
        camera = labels.LocalCamera(camnum, self.root)
        if camera.active:
            self.localcameras.append(camera)
            return True
        else:
            return False
        
    def setLocalCamColor(self, camind, color):
        """
        Local variant of setCamColor
        """
        self.cameras[camind].color = color

    def addButton(self, text, command):
        """
        Adds a button to the class registry
        """
        self.buttons.append(tk.Button(self.root, text=text, command=command))

    def addEntry(self, name, convtype, defaultval=None):
        """
        Adds a user entry field to the class registry
        """
        entry = labels.Entry(name, convtype, defaultval)
        self.entries[name] = entry
    
    def processGuiMap(self, guimap):
        """
        Places items on grid based on a dimensioned array with integers standing for different components
        EX:
        [[[0, 0, 1, 1, 1]
        [0, 0, 1, 1, 1]
        [0, 0, 1, 1, 1]],
        {1: "camera1"}]
        would place the first camera the window recognizes on column 2 row 1 with a columnspan of 3 and rowspan of 3
        """
        labelspans = findLabelSpans(guimap)
        for num in guimap[1]:
            labelnum = int(re.sub(r"[a-zA-Z]", "", guimap[1][num]))
            labeltype = re.sub(r"[0-9]", "", guimap[1][num])
            if labeltype.lower() == "camera":
                label = self.cameras[labelnum]
            elif labeltype.lower() == "button":
                label = self.buttons[labelnum]
            elif labeltype.lower() == "entry":
                label = self.entries[labelnum]
            elif labeltype.lower() == "textbox":
                label = self.textboxes[labelnum]
            num = int(num)
            label.label.grid(column = labelspans[num][0], row = labelspans[num][2], columnspan = labelspans[num][1]-labelspans[num][0], rowspan = labelspans[num][3]-labelspans[num][2])

    def killLoop(self):
        self.active = False
        
    def pollForCams(self, camrange):
        """
        Checks for active cams on the network
        """
        for num in range(camrange):
            self.addCam(num)

    def emergencyShutdown(self):
        """
        Safely shuts down system in case of error
        """
        for cam in self.cameras:
            cam.shutdown()
        for cam in self.localcameras:
            cam.shutdown()

def null(self):
    pass

def findLabelSpans(guimap):
    """
    Detects griding paramiters from a gui file list
    """
    labelspans = {} #{num: (firstcolumn, lastcolumn, firstrow, lastrow)}
    firstcolumn, lastcolumn, firstrow, lastrow = None, None, None, None
    numencountered = False
    for num in guimap[1]:
        num = int(num)
        for ind, row in enumerate(guimap[0]):
            if num in row:
                if not numencountered:
                    firstrow = ind
                    firstcolumn = row.index(num)
                    lastcolumn = len(row)-row[::-1].index(num)-1
                    numencountered = True
                    continue
                elif numencountered:
                    lastrow = ind
                    break
        labelspans[num] = (firstcolumn, lastcolumn, firstrow, lastrow)
        numencountered = False
    return labelspans

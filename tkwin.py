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
        thread = threading.Thread(target=self.threadLoop, args=(self))
        thread.start()
        self.root.mainloop()

    def setThreadLoop(self, func):
        self.threadloop = func

    def threadLoop(self):
        self.threadloop()

    def addCam(self, camnum):
        camera = labels.Camera(camnum, self.root)
        if camera.active:
            self.cameras.append(camera)
            return True
        else:
            return False
        
    def setCamColor(self, camind, color):
        self.localcameras[camind].color = color
    
    def addLocalCam(self, camnum):
        camera = labels.LocalCamera(camnum, self.root)
        if camera.active:
            self.localcameras.append(camera)
            return True
        else:
            return False
        
    def setLocalCamColor(self, camind, color):
        self.cameras[camind].color = color

    def addButton(self, text, command):
        self.buttons.append(tk.Button(root, text=text, command=command))

    def addEntry(self, name, convtype, defaultval=None):
        entry = labels.Entry(name, convtype, defaultval)
        self.entries[name] = entry
    
    def processGuiMap(self, guimap):
        """
        Places items on grid based on a dimensioned array with integers standing for different components
        """
        """
        EX:
        [
        [[0, 0, 1, 1, 1]
        [0, 0, 1, 1, 1]
        [0, 0, 1, 1, 1]],
        {1: "camera1"}
        ]
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
        label.grid(column = objspans[num][0], row = objspans[num][2], columnspan = objspans[num][1]-objspans[num][0], rowspan = objspans[num][3]-objspans[num][2])

    def killLoop(self):
        self.active = False

def null():
    pass
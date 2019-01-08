#ui.py: An app made with the grid tkinter ui instead of pack
#1/7/2019 HP

#Module Imports
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
import threading
import imutils
import numpy as np
import re #Used for string processing
from networktables import NetworkTables as nt

#Local Imports
import network as localnet #UTP networking library with vision system

#Globals
"""
ip = "10.44.15.1"
nt.initialize(ip)
visiontable = nt.getTable("/vision")
netsock = localnet.initSocket(ip, localnet.TCP, 5800)
"""


class TkWin:
    def __init__(self, name):
        self.name = name
        self.root = tk.Tk()
        self.root.title = name #Sets the title of the window as the user sees it
        #Lists of different types of labels
        self.cameras = []
        self.localcameras = []
        self.buttons = []
        self.textboxes = []
        self.entries = []
        self.active = True
        #List of all filled points on the window's grid
        self.filled = []

    def threadLoop(self):
        while self.active:
            for camera in self.cameras:
                if camera.active:
                    camera.upCam()
            

    def addCam(self, camnum):
        camera = Camera(camnum, self.root)
        if camera.active:
            self.cameras.append(camera)
            return True
        else:
            return False
        
    def setCamColor(self, camind, color):
        self.localcameras[camind].color = color
    
    def addLocalCam(self, camnum):
        camera = LocalCamera(camnum, self.root)
        if camera.active:
            self.localcameras.append(camera)
            return True
        else:
            return False
        
    def setLocalCamColor(self, camind, color):
        self.cameras[camind].color = color

    def addButton(self, text, function):
        self.buttons.append(tk.Button(root, text=text, command=command))

    def addEntry(self, name, convtype, defaultval=None):
        entry = Entry(name, convtype, defaultval)
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
    
    def gridObj(self, obj, coulmn, row, cspan=1, rspan=1):
        #Puts any type of griddable object on the grid
        #May or may not be used: is slow but safe, but may be depreciated by processGuiMap
        if not self.spaceIsFilled(column, row, cspan, rspan):
            obj.grid(row=row, column=column, coulmnspan=cspan, rowspan=rspan)
            setOnGrid(column, row, cspan, rspan)
            return True
        else:
            return False

    def setOnGrid(self, column, row, cspan, rspan):
        top, bottom, right, left = findCornerPoints(column, row, cspan, rspan)
        self.filled += findFilledPoints(top, bottom, left, right)

    def isFilled(self, point):
        #Tells whether an (x, y) point pair is occupied on the grid
        if point in self.filled:
            return True
        else:
            return False
    
    def spaceIsFilled(column, row, cspan, rspan):
        top, bottom, right, left = findCornerPoint(column, row, cspan, rspan)
        points = findFilledPoints(top, bottom, right, left)
        for point in points:
            if self.isFilled(point):
                return True
        return False
            
def findCornerPoints(column, row, cspan=1, rspan=1):
    top = row
    bottom = row+rspan-1
    left = column
    right = column+cspan-1
    return top, bottom, left, right

def findFilledPoints(top, bottom, left, right):
    filled = []
    for x in range(left, right+1):
        for y in range(top, bottom+1):
            filled.append((x, y))
    return filled

"""
#Test code
top, bottom, left, right = findCornerPoints(1, 1, 2, 3)
filled = findFilledPoints(top, bottom, left, right)
print(top, bottom, left, right, filled)
"""

class Camera:
    #Class which reaches over the global network for camera access: for a local variant, use LocalCamera
    def __init__(self, camnum, root):
        #Camnum must match up with camnum on robot network
        testcam = pinet.makeCam(camnum)
        if testcam:
            self.cam = testcam
            self.camnum = camnum
            self.active = True
            #TODO: Width and Height are magic numbers: replace them with a good default.
            self.width = 100
            self.height = 100
            self.color = "GRAY"
            self.framerate = 10
            updateCamOverNetwork()
            self.label = tk.Label(root)
        else:
            testcam.release()
            self.active = False
    
    def updateImgOnLabel(self):
        #Places an image from the networked camera on the label
        image = self.processIncomingImage()
        label['image'] = image

    def setOnGrid(self, row, column, cspan, rspan):
        self.label.grid(column=column, row=row, coulmnspan=cspan, rowspan=rspan)
    
    def updateCamOverNetwork(self):
        #Updates Networktable data about the specefic camera
        visiontable.putBoolean("{0}active".format(self.camnum), self.active)
        visiontable.putNumber("{0}width".format(self.camnum), self.width)
        visiontable.putNumber("{0}height".format(self.camnum), self.height)
        visiontable.putString("{0}color".format(self.camnum), self.color)
        visiontable.putNumber("{0}framerate".format(self.camnum), self.framerate)
        
    def getImgFromNetwork(self):
        img = localnetwork.getImgUtp(netsock, self.camnum+5800)
        img = processIncomingImg(img)
        return img
    
    def processIncomingImg(self, img):
        img = pickle.loads(img)
        img = Image.fromarray(img)
        img = ImageTK.PhotoImage(image)
        return img

class LocalCamera:
    def __init__(self, camnum, root):
        testcam = cv.VideoCapture(camnum)
        ret, _ = testcam.read()
        if ret:
            self.cam = testcam
            self.camnum = camnum
            self.active = True
            #TODO: Width and Height are magic numbers: replace them with a good default.
            self.width = 100
            self.height = 100
            self.color = "GRAY"
            self.framerate = 10
            self.label = tk.Label(root)
        else:
            testcam.release()
            self.active = False
    
    def setOnGrid(self, row, column, cspan, rspan):
        self.label.grid(column=column, row=row, coulmnspan=cspan, rowspan=rspan)

    def updateCam(self):
        _, frame = self.cam.read()
        img = self.processImg(frame)
        self.label.config(image=img)
        self.label.img = img

    def processImg(self, img):
        #Array Processing
        if self.color == "RGB":
            img = cv.cvtcolor(img, cv.BGR2RGB)
        elif self.color == "GRAY":
            img = cv.cvtcolor(img, cv.BGR2GRAY)
        img = imutils.resize(width=self.width, height=self.height)
        #Conversions
        img = Image.fromarray(img)
        img = ImageTK.PhotoImage(image)
        return img


class Entry:
    def __init__(self, root, name, convtype, defaultval):
        self.entry = tk.Entry(root)
        self.var = tk.StringVar()
        self.value = defaultval
        #The type to convert this entry's values to on updates
        self.type = convtype

    def updateVal(self):
        self.value = self.type(self.var.get())

def findLabelSpans(guimap):
    labelspans = {} #{num: (firstcolumn, lastcolumn, firstrow, lastrow)}
    firstcolumn, lastcolumn, firstrow, lastrow = None, None, None, None
    numencountered = False
    for num in guimap[1]:
        for ind, row in enumerate(guimap[0]):
            print(row)
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

"""
win = TkWin("Hello")
for num in range(4):
    win.addLocalCam(num)
win.addButton("Start", win.threadloop)
win.addButton("Stop", win.killLoop)
win.addEntry("Cameranum", int, 0)
"""

labelgrid = [[[0, 0, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 0, 0]],
            {1: "camera1"}]
print(findLabelSpans(labelgrid))


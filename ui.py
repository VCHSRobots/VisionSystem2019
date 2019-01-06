#ui.py: An app made with the grid tkinter ui instead of pack
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
import threading
import imutils
import numpy as np

class TkWin:
    def __init__(self, name):
        self.name = name
        self.root = tk.Tk()
        self.root.title = name
        self.cameras = []
        self.buttons = []
        self.entries = {}
        self.active = True
        #list of all filled points on the window's grid
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
        self.cameras[camind].color = color

    #Depreciated, use gridObj instead
    def gridCam(self, camind, row, column, cspan=1, rspan=1):
        if not self.spaceIsFilled(column, row, cspan, rspan):
            cameras[camind].setOnGrid(row, column, cspan, rspan)
            setOnGrid(column, row, cspan, rspan)
            return True
        else:
            return False
    
    def addButton(self, text, function):
        self.buttons.append(tk.Button(root, text=text, command=command))
    
    #Depreciated, use gridObj instead
    def gridButton(self, bind, coulmn, row,  cspan=1, rspan=1):
        if not self.spaceIsFilled(coulmn, row, cspan, rspan):
            self.buttons[bind].grid(row=row, column=column, coulmnspan=cspan, rowspan=rspan)
            setOnGrid(coulmn, row, cspan, rspan)
            return True
        else:
            return False
    
    def addEntry(self, name, convtype, defaultval=None):
        entry = Entry(name, convtype, defaultval)
        self.entries[name] = entry

    def gridObj(self, obj, coulmn, row, cspan=1, rspan=1):
        #puts any type of griddable object on the grid
        if not self.spaceIsFilled(column, row, cspan, rspan):
            obj.grid(row=row, column=column, coulmnspan=cspan, rowspan=rspan)
            setOnGrid(column, row, cspan, rspan)
            return True
        else:
            return False

    def killLoop(self):
        self.active = False
    
    def setOnGrid(self, column, row, cspan, rspan):
        top, bottom, right, left = findCornerPoints(column, row, cspan, rspan)
        self.filled += findFilledPoints(top, bottom, left, right)

    def isFilled(self, point):
        #tells whether an (x, y) point pair is occupied on the grid
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
    def __init__(self, camnum, root):
        testcam = cv.VideoCapture(camnum)
        ret, _ = testcam.read()
        if ret:
            self.cam = testcam
            self.active = True
            #TODO: Width and Height are magic numbers: replace them with a good default.
            self.width = 100
            self.height = 100
            self.color = "RGB"
            #TODO: Currently unused
            self.framerate = "auto"
            self.label = tk.Label(root)
        else:
            testcam.release()
            self.active = False
    
    def setOnGrid(self, row, column, cspan, rspan):
        self.label.grid(column=column, row=row, coulmnspan=cspan, rowspan=rspan)

    def upCam(self):
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
        #the type to convert this entry's values to on updates
        self.type = convtype

    def updateVal(self):
        self.value = self.type(self.var.get())

def setItemlistOnGrid(items, coulmnrange, rowspan, cspan, rspan):
    pass

def setButtonsOnGrid(win, coulmnrange):
    pass

def setEntriesOnGrid(win, coulmnrange):
    pass

def setItemsOnGrid(win, coulmnrange):
    pass

win = TkWin("Hello")
for num in range(4):
    win.addCam(num)
win.addButton("Start", win.threadloop)
win.addButton("Stop", win.killLoop)
win.addEntry("Cameranum", int, 0)


#ui.py: An app made with the grid tkinter ui instead of pack
#1/7/2019 HP

#Module Imports
import imutils
import zlib
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
from networktables import NetworkTables as nt

#Local Imports
import network as localnet #UTP networking library with vision system

#Globals
ip = "10.44.15.1"
nt.initialize(ip)
visiontable = nt.getTable("/vision")
netsock = localnet.initSocket(ip, localnet.TCP, 5800)

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
            self.compression = 6
            updateCamOverNetwork()
            self.label = tk.Label(root)
        else:
            del testcam
            self.active = False
    
    def updateImgOnLabel(self):
        #Places an image from the networked camera on the label
        image = self.processIncomingImage()
        label.configure(image=image)
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
        visiontable.putNumber("{0}compression".format(self.camnum), self.compression)
        
    def getImgFromNetwork(self):
        img = localnetwork.getImgUtp(netsock, self.camnum+5800)
        img = processIncomingImg(img)
        return img
    
    def processIncomingImg(self, img):
        img = pickle.loads(img)
        img = zlib.decompress(img)
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
#labels.py: Classes and functions to manage tkinter items and their different behaviors
#1/7/2019 HP

#Module Imports
import socket
import imutils
import zlib
import cv2
import io
import tkinter as tk
from PIL import Image
from PIL import ImageTk
from networktables import NetworkTables as nt

#Local Imports
import network as localnet #UTP networking library with vision system

#Globals
#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")

class Camera:
    #Class which reaches over the global network for camera access: for a local variant, use LocalCamera
    def __init__(self, camnum, root):
        #Camnum will match up with camnum on robot network
        self.root = root
        self.camnum = camnum
        self.active = True
        #TODO: Width and Height are magic numbers: replace them with a good default.
        self.width = 100
        self.height = 100
        self.color = True
        self.framerate = 10
        self.quantization = 8
        self.compression = 6
        self.quality = 95
        self.maxsize = 50000
        self.updateCamOverNetwork()
        self.label = tk.Label(root)
        #Makes a listener socket bound to this specific camera
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, camnum+5800))
        #Finds the size of the image to be recieved from the network
        self.size = visiontable.getNumber("{0}size", 0)
        
    def updateImgOnLabel(self):
        """
        Places the latest image from the socket stream port aligning with the camnum
        """
        #Places an image from the networked camera on the label
        image = self.getImgFromNetwork()
        self.label.configure(image=image)
        self.label['image'] = image

    def setOnGrid(self, row, column, cspan, rspan):
        """
        Sets the camera on the user interface
        """
        self.label.grid(column=column, row=row, coulmnspan=cspan, rowspan=rspan)
    
    def updateCamOverNetwork(self):
        """
        Updates Networktable data about the camera
        """
        visiontable.putBoolean("{0}active".format(self.camnum), self.active)
        visiontable.putNumber("{0}width".format(self.camnum), self.width)
        visiontable.putNumber("{0}height".format(self.camnum), self.height)
        visiontable.putBoolean("{0}color".format(self.camnum), self.color)
        visiontable.putNumber("{0}framerate".format(self.camnum), self.framerate)
        visiontable.putNumber("{0}quantization".format(self.camnum), self.quantization)
        visiontable.putNumber("{0}compression".format(self.camnum), self.compression)
        visiontable.putNumber("{0}quality".format(self.camnum), self.quality)
        visiontable.putNumber("{0}maxsize".format(self.camnum), self.maxsize)
        
    def getImgFromNetwork(self):
        """
        Polls the latest image from the network socket which corresponds with the camera number
        """
        img = self.sock.recv(self.maxsize)
        img = self.processIncomingImg(img)
        return img
    
    def processIncomingImg(self, img):
        """
        Converts a bytes jpeg image to the TKInter usable format
        """
        #Decompresses IOBytes image
        img = zlib.decompress(img)
        #Turns image into bytes string
        img = io.BytesIO(img)
        #Opens image as if it were a file object
        img = Image.open(img)
        img = ImageTk.PhotoImage(img)
        return img

    def shutdown(self):
        self.sock.close()
    
class LocalCamera:
    """
    All functions matching with Camera share identical documentation
    """
    def __init__(self, camnum, root):
        testcam = cv2.VideoCapture(camnum)
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
    
    def setOnGrid(self, row, column, columnspan, rowspan):
        print("Hello World")
        self.label.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

    def updateCam(self):
        _, frame = self.cam.read()
        img = self.processImg(frame)
        self.label.config(image=img)
        self.label.img = img

    def processImg(self, img):
        #Array Processing
        if self.color == "RGB":
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif self.color == "GRAY":
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = imutils.resize(image = img, width=self.width, height=self.height)
        #Conversions
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        return img

    def shutdown(self):
        self.cam.release()

class Entry:
    def __init__(self, root, name, defaultval):
        self.entry = tk.Entry(root)
        self.var = tk.StringVar()
        self.value = defaultval

    def updateVal(self):
        """
        Recieves any input from the user-input field and puts it in self.var as a string
        """
        self.value = str(self.var.get())

    def shutdown(self):
        pass

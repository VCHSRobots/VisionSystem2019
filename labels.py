#labels.py: Classes and functions to manage tkinter items and their different behaviors
#1/7/2019 HP

#Module Imports
import socket
import imutils
import zlib
import cv2
import io
import time
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image
from PIL import ImageTk
from networktables import NetworkTables as nt

#Globals
#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")

def null(self):
    pass

class Camera:
    #Class which reaches over the global network for camera access: for a local variant, use LocalCamera
    def __init__(self, camnum, root):
        #Camnum will match up with camnum on robot network
        self.root = root
        self.camnum = camnum
        self.active = True
        #TODO: Width and Height are magic numbers: replace them with a good default.
        self.width = 500
        self.height = 500
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
        self.label.config(image=image)
        self.label.image = image

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
        img = np.asarray(img)
        img = imutils.resize(img, width = self.width, height = self.height)
        img = cv2.cvtColor(img, self.color)
        img = Image.fromarray(img)
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
        #img = imutils.resize(image = img, width=self.width, height=self.height)
        #Conversions
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        return img

    def shutdown(self):
        self.cam.release()

class Widget:
    def __init__(self, root):
        self.value = tk.StringVar()

    def getValue(self):
        """
        Recieves any input from the user-input field and puts it in self.var as a string
        """
        return str(self.value.get())

class Entry(Widget):
    def __init__(self, root, name):
        self.root = root
        self.value = tk.StringVar()
        self.entry = tk.Entry(root, textvariable=self.value)

class Button:
    def __init__(self, root, text, command):
        self.root = root
        self.button = tk.Button(root, text=text, command=command)
    
    def changeText(self, text):
        self.button["text"] = text

class Checkbox(Widget):
    def __init__(self, root, text, command, onval=True, offval=False):
        self.root = root
        self.value = tk.StringVar()
        self.box = tk.Checkbutton(root, text=text, command=command, onvalue=onval, offvalue=offval)

class RadioButton(Widget):
    def __init__(self, root, buttons):
        self.root = root
        #Buttons are a (displaytext, value) pair
        self.var = tk.StringVar()
        self.options = [tk.Radiobutton(root, text=text, variable=self.var, value=val) for text, val in buttons]
    
    def addOption(self, text, value):
        self.options.append(tk.Radiobutton(self.root, text=text, variable=self.var, value=value))

class Combobox:
    def __init__(self, root, values=[], onchange=null):
        self.root = root
        self.var = tk.StringVar()
        self.box = ttk.Combobox(root, textvariable=self.var)
        self.values = values
        self.box["values"] = tuple(values)
        self.onchange = onchange

    def configCommand(self, command):
        self.box.bind("<<ComboboxSelected>>", command)

    def addValue(self, value):
        self.values.append(value)
        self.box["values"] = tuple(self.values)

class Listbox:
    def __init__(self, root, height, values, multipleselect=False):
        self.root = root
        self.var = tk.StringVar()
        self.box = tk.Listbox(root, height=height)
        self.values = values
        self.multipleselect = multipleselect
        self.box["listvariable"] = values
        self.setMode(multipleselect)

    def getValue(self):
        return self.box.curselection()

    def addValue(self, value):
        self.values.append(value)
        self.box["listvariable"] = self.values

    def delValue(self, value):
        if value in self.values:
            self.values.pop(value)
            self.box["listvariable"] = self.values
            return True
        else:
            return False
    
    def setMode(self, multipleselect=False):
        if multipleselect:
            self.box["selectmode"] = "extended"
        else:
            self.box["selectmode"] = "browse"

class Text:
    def __init__(self, root, text):
        self.label = tk.Label(root)
        self.label.text = text #Not sure if correct

    def setValue(self, text):
        """
        Changes text to parameters
        """
        self.label.text = text

    def getValue(self):
        return self.label.text

class Scale:
    def __init__(self, root, length, orient=tk.VERTICAL, start=None, end=None, command=null, variable=False):
        #Defaults start and end values if either are not defined
        self.root = root
        self.var = None
        if (not start) and (not end):
            start = 0
            end = start+length
        elif (not start) and end:
            start = end-length
        elif start and (not end):
            end = start+length
        self.scale = ttk.Scale(root, orient=orient, length=length, from_=start, to=end)
        if command is not null:
            self.configCommand(command)
        if variable:
            self.var = tk.StringVar()
            self.scale["variable"] = self.var

    def getValue(self):
        """
        Recieves any input from the user-input field and puts it in self.var as a string
        """
        self.value = self.scale.get()

    def setValue(self, value):
        """
        Sets scale value
        """
        self.scale.set(value)

    def configCommand(self, command):
        self.scale["command"] = command

    def configVariable(self, variable):
        self.scale["variable"] = variable

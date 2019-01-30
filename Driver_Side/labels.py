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

#Local Imports
import sockettables
from visglobals import ip

visiontable = sockettables.SocketTable()
visiontable.startSocketTables()

def null(self):
    pass

class Widget:
    def __init__(self, root):
        #Dummy variable inits to make class work: must be overridden
        self.value = tk.StringVar()
        self.widget = tk.Label(root)
        self.location = ()

    def getValue(self):
        """
        Returns input from the user-input field
        """
        return str(self.value.get())

    def setOnGrid(self, row, column, columnspan, rowspan):
        """
        Sets the widget on the user interface
        """
        self.widget.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self.location = (column, row, columnspan, rowspan)

    def getLocation(self):
        """
        Retrives the grid arguments send when the object was placed on the grid
        """
        return self.location

    def ungrid(self):
        self.widget.grid_forget()
        self.location = ()

class Camera(Widget):
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
        self.widget = tk.Label(root)
        #Makes a listener socket bound to this specific camera
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, camnum+5800))
        
    def updateImgOnLabel(self):
        """
        Places the latest image from the socket stream port aligning with the camnum
        """
        #Places an image from the networked camera on the label
        image = self.getImgFromNetwork()
        self.widget.config(image=image)
        self.widget.image = image
    
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
    
class LocalCamera(Widget):
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
            self.widget = tk.Label(root)
            self.location = ()
        else:
            testcam.release()
            self.active = False

    def updateCam(self):
        _, frame = self.cam.read()
        img = self.processImg(frame)
        self.widget.config(image=img)
        self.widget.img = img

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

class Entry(Widget):
    def __init__(self, root):
        self.root = root
        self.value = tk.StringVar()
        self.widget = tk.Entry(root, textvariable=self.value)
        self.location = ()

class Button(Widget):
    def __init__(self, root, text, command):
        self.root = root
        self.widget = tk.Button(root, text=text, command=command)
        self.location = ()
    
    def changeText(self, text):
        self.widget["text"] = text

class Checkbox(Widget):
    def __init__(self, root, text, command, onval=True, offval=False):
        self.root = root
        self.value = tk.StringVar()
        self.widget = tk.Checkbutton(root, text=text, command=command, onvalue=onval, offvalue=offval)
        self.location = ()

class RadioButton(Widget):
    def __init__(self, root, buttons):
        self.root = root
        #Buttons are a (displaytext, value) pair
        self.value = tk.StringVar()
        self.options = [tk.Radiobutton(root, text=text, variable=self.value, value=val) for text, val in buttons]
        self.location = {}

    def addOption(self, text, value):
        self.options.append(tk.Radiobutton(self.root, text=text, variable=self.value, value=value))

    def setOnGrid(self, option, row, column, columnspan, rowspan):
        self.options[option].grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self.location[option] = (column, row, columnspan, rowspan)

    def ungrid(self, option):
        #Ungrids a single option from the set of RadioButton
        self.options[option].grid_forget()
        self.location.pop(option)

class Combobox:
    def __init__(self, root, values=[], onchange=null):
        self.root = root
        self.value = tk.StringVar()
        self.widget = ttk.Combobox(root, textvariable=self.value)
        self.values = values
        self.widget["values"] = tuple(values)
        self.onchange = onchange
        self.location = ()

    def configCommand(self, command):
        self.widget.bind("<<ComboboxSelected>>", command)

    def addValue(self, value):
        self.values.append(value)
        self.widget["values"] = tuple(self.values)

class Listbox:
    def __init__(self, root, height, values, multipleselect=False):
        self.root = root
        self.value = tk.StringVar()
        self.widget = tk.Listbox(root, height=height)
        self.values = values
        self.multipleselect = multipleselect
        self.widget["listvariable"] = values
        self.setMode(multipleselect)
        self.location = ()

    def getValue(self):
        return self.widget.curselection()

    def addValue(self, value):
        self.values.append(value)
        self.widget["listvariable"] = self.values

    def delValue(self, value):
        if value in self.values:
            self.values.pop(value)
            self.widget["listvariable"] = self.values
            return True
        else:
            return False
    
    def setMode(self, multipleselect=False):
        if multipleselect:
            self.widget["selectmode"] = "extended"
        else:
            self.widget["selectmode"] = "browse"

class Text:
    def __init__(self, root, text):
        self.widget = tk.Label(root)
        self.widget.text = text #Not sure if correct
        self.location = ()

    def setValue(self, text):
        """
        Changes text to parameters
        """
        self.widget.text = text

    def getValue(self):
        return self.widget.text

class Scale:
    def __init__(self, root, length, orient=tk.VERTICAL, start=None, end=None, command=null, variable=False):
        #Defaults start and end values if either are not defined
        self.root = root
        self.value = None
        self.location = ()
        if (not start) and (not end):
            start = 0
            end = start+length
        elif (not start) and end:
            start = end-length
        elif start and (not end):
            end = start+length
        self.widget = ttk.Scale(root, orient=orient, length=length, from_=start, to=end)
        if command is not null:
            self.configCommand(command)
        if variable:
            self.value = tk.StringVar()
            self.widget["variable"] = self.value

    def getValue(self):
        """
        Returns any input from the user-input field
        """
        return self.widget.get()

    def setValue(self, value):
        """
        Sets scale value
        """
        self.widget.set(value)

    def configCommand(self, command):
        self.widget["command"] = command

    def configVariable(self, variable):
        self.widget["variable"] = variable

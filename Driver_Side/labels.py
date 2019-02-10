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
import fonts
from visglobals import ip, visiontable

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
        location = self.location
        self.location = ()
        return location

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
        self.updateOverNetwork()
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
        if not image:
            return
        self.widget.config(image=image)
        self.widget.image = image
    
    def updateOverNetwork(self):
        """
        Updates Networktable data about the camera
        """
        visiontable.putBoolean("{0}active".format(self.camnum), self.active)
        visiontable.putNumber("{0}width".format(self.camnum), self.width)
        visiontable.putNumber("{0}height".format(self.camnum), self.height)
        visiontable.putBoolean("{0}color".format(self.camnum), self.color)
        visiontable.putNumber("{0}framerate".format(self.camnum), self.framerate)
        #visiontable.putNumber("{0}quantization".format(self.camnum), self.quantization)
        visiontable.putNumber("{0}compression".format(self.camnum), self.compression)
        visiontable.putNumber("{0}quality".format(self.camnum), self.quality)
        
    def getImgFromNetwork(self):
        """
        Polls the latest image from the network socket which corresponds with the camera number
        """
        #TODO Make socket timeout if it takes too long
        img = self.recvWithTimeout()
        if img == b"":
            return False
        img = self.processIncomingImg(img)
        return img
    
    def recvWithTimeout(self):
        try:
            message = self.sock.recv(self.maxsize)
        except socket.error:
            message = b""
        return message

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
        pass

    @property
    def timeout(self):
        self.sock.settimeout(self.timeout)
        return self.timeout

    @timeout.setter
    def timeout(self, timeout):
        if timeout < 0:
            timeout = None
        self.sock.settimeout(timeout)
        self.__timeout = timeout


class FailedCamera(Widget):
    #Camera fallback if a number cannot connect
    def __init__(self, camnum, root, window, interface, ind):
        #Camnum will match up with camnum on robot network
        self.root = root
        self.camnum = camnum
        message = "Camera at network index {} is currently unavalible.".format(camnum)
        self.widget = tk.Label(root, text=message, font=fonts.Textbox)
        self.window = window
        self.interface = interface
        self.ind = ind

        #Original Camera class variables except socket
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
        
    def updateImgOnLabel(self):
        """
        Placeholder for this method on Camera
        """
        self.tryToConnect() #Tries to connect to proper camera
    
    def updateOverNetwork(self):
        """
        Updates Networktable data about the camera
        """
        visiontable.putBoolean("{0}active".format(self.camnum), self.active)
        visiontable.putNumber("{0}width".format(self.camnum), self.width)
        visiontable.putNumber("{0}height".format(self.camnum), self.height)
        visiontable.putBoolean("{0}color".format(self.camnum), self.color)
        visiontable.putNumber("{0}framerate".format(self.camnum), self.framerate)
        #visiontable.putNumber("{0}quantization".format(self.camnum), self.quantization)
        visiontable.putNumber("{0}compression".format(self.camnum), self.compression)
        visiontable.putNumber("{0}quality".format(self.camnum), self.quality)

    def tryToConnect(self):
        """
        Tests whether the camera being replaced has become avalible and puts it in place if it has
        """
        if visiontable.getBoolean("{}isactive".format(self.camnum)):
            camera = Camera(self.camnum, self.root)
            self.window.cameras[self.interface].remove(self.widget)
            self.window.cameras[self.interface].insert(self.ind, camera)
            self.window.replaceWidget(self.widget, camera)
            self.widget.destroy()


    def shutdown(self):
        pass
    
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
    def __init__(self, root, font=fonts.Textbox):
        self.root = root
        self.value = tk.StringVar()
        self.widget = tk.Entry(root, textvariable=self.value, font=font)
        self.location = ()

class Button(Widget):
    def __init__(self, root, text, command, font=fonts.Button):
        self.root = root
        self.text = tk.StringVar()
        self.widget = tk.Button(root, textvariable=self.text, command=command, font=font)
        self.text.set(text)
        self.location = ()
    
    def setText(self, text):
        self.text.set(text)

    def getValue(self):
        return self.text.get()

class Checkbox(Widget):
    def __init__(self, root, text, command, onval=True, offval=False, font=fonts.Button):
        self.root = root
        self.value = tk.StringVar()
        self.widget = tk.Checkbutton(root, text=text, command=command, onvalue=onval, offvalue=offval, font=font)
        self.location = ()

class RadioButtonParent(Widget):
    def __init__(self, root, buttons, font=fonts.Button, vartype = tk.IntVar):
        self.root = root
        self.font = font
        self.value = vartype()
        #Buttons are a (displaytext, value) pair
        #They must all be of the same type
        self.buttons = [RadioButton(root, text=text, variable=self.value, onvalue=val, font=self.font) for text, val in buttons]
        self.location = ()

    def addButton(self, text, value):
        self.buttons.append(RadioButton(self.root, text=text, variable=self.value, onvalue=value, font=self.font))

    def setOnGrid(self, option, row, column, columnspan, rowspan, perbutton=1):
        rowmode = True
        if perbutton < 1:
            raise ValueError("Rowspan cannot be less than one")
        if rowspan >= len(self.buttons)*perbutton:
            pass
        elif columnspan >= len(self.buttons)*perbutton:
            rowmode = False
        else:
            if perbutton > 1:
                perbuttonmessage = " with each button taking {} rows/columns"
            else:
                perbuttonmessage = ""
            raise ValueError("Rowspan of {} and columnspan of {} are too small to support {} buttons{}.".format(rowspan, columnspan, len(self.buttons), perbuttonmessage))
        if rowmode:
            row = row
            for button in self.buttons:
                button.setOnGrid(row, column, columnspan=columnspan, rowspan=perbutton)
            row += perbutton
        else:
            column = column
            for button in self.buttons:
                button.setOnGrid(row, column, columnspan=perbutton, rowspan=rowspan)
            column += perbutton
        print("Unimplemented feature: Set parent radio button on grid")

    def ungrid(self):
        #Ungrids a single option from the set of RadioButton
        for button in self.buttons:
            button.ungrid()
        print("Unimplemented")

class RadioButton(Widget):
    def __init__(self, root, text, variable=tk.BooleanVar, onvalue=True, font=fonts.Button):
        self.root = root
        #Buttons are a (displaytext, value) pair
        self.text = tk.StringVar()
        if variable == type:
            self.value = variable()
        else:
            self.value = variable
        self.widget = tk.Radiobutton(root, text=self.text, textvariable=self.value, onvalue=onvalue, font=font)
        self.location = ()

    def changeText(self, text):
        self.text.set(text)

class Combobox:
    def __init__(self, root, values=[], onchange=null, font=fonts.Button):
        self.root = root
        self.value = tk.StringVar()
        self.widget = ttk.Combobox(root, textvariable=self.value, font=font)
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
    def __init__(self, root, height, values, multipleselect=False, font=fonts.Button):
        self.root = root
        self.value = tk.StringVar()
        self.widget = tk.Listbox(root, height=height, font=font)
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

class Text(Widget):
    def __init__(self, root, text, font=fonts.Textbox):
        self.text = tk.StringVar()
        self.widget = tk.Label(root, textvariable=self.text, font=font)
        self.text.set(text)
        self.location = ()

    def setValue(self, text):
        """
        Changes text to parameters
        """
        self.text.set(text)

    def getValue(self):
        return self.text.get()

class Scale(Widget):
    def __init__(self, root, length, orient=tk.VERTICAL, start=None, end=None, command=null, variable=False, font=fonts.Button):
        #Defaults start and end values if either are not defined
        self.root = root
        self.value = tk.DoubleVar()
        self.location = ()
        if (not start or not end) and (not length):
            raise ValueError("No length value passed and start and end not explicitly defined")
        elif (not start) and (not end):
            start = 0
            end = start+length
        elif (not start) and end:
            start = end-length
        elif start and (not end):
            end = start+length
        self.widget = ttk.Scale(root, var=self.value, orient=orient, length=length, from_=start, to=end, font=fonts.Button)
        if command is not null:
            self.configCommand(command)
        if variable:
            self.value = tk.StringVar()
            self.widget["variable"] = self.value

    def setValue(self, value):
        """
        Sets scale value
        """
        self.value.set(value)

    def configCommand(self, command):
        self.widget["command"] = command

    def configVariable(self, variable):
        self.widget["variable"] = variable

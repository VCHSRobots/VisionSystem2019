#tkwin.py: A class to manage tkinter's interaction with FRC networktables
#1/8/2019 HP

#Module Imports
import threading
import networktables
import re #Used for string processing
import functools as fts
import tkinter as tk
from networktables import NetworkTables as nt

#Local Imports
import labels
from globals import visiontable, myadr, piadr, widgettypes

#Globals
#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")
NOARG = "*None*"
GLOBAL = "*Global*"

class TkWin:
    def __init__(self, name, width = 100, height = 100, menustructure = {}):
        #TODO width and height are magic numbers
        self.name = name
        #Sets up the window root
        self.root = tk.Tk()
        self.root.title = name #Sets the title of the window as the user sees it
        self.root.geometry("{0}x{1}".format(width, height))
        #Lists of different types of widgets
        self.cameras = {}
        self.localcameras = {}
        self.buttons = {}
        self.textboxes = {}
        self.entries = {}
        self.checkboxes = {}
        self.radiobuttons = {}
        self.comboboxes = {}
        self.listboxes = {}
        self.scales = {}
        self.vars = {}
        self.globalwidgets = {}
        #Objects currently on the grid
        self.gridded = []
        #Whether the window itself is active
        self.active = True
        #List of all filled points on the window's grid
        self.filled = []
        self.threadloop = null
        #Inits Menu system
        #Menus are structured as {Menu: Command, PulldownMenu: {MenuLabel1: Command1, MenuLabel2, Command2}}
        self.menus = menustructure
        self.initMenuSystem()

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

    def initMenuSystem(self):
        self.root.option_add("*tearOff", False) #Not sure how to implement this
        self.toplevel = tk.Menu(self.root)
        processMenuHierarchy(self.toplevel, self.menus, self)
        self.root.config(menu=self.toplevel)

    def addCam(self, camnum, interface="mainmenu"):
        """
        Tries to add a remote camera to the window; returns False if it fails
        """
        if interface not in self.cameras:
            self.cameras[interface] = []
        if visiontable.getBoolean("{0}isactive".format(camnum), False):
            self.cameras[interface].append(labels.Camera(camnum, self.root))
            return True
        return False
        
    def setCamColor(self, camind, color):
        """
        Sets the color of the camera's socket output
        """
        self.localcameras[camind].color = color
    
    def addLocalCam(self, camnum, interface="mainmenu"):
        """
        Local variant of addCam
        """
        if interface not in self.localcameras:
            self.localcameras[interface] = []
        camera = labels.LocalCamera(camnum, self.root)
        if camera.active:
            self.localcameras[interface].append(camera)
            return True
        else:
            return False
        
    def setLocalCamColor(self, camind, color):
        """
        Local variant of setCamColor
        """
        self.cameras[camind].color = color

    #Widget functions
    #Class sends self variable to all commands executed by default: this can be disabled by setting the sendself argument to False
    def addEntry(self, interface="mainmenu"):
        """
        Adds a button to the given interface
        """
        if interface not in self.entries:
            self.entries[interface] = []
        entry = labels.Entry(self.root)
        self.entries[interface].append(entry)

    
    def addButton(self, text, command, partialarg = "*self*", interface="mainmenu"):
        """
        Adds a button to the given interface
        """
        if interface not in self.buttons:
            self.buttons[interface] = []
        if partialarg == "*self*":
            partialarg = self
        if partialarg != NOARG:
            command = fts.partial(command, partialarg)
        self.buttons[interface].append(labels.Button(self.root, text=text, command=command))

    def addCheckbox(self, text, onval=True, offval=False, interface="mainmenu"):
        """
        Adds a user entry field to the given interface
        """
        if interface not in self.checkboxes:
            self.checkboxes[interface] = []
        self.checkboxes[interface].append(labels.Checkbox(self.root, text, onval, offval))
    
    def addRadioButton(self, buttons, interface="mainmenu"):
        """
        Adds a user entry field to the given interface
        """
        if interface not in self.radiobuttons:
            self.radiobuttons[interface] = []
        self.radiobuttons[interface].append(labels.RadioButton(self.root, buttons))

    def addCombobox(self, values=[], onchange=labels.null, partialarg = "*self*", interface="mainmenu"):
        """
        Adds a user entry field to the given interface
        """
        if interface not in self.comboboxes:
            self.comboboxes[interface] = []
        if partialarg == "*self*":
            partialarg = self
        if partialarg != NOARG:
            command = fts.partial(command, partialarg)
        self.comboboxes[interface].append(labels.Combobox(self.root, values=values, onchange=command))

    def addListbox(self, height, values, multipleselect=False, interface="mainmenu"):
        """
        Adds a user entry field to the given interface
        """
        if interface not in self.listboxes:
            self.listboxes[interface] = []
        self.listboxes[interface].append(labels.Listbox(self.root, height, values, multipleselect=multipleselect))
    
    def addText(self, text, interface="mainmenu"):
        """
        Adds a user entry field to the given interface
        """
        if interface not in self.textboxes:
            self.textboxes[interface] = []
        self.textboxes[interface].append(labels.Text(self.root, text))
    
    def addScale(self, length, orient=tk.VERTICAL, start=None, end=None, command=labels.null, variable=False, partialarg = "*self*", interface="mainmenu"):
        """
        Adds a user entry field to the given interface
        """
        if interface not in self.scales:
            self.scales[interface] = []
        if partialarg == "*self*":
            partialarg = self
        if partialarg != NOARG:
            command = fts.partial(command, partialarg)
        self.scales[interface].append(labels.Scale(self.root, length, orient=orient, start=start, end=end, command=command, variable=variable))
    
    def addWidget(self, widgetname):
        
    def addGlobalWidget(self, widget, widgettype):
        """
        Adds a widget which isn't associated with any specific interface
        """
        if isValidWidget(widgettype):
            if not widgettype in self.globalwidgets:
                self.globalwidgets[widgettype] = []
            self.globalwidgets[widgettype]
        else:
            raise ValueError("Invalid Widget Type: {0}".format(widgettype))

    def gridWidget(self, widget, column, row, columnspan, rowspan, option=None):
        """
        Grids a widget and tracks it in self.gridded
        """
        if option:
            widget.setOnGrid(option = option, column=column, row=row, columnspan=columnspan, rowspan=rowspan)
            self.gridded.append((widget, option))
        else:
            widget.setOnGrid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
            self.gridded.append((widget,))

    def ungridWidget(self, widget, option=None):
        """
        Ungrids a widget and returns its location
        """
        location = ()
        if option:
            location = widget.location[option]
            widget.ungrid(option)
        else:
            location = widget.location
            widget.ungrid()
        return location
        
    def replaceWidget(self, replaced, replacer, option=None):
        """
        Ungrids the replaced widget and puts replacer in its place
        """
        location = self.ungridWidget(replaced)
        self.gridWidget(replacer, location[0], location[1], location[2], location[3], option=option)

    #Random Window Variable Functions

    def processGuiMap(self, guimap, guiname):
        """
        Places items on grid based on a dimensioned array with integers standing for different components
        EX:
        [[[0, 0, 1, 1, 1]
        [0, 0, 1, 1, 1]
        [0, 0, 1, 1, 1]],
        {1: "camera1", 2: "radio0_1}]
        would place the first camera the window recognizes on column 2 row 1 with a columnspan of 3 and rowspan of 3
        """
        widgetspans = findWidgetSpans(guimap)
        for num in guimap[1]:
            #Wait to cast num to integer since it needs to match with the dictionary key to access the widget name
            widget, option = self.getWidget(guimap[1][num], guiname)
            num = int(num)
            column = widgetspans[num][0]
            row = widgetspans[num][2]
            columnspan = widgetspans[num][1]-widgetspans[num][0]+1
            rowspan = widgetspans[num][3]-widgetspans[num][2]+1
            print(column, row, columnspan, rowspan)
            if option:
                #Certain widgets, like radios, are gridded differently than other widgets: The first number specifies which set of buttons you refer to, and the second one refers to the button itself
                self.gridWidget(widget, column = widgetspans[num][0], row = widgetspans[num][2], columnspan = widgetspans[num][1]-widgetspans[num][0]+1, rowspan = widgetspans[num][3]-widgetspans[num][2]+1, option=option)
            else:
                self.gridWidget(widget, column=column, row=row, columnspan=columnspan, rowspan=rowspan)

    def getWidget(self, codename, guiname):
        """
        Retrieves a widget based on its gui reference name and parent interface
        """
        #Seperates widget's end tag from its type indicator
        widgettag = re.sub(r"[a-zA-Z]", "", codename)
        widgettype = re.sub(r"[0-9_]", "", codename)
        #Detects if the tag has an optional suffix
        if "_" in widgettag:
            num = ""
            option = ""
            ind = widgettag.index("_")
            num = int(widgettag[:ind])
            option = int(widgettag[ind+1:])
        else:
            num = int(widgettag)
            option = None
        #Finds widget based on its type
        if widgettype.lower() == "camera":
            widget = self.cameras[guiname][num]
        elif widgettype.lower() == "button":
            widget = self.buttons[guiname][num]
        elif widgettype.lower() == "entry":
            widget = self.entries[guiname][num]
        elif widgettype.lower() == "textbox":
            widget = self.textboxes[guiname][num]
        elif widgettype.lower() == "checkbox":
            widget = self.checkboxes[guiname][num]
        elif widgettype.lower() == "radio":
            widget = self.radiobuttons[guiname][num]
        return widget, option

    def killLoop(self):
        self.active = False
        
    def pollForCams(self, camrange):
        """
        Checks for active cams on the network
        """
        for num in range(camrange):
            self.addCam(num)

    def tearDown(self):
        """
        Clears the window of all the widgets grided by lastgui
        """
        for widget in self.gridded:
            if len(widget) > 1:
                widget[0].ungrid(widget[1])
            else:
                widget[0].ungrid()
        self.gridded.clear()

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

def isValidWidget(widgettype):
    if widgettype in widgettypes:
        return True
    else:
        raise ValueError("Invalid Widget Type: {0}".format(widgettype))

def findWidgetSpans(guimap):
    """
    Detects griding paramiters from a gui file list
    """
    widgetspans = {} #{num: (firstcolumn, lastcolumn, firstrow, lastrow)}
    firstcolumn, lastcolumn, firstrow, lastrow = None, None, None, None
    numencountered = False
    for num in guimap[1]:
        num = int(num)
        for ind, row in enumerate(guimap[0]):
            if num in row:
                if not numencountered:
                    #Some numbers have 1 added to them because there may be problems with index 0
                    firstrow = ind
                    firstcolumn = row.index(num)
                    lastcolumn = len(row)-row[::-1].index(num)-1
                    numencountered = True
                elif numencountered:
                    lastrow = ind
                    break
            if (ind == len(guimap[0])-1) and (not lastrow):
                #If on the last row of the map without encountering the number again
                lastrow = firstrow
        widgetspans[num] = (firstcolumn, lastcolumn, firstrow, lastrow)
        numencountered = False
        firstcolumn, lastcolumn, firstrow, lastrow = None, None, None, None
    return widgetspans

def processMenuHierarchy(toplevel, hierarchy, self):
    """
    Adds the lower level menus specified by hierarchy to the given toplevel menu
    """
    for itemname in hierarchy:
        item = hierarchy[itemname]
        if type(item) == dict:
            #if this item is a menu which contains commands
            menubar = tk.Menu(toplevel, tearoff=0)
            processMenuHierarchy(toplevel=menubar, hierarchy=item, self=self)
            toplevel.add_cascade(label=itemname, menu=menubar)
        elif not item:
            #if the item is a blank object, which indicates a seperator
            toplevel.add_separator()
        elif type(item) == type(null):
            #if the item only holds a single command
            #Checks for options on item
            if "_" in itemname:
                ind = itemname.index("_")
                option = itemname[ind+1:]
                itemname = itemname[:ind]
                if option == "*self*":
                    toplevel.add_command(label=itemname, command=fts.partial(item, self))
            else:
                toplevel.add_command(label=itemname, command=item)

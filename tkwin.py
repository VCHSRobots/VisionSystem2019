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

#Globals
#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
nt.initialize("roborio-4415-frc.local")
visiontable = nt.getTable("/vision")
NOARG = "*None*"

class TkWin:
    def __init__(self, name, width = 100, height = 100, menustructure = {}):
        #TODO width and height are magic numbers
        self.name = name
        #Sets up the window root
        self.root = tk.Tk()
        self.root.title = name #Sets the title of the window as the user sees it
        self.root.geometry("{0}x{1}".format(width, height))
        #Lists of different types of widgets
        self.cameras = []
        self.localcameras = []
        self.buttons = []
        self.textboxes = []
        self.entries = []
        self.checkboxes = []
        self.radiobuttons = []
        self.comboboxes = []
        self.listboxes = []
        self.scales = []
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

    #Class sends self variable to all commands executed by default: this can be disabled by setting the sendself argument to False
    def addEntry(self):
        """
        Adds a button to the class registry
        """
        entry = labels.Entry(self.root)
        self.entries.append(entry)

    
    def addButton(self, text, command, partialarg = "*self*"):
        """
        Adds a button to the class registry
        """
        if partialarg == "*self*":
            partialarg = self
        if partialarg != NOARG:
            command = fts.partial(command, partialarg)
        self.buttons.append(labels.Button(self.root, text=text, command=command))

    def addCheckbox(self, text, onval=True, offval=False):
        """
        Adds a user entry field to the class registry
        """
        self.checkboxes.append(labels.Checkbox(self.root, text, onval, offval))
    
    def addRadioButton(self, buttons):
        """
        Adds a user entry field to the class registry
        """
        self.radiobuttons.append(labels.RadioButton(self.root, buttons))

    def addCombobox(self, values=[], onchange=labels.null, partialarg = "*self*"):
        """
        Adds a user entry field to the class registry
        """
        if partialarg == "*self*":
            partialarg = self
        if partialarg != NOARG:
            command = fts.partial(command, partialarg)
        self.comboboxes.append(labels.Combobox(self.root, values=values, onchange=command))

    def addListbox(self, height, values, multipleselect=False):
        """
        Adds a user entry field to the class registry
        """
        self.listboxes.append(labels.Listbox(self.root, height, values, multipleselect=multipleselect))
    
    def addText(self, text):
        """
        Adds a user entry field to the class registry
        """
        self.textboxes.append(labels.Text(self.root, text))
    
    def addScale(self, length, orient=tk.VERTICAL, start=None, end=None, command=labels.null, variable=False, partialarg = "*self*"):
        """
        Adds a user entry field to the class registry
        """
        if partialarg == "*self*":
            partialarg = self
        if partialarg != NOARG:
            command = fts.partial(command, partialarg)
        self.scales.append(labels.Scale(self.root, length, orient=orient, start=start, end=end, command=command, variable=variable))
    
    def processGuiMap(self, guimap):
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
            widget, option = self.getWidget(guimap[1][num])
            num = int(num)
            if option:
                #Certain widgets, like radios, are gridded differently than other widgets: The first number specifies which set of buttons you refer to, and the second one refers to the button itself
                widget.setOnGrid(option = option, column = widgetspans[num][0], row = widgetspans[num][2], columnspan = widgetspans[num][1]-widgetspans[num][0]+1, rowspan = widgetspans[num][3]-widgetspans[num][2]+1)
            else:
                print("here")
                print(widgetspans)
                column = widgetspans[num][0]
                row = widgetspans[num][2]
                columnspan = widgetspans[num][1]-widgetspans[num][0]+1
                rowspan = widgetspans[num][3]-widgetspans[num][2]+1
                print(column, row, columnspan, rowspan)
                widget.setOnGrid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

    def getWidget(self, codename):
        """
        Retrieves a widget based on its gui reference name
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
            widget = self.cameras[num]
        elif widgettype.lower() == "button":
            widget = self.buttons[num]
        elif widgettype.lower() == "entry":
            widget = self.entries[num]
        elif widgettype.lower() == "textbox":
            widget = self.textboxes[num]
        elif widgettype.lower() == "checkbox":
            widget = self.checkboxes[num]
        elif widgettype.lower() == "radio":
            widget = self.radiobuttons[num]
        return widget, option

    def killLoop(self):
        self.active = False
        
    def pollForCams(self, camrange):
        """
        Checks for active cams on the network
        """
        for num in range(camrange):
            self.addCam(num)

    def tearDown(self, lastgui):
        """
        Clears the window of all the widgets grided by lastgui
        """
        for key in lastgui[1]:
            widgetname = lastgui[1][key]
            widget, option = self.getWidget(widgetname)
            if option:
                widget.ungrid(option)
            else:
                widget.ungrid()

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
                    lastrow = ind+1
                    break
                print("here", len(guimap[0]), ind)
            if ind == len(guimap[0])-1 and not lastrow:
                #If on the last row of the map without encountering the number again
                lastrow = firstrow
        widgetspans[num] = (firstcolumn, lastcolumn, firstrow, lastrow)
        numencountered = False
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

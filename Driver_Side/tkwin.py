#tkwin.py: A class to manage tkinter's interaction with FRC networktables
#1/8/2019 HP

#Module Imports
import threading
import networktables
import json
import re #Used for string processing
import functools as fts
import tkinter as tk

#Local Imports
import labels
import configuration as config
from visglobals import myadr, piadr, widgettypes, visiontable, guimaps, stackmaps, null

#Globals
#Ip is configured to Holiday's laptop... change if neccecary!
ip = "10.44.15.41"
NOARG = "*None*"
GLOBAL = "*Global*"
SELF = "*Self*"

class TkWin:
  def __init__(self, name, width = 100, height = 100, menustructure = {}):
    #TODO width and height are magic numbers
    self.name = name
    #Sets up the window root
    self.root = tk.Tk()
    self.root.title = name #Sets the title of the window as the user sees it
    self.root.geometry("{0}x{1}".format(width, height))
    #Using single widget lists is depreciated - use the widgets dictionary instead
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
    #Objects currently on the grid
    self.gridded = []
    #Cache of widgets to grid in columns according to keys
    self.stacks = {}
    #Whether the window itself is active
    self.active = True
    #List of all filled points on the window's grid
    self.filled = []
    self.threadloop = null
    #Inits Menu system
    #Menus are structured as {Menu: Command, PulldownMenu: {MenuLabel1: Command1, MenuLabel2, Command2}}
    self.menus = menustructure
    self.initMenuSystem()
    self.interface = "mainmenu"

  def runWin(self):
    """
    Initiates the tkinter window while running the instance's set thread function
    """
    self.thread.run(self)
    self.root.mainloop()

  def setThread(self, func):
    """
    Sets the function to be run when self.runWin is called
    """
    self.thread = func

  def initMenuSystem(self):
    self.root.option_add("*tearOff", False) #Not sure how to implement this
    self.toplevel = tk.Menu(self.root)
    processMenuHierarchy(self.toplevel, self.menus, self)
    self.root.config(menu=self.toplevel)

  def addCamera(self, camnum, interface="mainmenu", rewidget=False):
    """
    Tries to add a remote camera to the window; returns False if it fails
    """
    if interface not in self.cameras:
      self.cameras[interface] = []
    if visiontable.getBoolean("{}isactive".format(camnum), False):
      camera = labels.Camera(camnum, self.root)
    else:
      ind = len(self.cameras[interface]) #The index the placeholder camera will go in for
      camera = labels.FailedCamera(camnum, self.root, self, interface, ind)
    self.cameras[interface].append(camera)
    print(self.cameras)
    if rewidget:
      return camera

  def setCamColor(self, camind, color):
    """
    Sets the color of the camera's socket output
    """
    self.localcameras[camind].color = color

  #Depreciated
  def addLocalCam(self, camnum, interface="mainmenu", rewidget=False):
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
  def addEntry(self, interface="mainmenu", font=None, rewidget=False):
    """
    Adds a button to the given interface
    """
    if interface not in self.entries:
      self.entries[interface] = []
    if font:
      entry = labels.Entry(self.root, font=font)
    else:
      entry = labels.Entry(self.root)
    self.entries[interface].append(entry)
    if rewidget:
      return entry


  def addButton(self, text, command = null, partialarg = SELF, interface="mainmenu", font=None, convertpartialarg = True, rewidget=False):
    """
    Adds a button to the given interface
    """
    if interface not in self.buttons:
      self.buttons[interface] = []
    command = makePartial(command, partialarg, self)
    if font:
      button = labels.Button(self.root, text=text, command=command, font=font)
    else:
      button = labels.Button(self.root, text=text, command=command)
    self.buttons[interface].append(button)
    if rewidget:
      return button

  def addCheckbox(self, text, onval=True, offval=False, interface="mainmenu", font=None, rewidget=False):
    """
    Adds a user entry field to the given interface
    """
    if interface not in self.checkboxes:
      self.checkboxes[interface] = []
    if font:
      checkbox = labels.Checkbox(self.root, text, onval, offval, font=font)
    else:
      checkbox = labels.Checkbox(self.root, text, onval, offval)
    self.checkboxes[interface].append(checkbox)
    if rewidget:
      return checkbox

  def addRadioButton(self, buttons, interface="mainmenu", font=None, rewidget = False):
    """
    Adds a user entry field to the given interface
    """
    if interface not in self.radiobuttons:
      self.radiobuttons[interface] = []
    if font:
      radio = labels.RadioButton(self.root, buttons, font=font)
    else:
      radio = labels.RadioButton(self.root, buttons)
    self.radiobuttons[interface].append(radio)
    if rewidget:
      return radio

  def addCombobox(self, values=[], onchange=labels.null, partialarg = "*self*", interface="mainmenu", font=None, convertpartialarg=True, rewidget=False):
    """
    Adds a user entry field to the given interface
    """
    if interface not in self.comboboxes:
      self.comboboxes[interface] = []
    command = makePartial(onchange, partialarg, self, convertpartialarg=convertpartialarg)
    if font:
      combobox = labels.Combobox(self.root, values=values, onchange=command, font=font)
      self.comboboxes[interface].append()
    else:
      combobox = labels.Combobox(self.root, values=values, onchange=command)
    self.comboboxes[interface].append(combobox)
    if rewidget:
      return combobox

  def addListbox(self, height, values, multipleselect=False, interface="mainmenu", font=None, rewidget=False):
    """
    Adds a user entry field to the given interface
    """
    if interface not in self.listboxes:
      self.listboxes[interface] = []
    if font:
      listbox = labels.Listbox(self.root, height, values, multipleselect=multipleselect, font=font)
    else:
      listbox = labels.Listbox(self.root, height, values, multipleselect=multipleselect)
    self.listboxes[interface].append(listbox)
    if rewidget:
      return listbox

  def addText(self, text, interface="mainmenu", font=None, rewidget=False):
    """
    Adds a user entry field to the given interface
    """
    if interface not in self.textboxes:
      self.textboxes[interface] = []
    if font:
      textbox = labels.Text(self.root, text, font=font)
    else:
      textbox = labels.Text(self.root, text)
    self.textboxes[interface].append(textbox)
    if rewidget:
      return textbox

  def addScale(self, length=None, orient=tk.VERTICAL, start=None, end=None, command=labels.null, variable=False, partialarg = "*self*", interface="mainmenu", font=None, convertpartialarg=True, rewidget=False):
    """
    Adds a user entry field to the given interface
    """
    if interface not in self.scales:
      self.scales[interface] = []
    command = makePartial(command, partialarg, self, convertpartialarg)
    if font:
      scale = labels.Scale(self.root, length=length, orient=orient, start=start, end=end, command=command, variable=variable, font=font)
    else:
      scale = labels.Scale(self.root, length=length, orient=orient, start=start, end=end, command=command, variable=variable)
    self.scales[interface].append(scale)
    if rewidget:
      return scale

  def gridWidget(self, widget, column, row, columnspan, rowspan):
    """
    Grids a widget and tracks it in self.gridded
    """
    widget.setOnGrid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
    self.gridded.append(widget)

  def ungridWidget(self, widget):
    """
    Ungrids a widget and returns its location
    """
    location = widget.location
    widget.ungrid()
    return location

  def replaceWidget(self, replaced, replacer, option = None):
    """
    Ungrids the replaced widget and puts replacer in its place
    """
    location = self.ungridWidget(replaced)
    self.gridWidget(replacer, location[0], location[1], location[2], location[3])

  #Random Window Variable Functions
  def addVariable(self, name, value, interface = GLOBAL):
    self.vars[interface][name] = value

  def getVariable(self, name, interface = GLOBAL):
    return self.vars[interface][name]

  def processGuiStack(self, guiname):
    """
    Stack items in self.stackmap on top of each other according to their rows
    """
    stackmap = stackmaps[guiname]
    row = 0
    for key in self.stacks:
      gridparams = stackmap[key]
      column, columnspan = gridparams[0], gridparams[1]-gridparams[0]+1
      rowspan = gridparams[2]
      for widget in self.stacks[key]:
        self.gridWidget(widget, column, row, columnspan, rowspan)
        row += rowspan
      row = 0

  def processGuiMap(self, guiname):
    """
    Places items on grid based on a dimensioned array with integers standing for different components
    EX:
    [[[0, 0, 1, 1, 1]
    [0, 0, 1, 1, 1]
    [0, 0, 1, 1, 1]],
    {1: "camera1", 2: "radio0_1}]
    would place the first camera the window recognizes on column 2 row 1 with a columnspan of 3 and rowspan of 3
    """
    print(self.cameras)
    print(guiname)
    guimap = guimaps[guiname]
    widgetspans = findWidgetSpans(guimap)
    for num in guimap[1]:
      #Wait to cast num to integer since it needs to match with the dictionary key to access the widget name
      widget = self.getWidgetFromName(guimap[1][num], guiname)
      num = int(num)
      column = widgetspans[num][0]
      row = widgetspans[num][2]
      columnspan = widgetspans[num][1]-widgetspans[num][0]+1
      rowspan = widgetspans[num][3]-widgetspans[num][2]+1
      print(column, row, columnspan, rowspan)
      self.gridWidget(widget, column=column, row=row, columnspan=columnspan, rowspan=rowspan)
  
  def getWidgetFromName(self, widgetname, guiname):
    """
    Retrieves a widget based on its gui reference name and parent interface
    """
    widgettype, num = splitWidgetName(widgetname)
    #Finds widget based on its type
    if isValidWidget(widgettype):
      if widgettype == "listbox":
        widget = self.listboxes[guiname][num]
      if widgettype == "camera":
        widget = self.cameras[guiname][num]
      elif widgettype == "localcamera":
        widget = self.localcameras[guiname][num]
      elif widgettype == "button":
        widget = self.buttons[guiname][num]
      elif widgettype == "entry":
        widget = self.entries[guiname][num]
      elif widgettype == "checkbox":
        widget = self.checkboxes[guiname][num]
      elif widgettype == "radiobutton":
        widget = self.radiobuttons[guiname][num]
      elif widgettype == "combobox":
        widget = self.comboboxes[guiname][num]
      elif widgettype == "text":
        widget = self.textboxes[guiname][num]
      elif widgettype == "scale":
        widget = self.scales[guiname][num]
    return widget

  def killLoop(self):
    self.active = False

  def pollForCams(self, camrange):
    """
    Checks for active cams on the network
    """
    for num in range(camrange):
      self.addCamera(num)

  def switchUi(self, guiname, gridstyle="guimap"):
    """
    Configures the window for the given the guifile to be setup and any stray widgets to clear
    """
    self.tearDown()
    #Configures window for the new gui
    if not config.configwascalled[guiname]:
        config.configfunctions[guiname](self)
    #Grids gui widgets
    print(guiname)
    hasguimap = guiname in guimaps
    hasstack = guiname in stackmaps
    #If a single gridding style is specified
    if gridstyle == "guimap":
      self.processGuiMap(guiname)
    elif gridstyle == "stack":
      self.processGuiStack(guiname)
    else:
      #Tries to grid interface based on what is avalible
      #Will grid with both stack and map if possible
      if hasguimap:
        self.processGuiMap(guiname)
      if hasstack:
        self.processGuiStack(guiname)
      if not hasguimap and not hasstack:
        raise FileNotFoundError("No stack file or gui file found for interface {}. Have you added the file name to visglobals.py?".format(guiname))
    self.interface = guiname

  def setWindowVars(self, setup):
    interface = setup.pop("interface")
    self.vars[interface] = setup

  def tearDown(self):
    """
    Clears the window of all the widgets grided by lastgui
    """
    print(self.gridded)
    for widget in self.gridded:
        widget.ungrid()
    self.gridded.clear()

  def emergencyShutdown(self):
    """
    Safely shuts down system in case of error
    """
    for cam in self.cameras:
      cam.shutdown()
    for cam in self.localcameras:
      cam.shutdown()
  
def splitWidgetName(widgetname):
  print(widgetname)
  #Seperates widget's end tag from its type indicator
  num = int(re.sub(r"[a-zA-Z]", "", widgetname))
  widgettype = re.sub(r"[0-9]", "", widgetname)
  return widgettype, num
  
def isValidWidget(widgettype):
  print(widgettypes)
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
  rowswithnum = []
  for num in guimap[1]:
    num = int(num)
    for ind, row in enumerate(guimap[0]):
      if num in row:
        rowswithnum.append(ind)
        firstcolumn = row.index(num)
        lastcolumn = len(row)-row[::-1].index(num)-1
    firstrow, lastrow = min(rowswithnum), max(rowswithnum)
    widgetspans[num] = (firstcolumn, lastcolumn, firstrow, lastrow)
    firstcolumn, lastcolumn, firstrow, lastrow = None, None, None, None
    rowswithnum = []
  return widgetspans
    
def makePartial(func, partial, self=None, convertpartialarg = False):
  partial = processPartialArg(partial, self=self)
  partialfunc = fts.partial(func, partial)
  return partialfunc
  
def processPartialArg(partial, self=None, convertfromnum = False):
  if partial == SELF:
    if self:
      arg = self
    else:
      raise ValueError("Invalid argument for \"self\": {0}".format(self))
  else:
    if convertfromnum:
      if type(partial) == str:
        if re.match("[0-9].[0-9]", partial) or partial.isdigit():
          arg = float(partial)
    else:
      arg = partial
  return arg

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

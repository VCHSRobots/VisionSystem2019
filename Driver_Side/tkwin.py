#tkwin.py: A class to manage tkinter's interaction with FRC networktables
#1/8/2019 HP

#Module Imports
import threading
import networktables
import json
import timer
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
    self.timer = timer.Timer()
    self.camerasconfiged = False

  def runWin(self):
    """
    Initiates the tkinter window while running the instance's set thread function
    """
    self.thread.start()
    self.root.mainloop()

  def setThread(self, func):
    """
    Sets the function to be run when self.runWin is called
    """
    self.thread = func

  def initMenuSystem(self):
    """
    Processes menu heirarchy dictionary into menu on the top of the screen
    """
    self.root.option_add("*tearOff", False) #Not sure how to implement this
    self.toplevel = tk.Menu(self.root)
    processMenuHierarchy(self.toplevel, self.menus, self)
    self.root.config(menu=self.toplevel)

  #Widget Functions
  def addCamera(self, camnum, interface="match", rewidget=False):
    """
    Adds a listener for a remote camera at a specified camnum socket
    Tries to reconnect with the FailedCamera widget if it cannot connect at first
    """
    if interface not in self.cameras:
      self.cameras[interface] = []
    ind = len(self.cameras[interface]) #Camera index to swap in case of failure
    camera = labels.Camera(camnum, self.root, self, interface, ind)
    self.cameras[interface].append(camera)
    if rewidget:
      return camera

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

  def addEntry(self, interface="mainmenu", font=None, rewidget=False):
    """
    Adds a user entry to the given interface
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
    command = makePartial(command, partialarg, self=self)
    if font:
      button = labels.Button(self.root, text=text, command=command, font=font)
    else:
      button = labels.Button(self.root, text=text, command=command)
    self.buttons[interface].append(button)
    if rewidget:
      return button

  def addCheckbox(self, text, onval=True, offval=False, interface="mainmenu", font=None, rewidget=False):
    """
    Adds a checkbox to the given interface
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
    Adds a set of mutually exclusive radio button selections to the given interface
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
    Adds a user entry field with default values to the given interface
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
    Adds a field with only default values to the given interface
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
    Adds a text box to the given interface
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
    Adds a bar which ranges between two numbers to the given interface
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
    self.gridded.remove(widget)
    return location

  def replaceWidget(self, replaced, replacer, option = None):
    """
    Ungrids the replaced widget and puts replacer in its place
    """
    location = self.ungridWidget(replaced)
    self.gridWidget(replacer, location[0], location[1], location[2], location[3])

  def processGuiStack(self, stackmap):
    """
    Grids the items in self.stack in appropriate column according to the stackrules file used
    """
    stackrules = stackmaps[stackmap]
    row = 0
    for key in self.stacks:
      gridparams = stackrules[key]
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
    Only uses the first two items in the given guimap
    """
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
      self.gridWidget(widget, column=column, row=row, columnspan=columnspan, rowspan=rowspan)
  
  def getWidgetFromName(self, widgetname, guiname):
    """
    Retrieves a widget based on its gui reference name
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
    """
    Tries to stop everything from functioning
    Usually ignored: This may be fixed in the future
    """
    self.active = False

  #Depreciated in favor of several functions under configuration.py
  def pollForCams(self, camrange):
    """
    Checks for active cams on the network
    """
    for num in range(camrange):
      self.addCamera(num)

  def switchUi(self, guiname):
    """
    Configures the window for the next gui to be set up
    Given the regular match socket is used, this will automatically cause the respective gui's menu function to be called
    """
    self.tearDown()
    #Configures window for the new gui
    config.configfunctions[guiname](self)
    #Grids gui widgets)
    self.processGuiMap(guiname)
    #If a gui file references stack rules, use those stack rules to grid widgets in self.stacks
    if "stackrules" in guimaps[guiname][2]:
      self.processGuiStack(guimaps[guiname][2]["stackrules"])
    self.interface = guiname

  def tearDown(self):
    """
    Clears the window of all the widgets in the gridded registry
    If widgets are added to the window indirectly, this will not work.
    """
    for widget in self.gridded:
        widget.ungrid()
    self.gridded.clear()

  def emergencyShutdown(self):
    """
    Safely shuts down system in case of error
    Needs to be integrated into competiton code
    """
    for cam in self.cameras:
      cam.shutdown()
    for cam in self.localcameras:
      cam.shutdown()
  
def splitWidgetName(widgetname):
  """
  Splits a widget's gui file name into the widget's type and number
  """
  #Seperates widget's end tag from its type indicator
  num = int(re.sub(r"[a-zA-Z]", "", widgetname))
  widgettype = re.sub(r"[0-9]", "", widgetname)
  return widgettype, num
  
def isValidWidget(widgettype):
  """
  Determines if the given string will be recognized as a widget type
  """
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
    
def makePartial(func, partialarg, self=None, convertpartialarg = False):
  """
  Makes a partial function out of an argument and command
  """
  partialarg = processPartialArg(partialarg, self=self)
  partial = fts.partial(func, partialarg)
  return partial
  
def processPartialArg(partial, *args, self=None, convertfromnum=False):
  """
  Accounts for special cases where the partial argument needs to be modified to function as intended
  """
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

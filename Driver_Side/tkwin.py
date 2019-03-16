#tkwin.py: A class to manage tkinter's interaction with FRC networktables
#1/8/2019 HP

#Module Imports
import threading
import json
import timer
import re #Used for string processing
import functools as fts
import tkinter as tk

#Local Imports
import labels
import configuration as config
#Safe to import in this method since visglobals is a small file I coded myself
from visglobals import *

#Globals
NOARG = "*None*"
GLOBAL = "*Global*"
SELF = "*Self*"

class TkWin:
  def __init__(self, name, width=800, 
               height=600, menustructure={}, 
               ip=myip, xloc=1915, yloc=0):
    #TODO width and height are magic numbers
    self.name = name
    #Sets up the window root
    self.root = tk.Tk()
    self.root.title = name #Sets the title of the window as the user sees it
    self.root.geometry("{}x{}+{}+{}".format(width, height, xloc, yloc))
    self.fullscreen = False
    self.root.bind("<F11>", self.toggleFullscreen)
    self.root.bind("<Escape>", self.escapeFullscreen)
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
    self.ip = ip
    self.methodnames = {}
    #Binds object method names to strings so they could be reffered to before object creation
    self.bindMethodNames()

  def runWin(self):
    """
    Initiates the tkinter window while running the instance's set thread function
    """
    self.thread.start()
    self.root.mainloop()

  def toggleFullscreen(self, _):
    self.fullscreen = not self.fullscreen
    self.root.attributes("-fullscreen", self.fullscreen)

  def activateFullscreen(self, _):
    self.fullscreen = True
    self.root.attributes("-fullscreen", True)

  def escapeFullscreen(self, _):
    self.fullscreen = False
    self.root.attributes("-fullscreen", False)

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

  #UI functions
  def startMatchInterface(self):
    """
    Sends the Vision System start signal for a competition match
    """
    self.switchUi(competitioninterface)
    sendStartSignal()

  #Widget Functions
  def addCamera(self, camnum, interface="match", rewidget=False):
    """
    Adds a listener for a remote camera at a specified camnum socket
    Tries to reconnect with the FailedCamera widget if it cannot connect at first
    """
    if interface not in self.cameras:
      self.cameras[interface] = []
    ind = len(self.cameras[interface]) #Camera index to swap in case of failure
    camera = labels.Camera(camnum, self.root, self, interface, ind, ip=self.ip)
    self.cameras[interface].append(camera)
    if rewidget:
      return camera

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

  #Unused in favor of several functions under configuration.py
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
  
  def copyMatchCameras(self, interface):
    """
    Copies the cameras in the match interface to the specified interface
    """
    #Initalizes list for the given interface
    self.cameras[interface] = []
    if "match" in self.cameras:
      #Adds cameras from match interface to specified interface
      for camera in self.cameras["match"]:
        self.cameras[interface].append(camera)

  def bindMethodNames(self):
      self.methodnames = {"runWin": self.runWin, "toggleFullscreen": self.toggleFullscreen, 
                "activateFullscreen": self.activateFullscreen, "escapeFullscreen": self.escapeFullscreen, 
                "setThread": self.setThread, "initMenuSystem": self.initMenuSystem, 
                "startMatchInterface": self.startMatchInterface, "addCamera": self.addCamera, 
                "addEntry": self.addEntry, "addButton": self.addButton, 
                "addCheckbox": self.addCheckbox, "addRadioButton": self.addRadioButton, 
                "addCombobox": self.addCombobox, "addListbox": self.addListbox, 
                "addText": self.addText, "addScale": self.addScale, 
                "gridWidget": self.gridWidget, "ungridWidget": self.ungridWidget,
                "replaceWidget": self.replaceWidget, "processGuiStack": self.processGuiStack, 
                "processGuiMap": self.processGuiMap, "getWidgetFromName": self.getWidgetFromName, 
                "switchUi": self.switchUi, "tearDown": self.tearDown, 
                "emergencyShutdown": self.emergencyShutdown, "killLoop": self.killLoop,
                "copyMatchCameras": self.copyMatchCameras}

class SwitchingWindow(TkWin):
  def switchToStagedCam(self):
    """
    Switches the camera number of the active camera widget to the number staged in networktables
    """
    staged = visiontable.getNumber("activecam", 0)
    if self.vars["staged"][0] != staged:
        #Tells the pi the camera is active for backward compatibility
        visiontable.putBoolean("{}isactive".format(staged), True)
        self.cameras["match"][0].changeCamnum(staged)
        self.vars[staged] = [staged]

#Multiview interface that never worked
class MultiviewWindow(TkWin):
  mains = [0, 1]
  sides = [2, 3]

  def putToDash(self, textbox, value):
    if textbox == "staged":
        staged = ""
        #Lists staged cameras in a gramatically correct manner
        for ind, val in enumerate(value):
            if ind == 0:
                if len(value) > 2:
                    staged += camnames[val] + ", "
                elif len(value) == 1:
                    staged += camnames[val]
                else:
                    staged += camnames[val] + " "
            elif ind == len(value)-1:
                staged += "and " + camnames[val]
            else:
                staged += camnames[val] + ", "
        if len(self.vars["staged"]) > 1:
            text = "The {} cameras are staged".format(staged)
        else:
            text = "The {} camera is staged".format(staged)
        self.textboxes["multiview"][0].setValue(text)
    elif textbox == "active":
        if value == True:
            active = "active"
        elif value == False:
            active = "not active"
        plural = len(self.vars["staged"]) > 1
        if plural:
            text = "The staged cameras are {}".format(active)
        else:
            text = "The staged camera is {}".format(active)
        self.textboxes["multiview"][1].setValue(text)
        if value:
            if plural:
                self.buttons["multiview"][7].setText("Deactivate Cameras")
            else:
                self.buttons["multiview"][7].setText("Deactivate Camera")
        else:
            if plural:
                self.buttons["multiview"][7].setText("Activate Cameras")
            else:
                self.buttons["multiview"][7].setText("Activate Camera")
    elif textbox == "quality":
        #Finds whether main, side, or both hierarchies of camera are staged
        stagedhierarchies = self.stagedCamHierarchies()
        resolutions = ""
        if stagedhierarchies[0] and stagedhierarchies[1]:
            resolutions += "\n({}x{} for main cameras and {}x{} for side cameras)".format(int(480*(value/7)), int(640*(value/7)), int(480*(value/14)), int(640*(value/14)))
        elif stagedhierarchies[0] and (not stagedhierarchies[1]):
            resolutions += "\n({}x{} for main cameras)".format(int(480*(value/7)), int(640*(value/7)))
        elif (not stagedhierarchies[0]) and stagedhierarchies[1]:
            resolutions += "\n({}x{} for side cameras)".format(int(480*(value/14)), int(640*(value/14)))
        else:
            raise ValueError("Staged camera index is empty")
        text = "The current quality preset is {} {}".format(value, resolutions)
        self.textboxes["multiview"][2].setValue(text)
    elif textbox == "color":
        if value:
            color = "RGB"
            self.buttons["multiview"][12].setText("Black & White")
        else:
            color = "B&W"
            self.buttons["multiview"][12].setText("Color")
        text = "Color: {}".format(color)
        self.textboxes["multiview"][3].setValue(text)
    elif textbox == "framerate":
        stagedhierarchies = self.stagedCamHierarchies()
        framerates = ""
        if stagedhierarchies[0] and (not stagedhierarchies[1]):
            framerates += "\n({}fps for main cameras)".format(int(30*(value/7)))
        elif (not stagedhierarchies[0]) and stagedhierarchies[1]:
            framerates += "\n({}fps for side cameras)".format(int(30*(value/7)))
        elif stagedhierarchies[0] and stagedhierarchies[1]:
            framerates += "\n({}fps for main cameras and {}fps for side cameras)".format(int(30*(value/7)), int(20*(value/7)))
        else:
            raise ValueError("Staged camera index is empty")
        text = "The current framerate preset is {} {}".format(value, framerates)
        self.textboxes["multiview"][4].setValue(text)
    elif textbox == "diagnostic":
        self.textboxes["multiview"][5].setValue(text)

  def setRemainingTime(self, time):
    text = "Match Currently running \n{} seconds remaning".format(time)
    self.putToDash("diagnostic", text)

  def stagedCamHierarchies(self):
      staged = self.vars["staged"]
      stagedhierarchies = [False, False]
      if (0 in staged) or (1 in staged):
          stagedhierarchies[0] = True
      if (2 in staged) or (3 in staged):
          stagedhierarchies[1] = True
      return stagedhierarchies

  def stageFrontCam(self):
      #The staged (active) camera objects
      self.vars["staged"] = [0]
      self.resetToggles(0)
      visiontable.putNumber("activecam", 0)
      self.putToDash("staged", self.vars["staged"])

  def stageBackCam(self):
      self.vars["staged"] = [1]
      visiontable.putNumber("activecam", 1)
      self.resetToggles(1)
      self.putToDash("staged", self.vars["staged"])

  def stageLeftCam(self):
      self.vars["staged"] = [2]
      visiontable.putNumber("activecam", 2)
      self.resetToggles(2)
      self.putToDash("staged", self.vars["staged"])

  def stageRightCam(self):
      self.vars["staged"] = [3]
      visiontable.putNumber("activecam", 3)
      self.resetToggles(3)
      self.putToDash("staged", self.vars["staged"])

  def stageAllCams(self):
      self.vars["staged"] = [0, 1, 2 ,3]
      self.resetToggles("all")
      self.putToDash("staged", self.vars["staged"])

  def stageMainCams(self):
      self.vars["staged"] = [0, 1]
      self.resetToggles("main")
      self.putToDash("staged", self.vars["staged"])

  def stageSubCams(self):
      self.vars["staged"] = [2, 3]
      self.resetToggles("sub")
      self.putToDash("staged", self.vars["staged"])

  def resetToggles(self, staged):
      self.resetActivity(staged)
      self.resetColor(staged)

  def toggleActivity(self):
      """
      Toggles wether the staged cameras are active or not
      """
      self.vars["isactive"] = not self.vars["isactive"]
      if self.vars["isactive"]:
          self.activateStaged()
      else:
          self.deactivateStaged()
      self.putToDash("active", self.vars["isactive"])


  def activateStaged(self):
      staged = self.getStagedCams()
      for camera in staged:
          activate(camera)

  def deactivateStaged(self):
      staged = self.getStagedCams()
      for camera in staged:
          deactivate(camera)

  def increaseFramerate(self):
      #Checks if framerate preset is at or above maximum
      if self.vars["framerate"] >= 7:
          return
      self.vars["framerate"] += 1
      self.updateToFramerate()
      self.putToDash("framerate", self.vars["framerate"])

  def decreaseFramerate(self):
      #Checks if framerate preset is at or below minimum
      if self.vars["framerate"] <= 1:
          return
      self.vars["framerate"] -= 1
      self.updateToFramerate()
      self.putToDash("framerate", self.vars["framerate"])

  def updateToFramerate(self):
      """
      Updates all cameras to the class framerate preset
      """
      staged = self.getStagedCams()
      preset = self.vars["framerate"]
      for ind in self.vars["staged"]:
          camera = staged[ind]
          if ind in self.mains:
              updateCamToFramerate(camera, preset, main=True)
          elif ind in self.sides:
              updateCamToFramerate(camera, preset, main=False)
          else:
              raise ValueError("Staged Index {} out of known range".format(self.vars["staged"][ind]))

  def increaseQuality(self):
      if self.vars["quality"] >= 7:
          return
      self.vars["quality"] += 1
      self.updateToQuality()
      self.putToDash("quality", self.vars["quality"])

  def decreaseQuality(self):
      if self.vars["quality"] <= 1:
          return
      self.vars["quality"] -= 1
      self.updateToQuality()
      self.putToDash("quality", self.vars["quality"])

  def updateToQuality(self):
      """
      Updates all cameras the class quality preset
      """
      staged = self.getStagedCams()
      preset = self.vars["quality"]
      for ind in self.vars["staged"]:
          camera = staged[ind]
          if ind in self.mains:
              updateCamToQuality(camera, preset, main=True)
          elif ind in self.sides:
              updateCamToQuality(camera, preset, main=False)
          else:
              raise ValueError("Staged Index {} out of known range".format(self.vars["staged"][ind]))

  def toggleColor(self):
      """
      Toggles the entire class's color from/to color
      """
      staged = self.getStagedCams()
      self.vars["color"] = not self.vars["color"]
      for camera in staged:
          setCamColor(camera, self.vars["color"])
      self.putToDash("color", self.vars["color"])

  def sendConnectedMessage(self):
    #This function may be overriden by a subclass if more/different devices need to be messaged
    comsock.sendto(b"connected", (piip, 5800))

  #Function never worked before, and was therefore simplified
  def resetActivity(self, staged):
      return True

  #Same rationale as above
  def resetColor(self, staged):
      return True

  def getStagedCams(self):
    staged = []
    for num in self.vars["staged"]:
      staged.append(self.cameras["match"][num])
    return staged

def activate(camera):
    camera.active = True
    camera.updateOverNetwork()

def deactivate(camera):
    camera.active = False
    camera.updateOverNetwork()

def updateCamToQuality(camera, preset, main = True):
    """
    Updates a single camera to one of the preset quality values
    """
    if main:
        quality = (int(480*(preset/7)), int(640*(preset/7)))
    else:
        quality = (int(480*(preset/14)), int(640*(preset/14)))
    camera.width = quality[1]
    camera.height = quality[0]
    camera.updateOverNetwork()

def updateCamToFramerate(camera, preset, main = True):
    """
    Updates a single camera to one of the preset framerate values
    """
    #Framerate will be higher for main cameras since they are more important
    if main:
        framerate = int(30*(preset/7))
    else:
        framerate = int(20*(preset/7))
    camera.framerate = framerate
    camera.updateOverNetwork()

def setCamColor(camera, color):
    """
    Sets a single camera to color/BW
    """
    camera.color = color
    camera.updateOverNetwork()

class SplitCam(TkWin):
  defaultlocation = (1, 1, 16, 16)

  def splitCamInTwo(self, cams, horizontal=True):
      self.ungridStaged()
      if horizontal:
          rows = self.defaultlocation[0], int((self.defaultlocation[2]-self.defaultlocation[0])/2)+2
          columns = self.defaultlocation[1], self.defaultlocation[1]
          rowspans = int(self.defaultlocation[2]/2), int(self.defaultlocation[2]/2)
          columnspans = self.defaultlocation[3], self.defaultlocation[3]
      else:
          rows = self.defaultlocation[0], self.defaultlocation[0]
          columns = self.defaultlocation[1], int((self.defaultlocation[3]-self.defaultlocation[1])/2)
          rowspans = self.defaultlocation[2], self.defaultlocation[2]
          columnspans = int(self.defaultlocation[3]/2), int(self.defaultlocation[3]/2)
      for ind in range(2):
          self.gridWidget(self.cameras["match"][cams[ind]], rows[ind], columns[ind], rowspans[ind], columnspans[ind])
      self.vars["staged"] = cams

  def splitToMains(self):
      self.splitCamInTwo(cams=[0, 1])

  def splitToSides(self):
      self.splitCamInTwo(cams=[2, 3])

  def splitCamInFour(self, order=[0,1,2,3]):
      self.ungridStaged()
      rows = (self.defaultlocation[0], int((self.defaultlocation[2]-self.defaultlocation[0])/4)+2, 
              self.defaultlocation[0], int((self.defaultlocation[2]-self.defaultlocation[0])/4)+2)
      columns = (self.defaultlocation[1], self.defaultlocation[1],
              int((self.defaultlocation[3]-self.defaultlocation[1])/4)+2, int((self.defaultlocation[3]-self.defaultlocation[1])/4)+2)
      rowspans = int(self.defaultlocation[2]/4), int(self.defaultlocation[2]/4), int(self.defaultlocation[2]/4), int(self.defaultlocation[2]/4)
      columnspans = int(self.defaultlocation[3]/4), int(self.defaultlocation[3]/4), int(self.defaultlocation[3]/4), int(self.defaultlocation[3]/4)
      for ind in range(4):
          self.gridWidget(self.cameras["match"][order[ind]], rows[ind], columns[ind], rowspans[ind], columnspans[ind])
      self.vars["staged"] = order

  def splitToAll(self):
      self.splitCamInFour(self)

  def ungridStaged(self):
      staged = self.getStagedCams()
      for camera in staged:
          self.ungridWidget(camera)

  def getStagedCams(self):
    staged = []
    for num in self.vars["staged"]:
      staged.append(self.cameras["match"][num])
    return staged

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

#Networking functions
def sendStartSignal():
  comsock.sendto(b"start", (piip, 5800))

#Puts pi into configuration mode
def configSystem():
  visiontable.putBoolean("config", True)

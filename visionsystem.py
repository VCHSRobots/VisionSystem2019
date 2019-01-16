#visionsystem.py: High level vision system interface
#HP 1/8/2019

import tkwin
import json
from networktables import NetworkTables as nt

ntip = "10.44.15.1"
nt.initialize(ntip)
visiontable = nt.getTable("/vision")

def testLoop(self):
    """
    Thread fucntion to be called by the tkinter class
    """
    while True:
        while self.active:
            activecams = getActiveCams(self, len(self.cameras))
            for activeind in activecams:
                self.cameras[activeind].updateImgOnLabel()

def testSystem():
    """
    A simple test of the vision system involving only one camera
    """
    win = tkwin.TkWin("Test")
    camnums = getActiveCams(10)
    for camnum in camnums:
        win.addCam(0)
    win.setThreadLoop(testLoop)
    guifile = open("test.gui")
    guimap = json.load(guifile)
    guifile.close()
    win.processGuiMap(guimap)
    win.runWin()

def getActiveCams(self, numrange):
    """
    Polls NetworkTables to check which cameras are active
    """
    actives = []
    for num in range(numrange):
        isactive = visiontable.getBoolean("{0}isactive".format(num), False)
        if isactive:
            actives.append(num)
    return actives

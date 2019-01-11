#visionsystem.py: High level vision system interface
#HP 1/8/2019

import tkwin
from networktables import NetworkTables as nt

ip = "10.44.15.1"
nt.initialize(ip)
visiontable = nt.getTable("/vision")

def testLoop(self):
    """
    Thread fucntion to be called by the tkinter class
    """
    while True:
        while self.active:
            activecams = getActiveCams(len(self.cameras))
            for activeind in activecams:
                self.cameras[activeind].updateImgOnLabel()

def testSystem():
    """
    A simple test of the vision system involving only one camera
    """
    win = tkwin.TkWin("Test")
    win.addCam(0)
    win.setThreadLoop(testLoop)
    win.runWin()

def getActiveCams(self, numrange):
    """
    Polls NetworkTables to check which cameras are active
    """
    actives = []
    for num in range(numofcams):
        isactive = visiontable.getBoolean("camera{0}".format(num), False)
        if isactive:
            actives.append(num)
    return actives

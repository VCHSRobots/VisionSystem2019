#threads.py: Handles threading for sockettables
#1/29/2019 HP

#import comsock
import threading
from networktables import NetworkTables as nt

import menus

matchfunctions = menus.matchfunctions

"""
class SocketThread(threading.Thread):
  def __init__(self, threadID, name, counter, timeout = 180):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.timeout = timeout

  def run(self):
    self.daemon = True
    comsock.mainloop(self.timeout)
"""

class SystemThread(threading.Thread):
  def __init__(self, win, threadID=0, name="", counter=0, roundtime = 180):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.roundtime = roundtime
    self.lastinterface = "mainmenu"
    self.win = win

  def run(self):
    while not nt.isConnected():
      nt.startClient("10.44.15.2")
    win = self.win
    print(win.interface, self.lastinterface)
    print(win)
    while True:
      if self.win.interface != self.lastinterface:
        matchfunctions[self.win.interface](self.win)
        self.lastinterface = self.win.interface

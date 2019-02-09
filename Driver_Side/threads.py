#threads.py: Handles threading for sockettables
#1/29/2019 HP

import comsock
import threading

import menus

matchfunctions = menus.matchfunctions

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

class SystemThread(threading.Thread):
  def __init__(self, threadID=0, name="", counter=0, roundtime = 180):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.roundtime = roundtime
    self.lastinterface = "mainmenu"

  def run(self, win):
    if win.interface != self.lastinterface:
      matchfunctions[win.interface](win)
      self.lastinterface = win.interface

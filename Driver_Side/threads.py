#threads.py: Handles threading for sockettables
#1/29/2019 HP

import comsock
import threading

class SocketThread(threading.Thread):
  def __init__(self, threadID, name, counter, timeout = 180):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter
    self.timeout = timeout

  def run(self):
    comsock.mainloop(self.timeout)

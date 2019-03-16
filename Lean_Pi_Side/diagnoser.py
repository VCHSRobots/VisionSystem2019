#diagnoser.py: Class which prints or saves diagnostic messages for the Pi Vision System
#2/20/2019 HP

import time

class Diagnoser:
  """
  Prints diagnostic output for Pi Vision System
  """
  def __init__(self, interval):
    self.interval = interval
    self.lastprinttime = 0
    self.framessent = 0
    self.totalsize = 0

  def update(self, framesize):
    self.framessent += 1
    self.totalsize += framesize
    if time.perf_counter()-self.lastprinttime >= self.interval:
      self.print()

  def print(self):
    bytespersec = self.totalsize/10
    bitspermin = bytespersec*8/1000000
    fps = self.framessent/10
    print("{0} frames sent at {1}fps. Average Mb/sec: {2}".format(self.framessent, fps, bitspermin))
    self.lastprinttime = time.perf_counter()
    self.framessent = 0
    self.totalsize = 0

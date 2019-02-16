import time

class Timer:
  def __init__(self, time=150):
    self.time = time
    self.starttime = 0

  def start(self):
    self.reset()
    self.starttime = time.perf_counter()
    self.lasttime = time.perf_counter()

  def updateTime(self):
    currenttime = time.perf_counter()
    timelost = currenttime - self.starttime
    remaining = self.time - timelost
    return remaining

  def reset(self):
    self.starttime = self.time

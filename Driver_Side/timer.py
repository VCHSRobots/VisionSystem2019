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
    self.remaining = self.time - timelost
    return self.remaining

  def reset(self):
    self.remaining = self.time

  @property
  def remaining(self):
    self.__remaining = self.time
  
  @remaining.setter
  def remaining(self, setval):
    if setval > 0:
      self.__remaining =  setval
    if setval < self.time:
      self.__remaining = self.time
    if setval <= 0:
      self.__remaining = 0
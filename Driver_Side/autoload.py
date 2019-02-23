import setvals

camfiles = {"Cam1": "defaultvals.json", 
            "Cam2": "defaultvals.json", 
            "Cam3": "defaultvals.json", 
            "Spare": "defaultvals.json"}

def cam1Setup(filename):
  vals = setvals.getJson(filename)
  setvals.loadFile(vals, [0])

def cam2Setup(filename):
  vals = setvals.getJson(filename)
  setvals.loadFile(vals, [1])

def cam3Setup(filename):
  vals = setvals.getJson(filename)
  setvals.loadFile(vals, [2])

def spareSetup(filename):
  vals = setvals.getJson(filename)
  setvals.loadFile(vals, [3])

def loadValues():
  cam1Setup(camfiles["Cam1"])
  cam2Setup(camfiles["Cam2"])
  cam3Setup(camfiles["Cam3"])
  spareSetup(camfiles["Spare"])
  
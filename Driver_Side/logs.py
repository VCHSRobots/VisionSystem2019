#logs.py: Manages error logs in the vision system
#1/29/2019 HP

import json
import time

logfilename = "logs.json"

def log(message):
  logfile = open(logfilename)
  logs = json.load(logfile)
  logfile.close()
  t = time.ctime()
  logs[t] = message
  json.dump(logs, logfilename)
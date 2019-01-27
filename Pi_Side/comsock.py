#comsock.py: Manages the pi side of the two-way communications socket between the pi and computer because NetworkTables malfunctioned
#1/26/2019 HP

#Module Imports
import socket
import zlib

myip = "10.44.15.62"
internip = ""
myadr = (myip, 5809)
internadr = (internip, 4000)
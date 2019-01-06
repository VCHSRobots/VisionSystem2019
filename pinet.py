#pinet.py: Hosts socket for pi camera using UTP or TCP
#11/17/2018 HP

#Module Imports
import time
import socket
import pickle
import imutils
#import somecompressionlib
import cv2 as cv
import numpy as np
from networktables import NetworkTables as nt

#Globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM
RGB = cv2.BGR2RGB
GRAY = cv2.BGR2GRAY
dwidth = 400
dhegiht = 400

def setupSocket(ip, socktype, port):
    #Sets up and returns a ready to use socket bound to the ip and port arguments
    sock = socket.socket(socket.AF_INET, socktype)
    sock.bind((ip, port))
    sock.listen()
    return sock

def exportImg(camera, camnum, sock, width = dwidth, height = dheight, color = RGB):
    #Reads, pickles, and exports an image from the OpenCV camera
    _, frame = camera.read()
    frame = processImg(frame, width, height, color)
    frame = pickle.dumps(frame)
    sock.sendto(labledframe, camnum+5800)

def processImg(img, width = dwidth, height = dheight, color = RGB):
    #Processes an image in numpy array format to the desired specefications
    img = imutils.resize(width = width, height = height)
    img = cv.cvtcolor(img, color)
    return img

def makeCam(camnum):
    #Tries to make a camera, fails if it doesn't work
    camera = cv.VideoCapture(camnum)
    ret, _ = camera.read()
    if ret:
        return camera
    else:
        return False

def findCam(numrange = (0, 100)):
    #Scans through numbers within numrange and returns the first unexcluded camera
    cam = False
    for num in range(numrange[0], numrange[1]):
            cam = makeCam(num)
            if cam != False:
                return num, cam

def scanForCams(numrange = (0, 100)):
    #Scans through numbers within numrange and returns all found cameras
    cams = []
    for num in range(numrange[0], numrange[1]):
            cam = makeCam(num)
            if cam != False:
                cams.append((num, cam))
    return cams

def setupNetworkTable(ip, tablename = "/"):
   #Sets up networktable client with the specified ip and returns the specified table
   nt.initialize(ip)
   table = nt.getTable(tablename)
   return table

def pollCamVars(camnum, table):
    active = table.getBoolean("{0}isactive".format(camnum), False)
    width = table.getInt("{0}width".format(camnum), dwidth)
    height = table.getInt("{0}height".format(camnum), dheight)
    color = table.getString("{0}color".format(camnum), "RGB")
    framerate = table.getInt("{0}framerate".format(camnum), 10) #Finds time interval for each camera. Defaults to 20/s
    if color == "RGB":
        color = RGB
    elif color == "GRAY":
        color = GRAY
    else:
        color = RGB
    return active, width, height, color, framerate

def exportStream(camnum, ip, socktype = UTP, port = 1024):
    #Starts a stream of pickled images from the camera connected to external port camnum in the specified ip and network port
    sock = setupSocket(ip, socktype, port)
    camactive = False
    cam = findCam()
    while True:
        exportImg(cam, sock, port)
        if cv.waitKey(1) == 0:
            break

def exportManagedStream(camnum, ip, socktype = UTP, port = 1024):
    timepassed = [] #The time passed since the last frame update for each camera
    #sock = setupSocket(ip, socktype, port)
    socks = 
    camactive = False
    cams = scanForCams()
    table = setupNetworkTable(ip, "/vision")
    starttime = time.perf_counter()
    timerecords = [[starttime, 0]] * len(cams) #Makes a records of when the time was last recorded and how long it's been since the frame was last updated for each camera in (lasttime, framediff) order
    while True:
        for num, cam in enumerate(cams):
            active, width, height, color, framerate = pollCamVars(num, table)
            timerecords[num][1] += time.perf_counter()-timerecords[num][1] #Compares current time to time since the last time update to see how much time has passed
            if active and timerecords[num][1] > 1/framerate: #If camera is active and framerate time has passed
                exportImg(cam, sock, port, width, height, color)
        if cv.waitKey(1) == 0:
            break

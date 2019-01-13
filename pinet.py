#pinet.py: Hosts socket for pi camera using UTP or TCP
#11/17/2018 HP

#Module Imports
import time
import socket
import pickle
import imutils
import zlib
import cv2
import numpy as np
from networktables import NetworkTables as nt

#Globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM
RGB = cv2.BGR2RGB
GRAY = cv2.BGR2GRAY
dwidth = 400
dheight = 400

def setupSocket(ip, socktype, port):
    """
    Sets up and returns a ready to use socket bound to the ip and port arguments
    """
    sock = socket.socket(socket.AF_INET, socktype)
    sock.bind((ip, port))
    sock.listen()
    return sock

def exportImg(camera, camnum, sock, width = dwidth, height = dheight, color = RGB, compression = 6):
    """
    Reads, pickles, and exports an image from the OpenCV camera
    """
    _, frame = camera.read()
    frame = processImg(frame, width, height, color)
    frame = zlib.compress(frame, compression)
    frame = pickle.dumps(frame)
    sock.sendto(frame, camnum+5800)

def processImg(img, width = dwidth, height = dheight, color = RGB):
    """
    Processes an image in numpy array format to the desired specefications
    """
    img = imutils.resize(width = width, height = height)
    img = cv2.cvtcolor(img, color)
    return img

def makeCam(camnum):
    """
    Tries to make a camera, fails if it doesn't work
    """
    camera = cv2.VideoCapture(camnum)
    ret, _ = camera.read()
    if ret:
        return camera
    else:
        return False

def findCam(numrange = (0, 100)):
    """
    Scans through numbers within numrange and returns the first unexcluded camera
    """
    cam = False
    for num in range(numrange[0], numrange[1]):
            cam = makeCam(num)
            if cam != False:
                return num, cam

def scanForCams(numrange = (0, 100)):
    """
    Scans through numbers within numrange and returns all found cameras
    """
    cams = {}
    for num in range(numrange[0], numrange[1]):
            cam = makeCam(num)
            if cam != False:
                cams[num] = cam
    return cams

def setupNetworkTable(ip, tablename = "/"):
    """
    Sets up networktable client with the specified ip and returns the specified table
    """
    nt.initialize(ip)
    table = nt.getTable(tablename)
    return table

def pollCamVars(camnum, table):
    """
    Recieves NetworkTables variables for the specified camera number
    """
    active = table.getBoolean("{0}isactive".format(camnum), False)
    width = table.getInt("{0}width".format(camnum), dwidth)
    height = table.getInt("{0}height".format(camnum), dheight)
    color = table.getString("{0}color".format(camnum), "RGB")
    framerate = table.getInt("{0}framerate".format(camnum), 10) #Finds time interval for each camera. Defaults to 20/s
    compression = table.getInt("{0}compression".format(camnum), 6)
    if color == "RGB":
        color = RGB
    elif color == "GRAY":
        color = GRAY
    else:
        color = RGB
    return active, width, height, color, framerate, compression

def exportStream(camnum, ip, socktype = UTP, port = 1024):
    """
    Starts a stream of pickled images from the camera connected to external port camnum in the specified ip and network port
    """
    sock = setupSocket(ip, socktype, port)
    cam = findCam()
    while True:
        exportImg(cam, sock, port)
        if cv2.waitKey(1) == 0:
            break

def exportManagedStream(ip, numrange = (0, 10), socktype = UTP, port = 1024):
    """
    Exports a stream of images with each camera individually managed by its NetworkTables values
    """
    sock = setupSocket(ip, socktype, port)
    cams = scanForCams(numrange=(0,10)) #Gets a dict of avalible cams within the number range 
    #TODO: Make cams a dict as opposed to a list
    table = setupNetworkTable(ip, "/vision")
    starttime = time.perf_counter()
    timerecords = [[starttime, 0]] * len(cams) #Makes a records of when the time was last recorded and how long it's been since the frame was last updated for each camera in (lasttime, framediff) order
    while True:
        for num in cams:
            active, width, height, color, framerate, compression = pollCamVars(num, table)
            timerecords[num][1] += time.perf_counter()-timerecords[num][1] #Compares current time to time since the last time update to see how much time has passed
            if active and timerecords[num][1] > 1/framerate: #If camera is active and framerate time has passed
                exportImg(cams[num], num, sock, width, height, color, compression)
        if cv2.waitKey(1) == 0:
            break

exportManagedStream(ip="10.44.15.1")
#network.py: Client-side networking for vision system
#11/17/2018 HP

#Module Level
import socket
import pcikle
import numpy

#globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM

def initSocket(ip, sockettype, port):
    #Returns a socket specified mode and ip
    soc = socket.socket(socket.AF_INET, sockettype)
    soc.bind((ip, port))
    soc.listen()
    return soc

def getImgUtp(socket, port):
    #Returns a numpy array image from the specified utp network camera port
    data = socket.recv(port)
    array = pickle.loads(data)
    return array

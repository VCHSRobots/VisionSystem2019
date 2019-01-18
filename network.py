#network.py: Client-side networking for vision system
#11/17/2018 HP, PR

#Module Level
import socket
import select
import pickle
import numpy

#Globals
TCP = socket.SOCK_STREAM
UTP = socket.SOCK_DGRAM
ip = "10.44.15.41"
sock = socket.socket(socket.AF_INET, UTP)

def initTcpClient(ip, port):
    """
    Returns a socket specified mode and ip. Only needed for tcp sockets
    """
    soc = socket.socket(socket.AF_INET, TCP)
    soc.connect((ip, port))
    return soc

def getImgUtp(sock, size):
    """
    Returns a numpy array image from the specified utp network camera port
    """
    data, sender = sock.recv(size)
    array = pickle.loads(data)
    return array, sender

def selectReadableCams(camsocks):
    readable = []
    socks, _, _ = select.select(camsocks.values(), [], [])
    for sock in socks:
        readable.append(camsocks.index(sock))
    return readable

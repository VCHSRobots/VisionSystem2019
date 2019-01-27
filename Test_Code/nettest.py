#nettest.py: Test of socket networking with the pi and driver computer
#1/14/2019 HP

import socket

def connectToClient():
    """
    Connects a udp server to a network on the specified address
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock

def makeTcp(ip, port):
    """
    Connects to a tcp server
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock
    
def getAddr(num):
    return "10.44.15.41", int(num+4000)

def getSocks():
    socks = []
    for sock in range(0, 10):
        socks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        socks[-1].bind(getAddr(sock))
    return socks
#parseimg.py: Library for quantization-based custom object compression
#1/17/2019

def compress(image, colors = 128):
    """
    Parses image into an efficent compressed byte format
    """
    """
    Format: size header, key: colorval pairs, flag, pixels defined by keys
    """
    #Quantizes images
    #Generates map of colors on bytearray
    #Defines each pixel with smallest possible int on bytearray
    pass

def decompress(image):
    """
    Decompresses an image from byte format
    """
    #Looks for image size

def getBinFromByte(int):
    """
    Gets the binary form of an 8 bit number in a list
    """
    

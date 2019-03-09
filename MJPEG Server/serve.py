import imutils
import cv2
import io
import sys
from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from networktables import NetworkTables

from stdreader import scanForCameras

NetworkTables.startClient("roboRIO-4415-frc.local")
visiontable = NetworkTables.getTable("vision")
width = 320
height = 240
defaultcamvals = {"isactive": True, "width": width, "height": height, "color": True, "framerate": 10, "quality": 28}
intvals = ["width", "height", "quality"]

RGB = cv2.COLOR_BGR2RGB
GRAY = cv2.COLOR_BGR2GRAY

class CamHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path.endswith('.mjpg'):
      self.send_response(200)
      self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
      self.end_headers()
      while True:
        try:
          checkIfCameraChanged()
          rc, img = camera.read()
          if not rc:
            continue
          jpg = processImage(img)
          tmpFile = io.StringIO()
          jpg.save(tmpFile, 'JPEG')
          self.wfile.write("--jpgboundary")
          self.send_header('Content-type','image/jpeg')
          self.send_header('Content-length', str(sys.getSizeOf(tmpFile)))
          self.end_headers()
          jpg.save(self.wfile, format = 'JPEG', quality = visiontable.getNumber("quality", 20))
        except KeyboardInterrupt:
          break
      return
    if self.path.endswith('.html'):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write('<html><head></head><body>')
      self.wfile.write('<img src="http://10.44.15.6:5800/cam.mjpg"/>')
      self.wfile.write('</body></html>')
      return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

#For this to work properly, the cameras must be plugged in in order
def checkIfCameraChanged():
  global camera
  global active
  tablenum = visiontable.getNumber("isactive", camnums[0])
  if active != tablenum:
    if tablenum in camnums:
      camera.release()
      camera = cv2.VideoCapture(tablenum)
      active = tablenum
    setCameraSettings()
    
def updateCameraSettings():
  global width
  global height
  tablewidth = int(visiontable.getNumber("width", width))
  tableheight = int(visiontable.getNumber("height", height))
  if tablewidth != width or tableheight != height:
    width = tablewidth
    height = tableheight
    setCameraSettings

def setCameraSettings():
  """
  Sets camera to global width and height
  """
  global camera
  camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
  camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)

def processImage(img):
  """
  Processes an image from numpy array format to jpeg bytes blob
  """
  if not visiontable.getBoolean("color", True):
    img = cv2.cvtColor(img, cv2.RGB2GRAY)
  img = Image.fromarray(img)
  return img

def main():
  global camera
  global width
  global height
  global active
  global camnums
  camnums = scanForCameras()
  active = visiontable.getNumber("isactive", camnums[0])
  camera = cv2.VideoCapture(active)
  width = int(visiontable.getNumber("width", width))
  height = int(visiontable.getNumber("height", height))
  setCameraSettings()
  try:
    server = ThreadedHTTPServer(('localhost', 5800), CamHandler)
    print("server started")
    server.serve_forever()
  except KeyboardInterrupt:
    camera.release()
    server.socket.close()

if __name__ == '__main__':
  main()

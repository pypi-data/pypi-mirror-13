#!/usr/bin/python3.5

import numpy as np
import cv2 as cv
import sys
import math

# ===========================================================================
# Targeting System Class
# ===========================================================================

class TargetingSystem(object):

  def __init__( self, cam_usb=0, min_val=227, max_val=255 ):
    #Set up camera
    self.camera = cv.VideoCapture( cam_usb )
    
    #Set up threhold values
    self.min      = min_val
    self.max      = max_val

    #Other important stuff that we'll just initialize
    self.frame    = None
    self.thresh   = None
    self.rect     = None
    self.box      = None
    self.contours = None
    self.theta    = None
    self.width    = None
    self.height   = None
    self.frameMid = None
    self.pixwid   = 0

    #setup focal
    self.focal = Focal()
    self.focal.setFocalLength()

    #get width and height
    self.getWidthHeight()

  def __del__( self ):
    #Free the camera
    self.camera.release()
    #cv.destroyAllWindows()
  
  def set_min( self, val=227 ):
    self.min = val

  def set_min( self, val=255 ):
    self.max = val

  def nextFrame( self ):
    n, self.frame  = self.camera.read()
    self.frame = cv.flip(self.frame, flipCode=-1)

  def getPixWid( self ):
    return self.pixwid

  def getWidthHeight( self ):
    n, f = self.camera.read()
    self.height, self.width = f.shape[:2]
    self.frameMid = (int(self.width/2), int(self.height/2))

  def thresholdFrame( self ):
    gray = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
    
    n, self.thresh = cv.threshold(gray, self.min, self.max, cv.THRESH_BINARY)
    
  def findContours( self ):
    n, self.contours, h = cv.findContours(self.thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    shot = False
    for cntr in self.contours:
      self.rect = cv.minAreaRect( cntr )
      self.box = cv.boxPoints( self.rect )
      self.box = np.int0( self.box )
      
      if set(self.box[0]) != set(self.box[1]):

        sortedbox = sorted(self.box, key=lambda point:point[1])
        topLeft = sortedbox[0]
        topRight = sortedbox[1]
        wid = abs(topLeft[0] - topRight[0])

        if wid > 30 and wid < 320:
          self.pixwid = abs(topLeft[0] - topRight[0])

          cv.drawContours( self.frame, [ self.box ], 0, (0,0,255), 2)
          midpoint = ( int((topLeft[0]+topRight[0])/2), int((topLeft[1]+topRight[1])/2) )

          if not shot:
            shot = self.checkShot(midpoint)

          cv.circle( self.frame, midpoint, 5, (0,255,0), thickness=2, lineType=8, shift=0 )

          self.getTheta(midpoint)  

    return shot


  def checkShot( self, midpoint ): 
    midx = midpoint[0]
    midy = midpoint[1]

    if math.hypot( self.frameMid[0] - midx, self.frameMid[1] - midy ) < 20:
      return True
    else:
      return False

  def showFrame( self ):
    cv.imshow( 'frame', self.frame )

  def getTheta( self, midpoint ):
    topLeft  = self.box[0]
    topRight = self.box[1]

    x_off = abs(topLeft[0]-topRight[0])
    y_off = abs(topLeft[1]-topRight[1])

    self.theta = math.degrees(math.atan(y_off/x_off))

    cv.putText(self.frame, str(self.theta), (midpoint[0]+5, midpoint[1]+5), 1, 1.0, (0,255,0))

  def drawCrosshair( self, shot ):
    if shot:
      print( "SHOOT" ) 
      cv.circle( self.frame, (int(self.width/2), int(self.height/2)), 20, (0,255,0), thickness=2, lineType=8, shift=0 )
      cv.line( self.frame, (int((self.width/2)-20), int(self.height/2)), (int((self.width/2+20)), int(self.height/2)), (0,255,0), thickness=1 )
      cv.line( self.frame, ( int(self.width/2), int((self.height/2)-20)), (int(self.width/2), int((self.height/2+20))), (0,255,0), thickness=1 )
    else:
      cv.circle( self.frame, (int(self.width/2), int(self.height/2)), 20, (0,0,255), thickness=2, lineType=8, shift=0 )
      cv.line( self.frame, (int((self.width/2)-20), int(self.height/2)), (int((self.width/2+20)), int(self.height/2)), (0,0,255), thickness=1 )
      cv.line( self.frame, ( int(self.width/2), int((self.height/2)-20)), (int(self.width/2), int((self.height/2+20))), (0,0,255), thickness=1 )
      

  def centroid( self ):
    None

  def readImg( self ):
    self.frame = cv.imread('setdist.png')

  def writeImg( self ):
    cv.imwrite('camimg.png', self.frame)

  def run( self ):
    #Procedure
    
    #get next frame from camera feed
    self.nextFrame()
    #self.readImg()

    #threshold the image
    self.thresholdFrame()

    #find and draw contours
    shot = self.findContours()

    pix = self.getPixWid()

    self.focal.calculateActualDistance( pix )

    distance = self.focal.getDistance()

    print(distance)

    self.drawCrosshair(shot)

    #show the frame
    #self.showFrame()
    #self.writeImg()

# ===========================================================================
# Targeting System Class
# ===========================================================================

class Focal(object):

  def __init__( self ):
    #ALL MEASUREMENTS ARE IN METERS
    self.focal_length = None

    #This should never change once we know this
    self.known_pixel_width = 361

    #This will never change
    self.known_real_width = 0.3556

    #This will never change
    self.known_real_distance = 0.9144

    #This is what we want
    self.actual_real_distance = None

  def __del__( self ):
    pass
  
  def setFocalLength( self ):
    ratio = ( self.known_real_distance / self.known_real_width )
    self.focal_length = self.known_pixel_width * ratio

  def calculateActualDistance( self, current_pixel_width ):
    if current_pixel_width != 0:
      ratio = self.focal_length / current_pixel_width
      self.actual_real_distance = self.known_real_width * ratio
    else:
      self.actual_real_distance = 9999;

  def getDistance( self ):
    return self.actual_real_distance

def Usage():
    print("Usage: ")
    print("./TargetingSystem <CAMERA USB PORT> <THRESHOLD MIN> <THRESHOLD MAX>")

if __name__ == '__main__':
    Usage()
#  if len( sys.argv ) < 2 :
#    Usage()
#  else:
#      print("Starting Targeting System...")
#      if len( sys.argv ) < 3 :
#        usb = int(sys.argv[1])
#        ts  = TargetingSystem( cam_usb=usb )
#      else:
#        usb = int(sys.argv[1])
#        mn  = int(sys.argv[2])
#        mx  = int(sys.argv[3])
#        ts  = TargetingSystem( cam_usb=usb, min_val=mn, max_val=mx )
#
#      while(True):
#        ts.run()
#        if cv.waitKey(1) & 0xFF == ord('q'):
#          break
#      del ts

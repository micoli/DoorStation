import time
import cv2.cv as cv
from threading import Thread
import DoorStation
import logging

logger = logging.getLogger('webcam')

class webcam(Thread):
    running = True
    def __init__(self,door_station,cfg):
        Thread.__init__(self)

    def run(self):
      running = True
      capture = cv.CaptureFromCAM(0)
      cpt = 0
      while running:
          img = cv.QueryFrame(capture)
          cpt = (cpt+1) % 20
          cv.SaveImage('/ram/pic-%d.jpg'%cpt, img)
          time.sleep(8)



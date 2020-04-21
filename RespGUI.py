__author__ = 'jonathanschor'

### Before you run me for the first time, make sure you've done the following:
#   pip3 install opencv-contrib-python
#   pip3 install pyserial
#   pip3 install wxPython

import cv2
import time
import numpy as np
import mineSerial
from GUIDraw import GUIDraw
from threading import Thread
from ItemStore import ItemStore
import sys

space = 10
boxNum = 4
graphNum = 2

#### Establish axis limits
axisHolder = [10,10,800,40,1]

#### Establish starting alarm range
alarmHolder = list()
for i in range(len(axisHolder)):
    alarmHolder.append([-axisHolder[i],axisHolder[i]])

#### Establish labels
labelHolder = [['Pressure','Pr','cmH2O'],
         ['Flow','Flow','L/min'],
         ['Tidal Vol','TV','mL'],
         ['Min Vol','MV','L/min']]

drawGUI = GUIDraw(space,boxNum,graphNum,axisHolder,alarmHolder,labelHolder)
drawGUI.drawInitialScreen()

vals = list()
valHolder = list()
for i in range(boxNum):
    vals.append(0)
    valHolder.append(0)


#### Open serial port
#ser = mineSerial.mineSerial("/dev/cu.usbmodem142201",115200)
#ser.flushInput()
    
serQueue = ItemStore()

drawGUI.updateTime()


#def getSer():
#    partial = None
#    while True:
#        bytesToRead = ser.inWaiting()
#        if bytesToRead>0:
#            wholeSer = ser.read(bytesToRead).decode(errors='ignore')
#            # print(wholeSer)
#            if wholeSer and partial is None and (wholeSer[0] is 'S') and (wholeSer[-1] is '\n'):
#                stripped = wholeSer.rstrip()
#                removeHeader = stripped.split('S')[1]
#                full = removeHeader.split(' ')
#                full.append(time.time())
#                serQueue.put(full)
#                # print(full)
#            elif wholeSer and partial is None and (wholeSer[0] is 'S') and (wholeSer[-1] is not '\n'):
#                stripped = wholeSer
#                partial = stripped
#            elif wholeSer and partial is not None and (wholeSer[0] is not 'S') and (wholeSer[-1] is not '\n'):
#                stripped = wholeSer
#                partial = partial + stripped
#            elif wholeSer and partial is not None and (wholeSer[0] is not 'S') and (wholeSer[-1] is '\n'):
#                stripped = wholeSer
#                stripped = partial + stripped
#                stripped = stripped.rstrip()
#                removeHeader = stripped.split('S')[1]
#                full = removeHeader.split(' ')
#                full.append(time.time())
#                serQueue.put(full)
#                # print(full)
#                partial = None
#
#
#t1 = Thread(target = getSer)
#t1.daemon = True
#t1.start()
drawGUI.updateGUI(serQueue)

# while True:

    #### Read from serial port, hacky parsing to get space delimited values
    # bytesToRead = ser.inWaiting()
    # if bytesToRead>0:
    #     wholeSer = ser.read(bytesToRead).decode(errors='ignore')
    #     if wholeSer and (wholeSer[0] is 'S') and (wholeSer[-1] is '\n'):
    #         stripped = wholeSer.rstrip()
    #         removeHeader = stripped.split('S')[1]
    #         vals = removeHeader.split(' ')


    #### Populate valHolder, replace random values with what you grabbed from serial port


    # #### Show GUI in full screen
    # cv2.imshow(windName,frame)
    # cv2.namedWindow(windName,cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty(windName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    #
    # #### To stop GUI, press "q" on keyboard
    # key = cv2.waitKey(1) & 0xFF
    # if key == ord("q"):
    #     break

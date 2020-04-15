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

space = 10
boxNum = 4
graphNum = 2

#### Establish axis limits
axisHolder = [500, 500,800,40,1]

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
frame = drawGUI.drawInitialScreen()

windName = 'RespGUI'

vals = list()
for i in range(boxNum):
    vals.append(0)

#### Open serial port
ser = mineSerial.mineSerial("/dev/cu.usbmodem142201",115200)
ser.flushInput()

drawGUI.updateTime()

while True:

    #### Read from serial port, hacky parsing to get space delimited values
    bytesToRead = ser.inWaiting()
    if bytesToRead>0:
        wholeSer = ser.read(bytesToRead).decode(errors='ignore')
        if wholeSer and (wholeSer[0] is 'S') and (wholeSer[-1] is '\n'):
            stripped = wholeSer.rstrip()
            removeHeader = stripped.split('S')[1]
            vals = removeHeader.split(' ')


    #### Populate valHolder, replace random values with what you grabbed from serial port
    valHolder = [float(vals[0]),
                 float(vals[1]),
                 float(vals[2]),
                 float(vals[3])]

    frame = drawGUI.updateGUI(valHolder)

    #### Show GUI in full screen
    cv2.imshow(windName,frame)
    cv2.namedWindow(windName,cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(windName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    #### To stop GUI, press "q" on keyboard
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

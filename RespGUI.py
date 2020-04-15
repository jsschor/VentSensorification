__author__ = 'jonathanschor'

### Before you run me for the first time, make sure you've done the following:
#   pip3 install opencv-contrib-python
#   pip3 install pyserial
#   pip3 install wxPython

import cv2
import time
import numpy as np
import mineSerial
import wx
import random

app = wx.App(False)
w,h = wx.GetDisplaySize()
# w = 1024
# h = 600
space = 10
alpha = .5
ft = cv2.freetype.createFreeType2()
ft.loadFontData(fontFileName='Helvetica.ttf',id=0)
windName = 'RespGUI'
boxNum = 4
graphNum = 2
prevPoint = list()
currPoint = list()
plotHolder = list()
vals = list()
for i in range(boxNum):
    vals.append(0)

colorHolder = [(255,99,71), (50,205,50), (138,43,226), (255,140,0), (0,191,255)]
for i in range(graphNum):
    plotHolder.append(list())
    prevPoint.append((round(w//4+10*space),round((h//(graphNum*2))+(i*h//graphNum))))
    currPoint.append(list())
valHolder = None

#### Establish axis limits
axisHolder = [5, 30,800,40,1]

#### Establish starting alarm range
alarmHolder = list()
for i in range(len(axisHolder)):
    alarmHolder.append([-axisHolder[i],axisHolder[i]])

#### Establish labels
labelHolder = [['Pressure','Pr','cmH2O'],
         ['Flow','Flow','L/min'],
         ['Tidal Vol','TV','mL'],
         ['Min Vol','MV','L/min']]

#### Open cv2 window
cv2.namedWindow(windName)

#### Build GUI screen
frame = np.zeros((h,w,3),'uint8')

#### Plot boxes and as semitransparent layer
overlay = np.copy(frame)
for i in range(boxNum):
    cv2.rectangle(overlay,(space,space*(i+1)+((h-6*space)//boxNum)*i),
                  (w//4,space*(i+1)+((h-6*space)//boxNum)*(i+1)),
                  (200,200,200),
                  -1)
cv2.addWeighted(overlay,alpha,frame,1-alpha,0,frame)

#### Put labels in boxes (non-semitransparent)
for i in range(boxNum):
    #Name
    text = labelHolder[i][0] + " (" + labelHolder[i][2] + ")"
    fontHeight = 20
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = (w//4-2*space)-widthText
    textY = space*(i)+((h-6*space)//boxNum)*(i+1)
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)

    #Top limit
    text = str(round(alarmHolder[i][1],1))
    fontHeight = 40
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = 3*space//2
    textY = (h//boxNum*i) + space + space//2*(i==0) + heightText
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)

    #Bottom limit
    text = str(round(alarmHolder[i][0],1))
    fontHeight = 40
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = 3*space//2
    textY = space*(i)+((h-6*space)//boxNum)*(i+1)
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)

#### Establish graphs
for i in range(graphNum):
    # Y-Axis
    cv2.line(frame,((w//4+10*space),(h//graphNum)*i + space),
             ((w//4+10*space),(h//graphNum)*(i+1)-space),
             (255,255,255),
             2)
    # X-Axis
    cv2.line(frame,((w//4+10*space),(h//(graphNum*2))+(i*h//graphNum)),
             (w-space,(h//(graphNum*2))+(i*h//graphNum)),
             (255,255,255),
             2)
    # Tick Marks
    for j in range(10):
        cv2.line(frame,
                 (int((w/4+10*space)+((3*w/4-4*space)/10*(j+1))),(h//(graphNum*2))+(i*h//graphNum)),
                 (int((w/4+10*space)+((3*w/4-4*space)/10*(j+1))),(h//(graphNum*2))+(i*h//graphNum)+space//2),
                 (255,255,255),
                 2)
    #Y-axis labels
    text = labelHolder[i][1]
    fontHeight = 30
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = (w//4+round(5*space))-widthText//2
    textY = (h//(graphNum*2))+(i*h//graphNum)
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)
    text = "(" + labelHolder[i][2] + ")"
    fontHeight = 20
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = (w//4+round(5*space))-widthText//2
    textY = (h//(graphNum*2))+(i*h//graphNum) + round(1.1*heightText)
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)

    #Top axis val
    text = str(axisHolder[i])
    fontHeight = 20
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = int((w//4+9.5*space)-widthText)
    textY = int((i*h//graphNum) + heightText + space)
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)
    #Bottom axis val
    text = str(-axisHolder[i])
    fontHeight = 20
    widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
    textX = int((w//4+9.5*space)-widthText)
    textY = int(((i+1)*h//graphNum) - space)
    ft.putText(frame,text,
               (textX,textY),
               fontHeight,(255,255,255),-1,cv2.LINE_AA,True)

#### Save empty box and graph
boxSave = frame[0:h,0:w//4,:]
graphSave = frame[0:h,w//4:w,:]

#### Open serial port and trial read in 2 lines
ser = mineSerial.mineSerial("/dev/cu.usbmodem142201",115200)
ser.flushInput()

#### Start central clock
startTime = time.time()

while True:
    currTime = time.time() - startTime
    xAxisTime = currTime*((.75*w-4*space)/10)+(w//4+10*space)
    dX = round(xAxisTime) - round(prevPoint[0][0])
    #### Read from serial port, hacky parsing to get space delimited values
    bytesToRead = ser.inWaiting()
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

    #### Redraw GUI from previous frame
    frame = np.zeros((h,w,3),'uint8')
    frame[0:h,0:w//4,:] = boxSave
    frame[0:h,w//4:w,:] = graphSave
    # Remove upcoming data point
    frame[0:h,round(prevPoint[0][0]):round(xAxisTime),:] = np.zeros(frame[0:h,round(prevPoint[0][0]):round(xAxisTime),:].shape,'uint8')

    #### Update numbers in boxes
    for i in range(boxNum):
        #Value
        text = str(round(valHolder[i],1))
        fontHeight = 80
        widthText,heightText = ft.getTextSize(text,fontHeight,-1)[0]
        textX = (w//4-2*space)-widthText
        textY = space*(i+1)+((h-6*space)//boxNum)*i+3*space+fontHeight//2
        if valHolder[i]<alarmHolder[i][1] and valHolder[0]>alarmHolder[i][0]:
            ft.putText(frame,text,
                       (textX,textY),
                       fontHeight,(255,255,255),-1,cv2.LINE_AA,True)
        else:
            ft.putText(frame,text,
                       (textX,textY),
                       fontHeight,(0,0,255),-1,cv2.LINE_AA,True)




    #### Plot graphs
    for i in range(graphNum):

        #### Replot X,Y and ticks
        # Y-Axis
        cv2.line(frame,((w//4+10*space),(h//graphNum)*i + space),
             ((w//4+10*space),(h//graphNum)*(i+1)-space),
             (255,255,255),
             2)

        # X-Axis
        cv2.line(frame,(round(prevPoint[i][0]),(h//(graphNum*2))+(i*h//graphNum)),
                 (round(xAxisTime),(h//(graphNum*2))+(i*h//graphNum)),
                 (255,255,255),
                 2)

        # Tick Marks
        for j in range(10):
            cv2.line(frame,
                     (int((w/4+10*space)+((3*w/4-4*space)/10*(j+1))),(h//(graphNum*2))+(i*h//graphNum)),
                     (int((w/4+10*space)+((3*w/4-4*space)/10*(j+1))),(h//(graphNum*2))+(i*h//graphNum)+space//2),
                     (255,255,255),
                     2)

        # Adjust data to graph axes
        plotHolder[i].append((round(xAxisTime),
                              ((-valHolder[i]/axisHolder[i])*(h//(graphNum*2)-space)+(h//(graphNum*2))+(i*h//graphNum))))
        currPoint[i] = (xAxisTime,
                        (-valHolder[i]/axisHolder[i])*(h//(graphNum*2)-space)+(h//(graphNum*2))+(i*h//graphNum))
        # Plot data
        cv2.polylines(frame,np.int32([plotHolder[i]]),False,colorHolder[i],2)

    #### Save current graph
    graphSave = frame[0:h,w//4:w,:]
    prevPoint = currPoint

    #### Show GUI in full screen
    cv2.imshow(windName,frame)
    cv2.namedWindow(windName,cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(windName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    #### If 10 seconds have elapsed, restart plot collection
    if currTime>10:
        prevPoint = list()
        plotHolder = list()
        for i in range(graphNum):
            prevPoint.append((round(w//4+10*space),round((h//(graphNum*2))+(i*h//graphNum))))
            plotHolder.append(list())
        startTime = time.time()

    #### To stop GUI, press "q" on keyboard
    key = cv2.waitKey(1) & 0xFF
    # time.sleep(.2)
    if key == ord("q"):
        break

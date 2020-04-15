__author__ = 'jonathanschor'

import cv2
import time
import numpy as np
import mineSerial
import wx

class GUIDraw:

    def __init__(self,space,boxNum,graphNum,axisHolder,alarmHolder,labelHolder):

        app = wx.App(False)
        self.w,self.h = wx.GetDisplaySize()
        self.space = space
        self.alpha = .5
        self.boxNum = boxNum
        self.graphNum = graphNum
        self.ft = cv2.freetype.createFreeType2()
        self.ft.loadFontData(fontFileName='Helvetica.ttf',id=0)
        self.colorHolder = [(255,99,71), (50,205,50), (138,43,226), (255,140,0), (0,191,255)]
        self.axisHolder = axisHolder
        self.alarmHolder = alarmHolder
        self.labelHolder = labelHolder
        self.prevPoint = list()
        self.currPoint = list()
        self.plotHolder = list()
        self.valHolder = None
        
    def drawInitialScreen(self):

        w,h = (self.w,self.h)
        space = self.space
        alpha = self.alpha
        boxNum = self.boxNum
        graphNum = self.graphNum
        ft = self.ft
        axisHolder = self.axisHolder
        alarmHolder = self.alarmHolder
        labelHolder = self.labelHolder
        prevPoint = self.prevPoint
        currPoint = self.currPoint
        plotHolder = self.plotHolder

        #### Initialize holders
        for i in range(graphNum):
            plotHolder.append(list())
            prevPoint.append((round(w//4+10*space),round((h//(graphNum*2))+(i*h//graphNum))))
            currPoint.append(list())


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
        self.boxSave,self.graphSave = self.GUISnapshot(frame)
        return frame

    def updateGUI(self,valHolder):
        w,h = (self.w,self.h)
        space = self.space
        prevPoint = self.prevPoint
        startTime = self.startTime
        currPoint = self.currPoint
        plotHolder = self.plotHolder
        boxSave = self.boxSave
        graphSave = self.graphSave
        graphNum = self.graphNum

        currTime = time.time() - startTime
        xAxisTime = currTime*((.75*w-4*space)/10)+(w//4+10*space)

        #### Redraw GUI from previous frame
        frame = self.retrievePreviousFrame(boxSave,graphSave,prevPoint,xAxisTime)

        #### Update numbers in boxes
        frame = self.updateBoxes(frame,valHolder)

        #### Plot graphs
        frame = self.updateGraphs(frame,valHolder,plotHolder,currPoint,prevPoint,xAxisTime)

        #### Save current graph
        _,self.graphSave = self.GUISnapshot(frame)
        self.prevPoint = currPoint

        #### If 10 seconds have elapsed, restart plot collection
        if currTime>10:
            self.prevPoint = list()
            self.plotHolder = list()
            for i in range(graphNum):
                self.prevPoint.append((round(w//4+10*space),round((h//(graphNum*2))+(i*h//graphNum))))
                self.plotHolder.append(list())
            self.updateTime()
        return frame


    def GUISnapshot(self,frame):
        w,h = (self.w,self.h)

        #### Save empty box and graph
        boxSave = frame[0:h,0:w//4,:]
        graphSave = frame[0:h,w//4:w,:]

        return boxSave,graphSave

    def retrievePreviousFrame(self,boxSave,graphSave,prevPoint,xAxisTime):
        w,h = (self.w,self.h)
        #### Redraw GUI from previous frame
        frame = np.zeros((h,w,3),'uint8')
        frame[0:h,0:w//4,:] = boxSave
        frame[0:h,w//4:w,:] = graphSave
        # Remove upcoming data point
        frame[0:h,round(prevPoint[0][0]):round(xAxisTime),:] = np.zeros(frame[0:h,round(prevPoint[0][0]):round(xAxisTime),:].shape,'uint8')
        return frame

    def updateBoxes(self,frame,valHolder):

        w,h = (self.w,self.h)
        space = self.space
        boxNum = self.boxNum
        ft = self.ft
        alarmHolder = self.alarmHolder

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
        return frame

    def updateGraphs(self,frame,valHolder,plotHolder,currPoint,prevPoint,xAxisTime):

        w,h = (self.w,self.h)
        space = self.space
        graphNum = self.graphNum
        axisHolder = self.axisHolder
        colorHolder = self.colorHolder

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
        return frame

    def updateTime(self):
        self.startTime = time.time()
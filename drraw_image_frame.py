# -*- coding: utf-8 -*-
"""
AI Technology Project : 
    Draw Frame Part (Static Image)

Created on Wed Apr 5 2023

@author: Nonpawit Ekburanawat
"""

import cv2 as cv

def click_event(event, x, y, flags, param):
    global draw, a, b
    
    if event == cv.EVENT_LBUTTONDOWN:
        a, b = x, y
        draw = 1
    elif event == cv.EVENT_MOUSEMOVE:
        if draw == 1:
            frame = frame1
            cv.imshow("frame", frame1)
            cv.waitKey(1)
    elif event == cv.EVENT_LBUTTONUP:
        cv.rectangle(frame1, (a, b), (x, y), (0, 0, 255), 1)
        global rect
        rect = a, b, x, y
        draw = 0
        cv.imshow("frame", frame1)
        cv.waitKey(1)
        
global draw, frame1, rect
draw        = 0
cap         = cv.VideoCapture(0)

_, frame1   = cap.read()
_, frame2   = cap.read()

rect        = 0, 0, frame1.shape[1], frame1.shape[0]

cv.imshow("frame", frame1)
cv.setMouseCallback('frame', click_event)
cv.waitKey(0)
cv.destroyAllWindows()
# -*- coding: utf-8 -*-
"""
AI Technology Project : 
    Draw Frame Part (Static Image)

Created on Wed Apr 5 2023

@author: Nonpawit Ekburanawat
"""

import cv2 as cv
import numpy as np

rectangles = []
drawing = False
ix, iy = -1, -1

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img, rectangles

    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            if len(rectangles) > 0:
                # Remove the last rectangle from the list
                rectangles.pop()
            cv.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 1)
            cv.imshow('image', img_copy)

    elif event == cv.EVENT_LBUTTONUP:
        drawing = False
        rectangles.append(((ix, iy), (x, y)))

# Open the default camera
cap = cv.VideoCapture(0)

# Check if camera is opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")

# Capture an image from the camera
_, frame = cap.read()

# Use the captured image as the input source
img = frame

# Create a window and set the mouse callback
cv.namedWindow('image')
cv.setMouseCallback('image', draw_rectangle)

while True:
    # Draw all the rectangles in the list
    img_copy = img.copy()
    for r in rectangles:
        cv.rectangle(img_copy, r[0], r[1], (0, 255, 0), 1)
    cv.imshow('image', img_copy)

    # Wait for key input
    key = cv.waitKey(1) & 0xFF

    # If 'q' is pressed, break the loop
    if key == ord('q'):
        break

# Release the camera capture and destroy all windows
cap.release()
cv.destroyAllWindows()
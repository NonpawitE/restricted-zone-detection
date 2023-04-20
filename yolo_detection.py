# -*- coding: utf-8 -*-
"""
AI Technology Project :
    YOLO Detection Part
    
Created on Wed Apr 19 2023

@author: Siripong Boonsiri
"""

import torch
import cv2   as cv
import numpy as np

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Initialize webcam
cap = cv.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, img = cap.read()

    # Perform object detection
    results = model(img)

    # Convert results.pred to a numpy array
    pred = np.array([x.tolist() for x in results.pred[0]])

    # Get only the results for 'person' class
    person_results = pred[pred[:, 5] == 0]

    # Draw bounding boxes around the detected persons
    for person in person_results:
        x1, y1, x2, y2, conf, cls = person
        cv.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    # Display the output image
    cv.imshow('Output', img)

    # Break the loop if 'q' key is pressed
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv.destroyAllWindows()
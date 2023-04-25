#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Technology Project :
    UI with YOLO demo Part
    
Created on Thu Apr 20 2023

@author: Nonpawit Ekburanawat
"""

import tkinter as     tk
import cv2     as     cv
from   PIL     import Image, ImageTk
from   tkinter import filedialog
import torch
import numpy   as np

## Video Capture Class Handler

class VideoStream:
    def __init__(self, src=None, master=None, canvas=None):
        # OpenCV VideoCapture object to capture frames from the camera or a video file
        self.stream = cv.VideoCapture(src) if src else cv.VideoCapture(0)

        # Set camera properties
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.stream.set(cv.CAP_PROP_AUTOFOCUS,    1)
        self.stream.set(cv.CAP_PROP_AUTO_WB,      1)
        self.stream.set(cv.CAP_PROP_FPS,          30)

        # Initialize variables to store frames and camera status
        (self.grabbed, self.frame)  = self.stream.read()
        self.stopped                = False
        self.master                 = master
        self.canvas                 = canvas
        
        # Intrusion zone variables
        self.zone_coords            = None
        self.drawing                = False
        self.in_zone                = False

    # Method to start video capture and display
    def start(self):
        self.master.after(0, self.update)

    # Method to continuously update frames in the canvas
    def update(self):
        if not self.stopped:
            # Read frames from camera or video file
            (self.grabbed, self.frame) = self.stream.read()
            if self.grabbed:
                self.frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
                
                # Display current video frame to canvas
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                
                # Perform object detection
                results_   = model(self.frame)
                pred_      = np.array([x.tolist() for x in results_.pred[0]])
                persons_   = pred_[pred_[:, 5] == 0]
                
                # Draw bounding boxes around the detected persons and detect intuders
                self.is_intruded = False
                self.canvas.delete("person")
                for person_ in persons_:
                    x1_, y1_, x2_, y2_, conf_, cls_ = person_
                    self.canvas.create_rectangle(x1_, y1_,
                                                 x2_, y2_,
                                                 outline="yellow",
                                                 tag="person")   
                    
                    # Check if person in restricted zone
                    if not self.drawing and \
                           self.zone_coords and \
                           self.__isoverlap([x1_, y1_, x2_, y2_], 
                                            [self.zone_coords[0], 
                                             self.zone_coords[1], 
                                             self.zone_coords[2], 
                                             self.zone_coords[3]]):
                        if not self.in_zone:
                            self.in_zone = True
                            crop         = self.frame[int(y1_):int(y2_), 
                                                      int(x1_):int(x2_)]
                            print("Detected Intruders")
                            cv.imwrite("intruder.jpg", 
                                       cv.cvtColor(crop, cv.COLOR_BGR2RGB))
                
                # Check if rectangle exists
                if self.zone_coords:
                    self.canvas.delete("rect")
                    self.canvas.create_rectangle(self.zone_coords[0], 
                                                 self.zone_coords[1], 
                                                 self.zone_coords[2], 
                                                 self.zone_coords[3], 
                                                 outline="red", 
                                                 tag="rect")

                self.master.after(10, self.update)
            else:
                self.stop()

    # Method to stop video capture and release camera resources
    def stop(self):
        self.stopped = True
        self.stream.release()
        self.__unbind()
        
    # Method to check if 2 rentangle overlapping
    def __isoverlap(self, R1, R2):
        if (R1[0] >= R2[2]) or \
           (R1[2] <= R2[0]) or \
           (R1[3] <= R2[1]) or \
           (R1[1] >= R2[3]):
            return False
        else:
            return True
    
    # Method to unbind mouse button click
    def __unbind(self):
        # Unbind Button Events
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
    
    # Method to bind mouse button click
    def bind(self):
        # Unbind Button Events
        self.canvas.bind("<Button-1>",        self.__start_rect) # On Mouse Click
        self.canvas.bind("<B1-Motion>",       self.__draw_rect)  # On Mouse Move
        self.canvas.bind("<ButtonRelease-1>", self.__stop_rect)  # On Mouse Release

    # Method to start drawing a rectangle on mouse click
    def __start_rect(self, event):
        self.drawing = True
        
        # Initial draw position
        self.zone_coords = [event.x, event.y, event.x, event.y]
    
    # Method to draw rectangle while mouse is down
    def __draw_rect(self, event):
        if self.drawing:
            # Check if mouse is moving
            if self.zone_coords[2:] != [event.x, event.y]:
                # Current mouse position
                self.zone_coords[2:]  = [event.x, event.y]
        
    # Method to stop drawing rectangle
    def __stop_rect(self, event):
        if self.drawing:
            self.drawing          = False
            # Current mouse position
            self.zone_coords[2:]  = [event.x, event.y]
            self.__unbind()
            
    # Method to clear all rectangle
    def clear_rect(self):
        self.zone_coords = None
        self.__unbind()
    
    
## Button Functions

def stop_camera():
    global vs
    if vs:
        vs.stop()
        canvas.delete('all')   
        if str(video_btn['image']) == str(nocam_icn):
            video_btn.config(image=cam_icn) 

def video_button():
    global vs
    
    # Toggle Button Icon
    if str(video_btn['image']) == str(cam_icn):
        vs = VideoStream(master=root, canvas=canvas)
        vs.start()
        video_btn.config(image=nocam_icn)
    elif str(video_btn['image']) == str(nocam_icn):
        stop_camera()

def open_file():
    # Close all previous camera source
    global vs
    stop_camera()
    
    # Ask to open file with video file format
    file_types  = [('Video Files', '*.avi;*.mp4;*.mov;*.mkv')]
    file_path   = filedialog.askopenfilename(filetypes=file_types)
    
    # Check if file path exists
    if file_path:
        # Open Canvas from video file
        vs = VideoStream(file_path, master=root, canvas=canvas)
        vs.start()

def draw_rect():
    global vs
    vs.bind()

def clear_rect():
    global vs
    vs.clear_rect()
    
    
## Initialize Window Settting

vs      = None
root    = tk.Tk()  
root.geometry("1280x850")
root.title("Restricted Zone Detection")
root.resizable(False, False)


## Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')


## Frame Components

cam_icn   = ImageTk.PhotoImage(Image.open('./icons/video.png'))
nocam_icn = ImageTk.PhotoImage(Image.open('./icons/no-video.png'))
open_icn  = ImageTk.PhotoImage(Image.open('./icons/open-file.png'))
rect_icn  = ImageTk.PhotoImage(Image.open('./icons/rectangle.png'))
circ_icn  = ImageTk.PhotoImage(Image.open('./icons/circle.png'))
erase_icn = ImageTk.PhotoImage(Image.open('./icons/erase.png'))

btn_frame = tk.Frame(root)
btn_frame.pack(side=tk.TOP)

# Spacer
spacer    = tk.Frame(btn_frame, 
                     width=10,
                     bd=0,
                     relief="ridge")

# Video Button
video_btn = tk.Button(btn_frame, 
                      image=cam_icn, 
                      height=30, 
                      width=30, 
                      command=lambda:video_button())
video_btn.pack(side=tk.LEFT)

# Open File Button
file_btn  = tk.Button(btn_frame, 
                      image=open_icn, 
                      height=30, 
                      width=30, 
                      command=open_file)
file_btn.pack(side=tk.LEFT)

spacer.pack(side=tk.LEFT)

# Draw Rectangle Button
rect_btn  = tk.Button(btn_frame, 
                      image=rect_icn, 
                      height=30, 
                      width=30, 
                      command=draw_rect)
rect_btn.pack(side=tk.LEFT)

# Draw Circle Button
circ_btn  = tk.Button(btn_frame, 
                      image=circ_icn, 
                      height=30, 
                      width=30, 
                      command=open_file)
circ_btn.pack(side=tk.LEFT)

# Clear Area Button
clear_btn = tk.Button(btn_frame, 
                      image=erase_icn, 
                      height=30, 
                      width=30, 
                      command=clear_rect)
clear_btn.pack(side=tk.LEFT)

# Create Canvas for Video Capture
canvas = tk.Canvas(root, 
                   width=1280, 
                   height=720, 
                   bg='lightgray')
canvas.pack(side=tk.TOP)


## Main Loop & Callback

def on_closing():
    stop_camera()
    root.destroy()

# Callback function that will be called when window is closing
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
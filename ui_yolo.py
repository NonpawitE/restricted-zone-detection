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
        self.zone_coords    = None
        self.drawing        = False
        self.in_zone        = False
        self.detect         = []
        self.view           = False

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
                with torch.no_grad():
                    results_ = model(self.frame)
                
                # Extract results
                boxes_      = results_.xyxy[0].cpu().numpy()
                scores_     = results_.pred[0][:, 4].cpu().numpy()
                labels_     = results_.pred[0][:, -1].cpu().numpy()
                
                # Eliminate result that have confidence score < 0.5
                boxes_  = boxes_[(scores_ > 0.5) & np.isin(labels_, self.detect)]
                labels_ = labels_[(scores_ > 0.5) & np.isin(labels_, self.detect)]
                
                                
                if boxes_.size != 0:
                    # Draw bounding boxes
                    self.is_intruded = False
                    self.canvas.delete("detect")
                    for i in range(len(boxes_)):
                        x1_, y1_, x2_, y2_, _, _ = boxes_[i].astype(np.int32) 
                        
                        if not self.view:
                            self.canvas.create_rectangle(x1_, y1_,
                                                         x2_, y2_,
                                                         outline="yellow",
                                                         tag="detect")  
                            
                        # Check if person in restricted zone
                        if not self.drawing and \
                               self.zone_coords and \
                               self.__isoverlap([x1_, y1_, x2_, y2_], 
                                                [self.zone_coords[0], 
                                                 self.zone_coords[1], 
                                                 self.zone_coords[2], 
                                                 self.zone_coords[3]]):
                           
                            if self.view:
                                self.canvas.create_rectangle(x1_, y1_,
                                                             x2_, y2_,
                                                             outline="yellow",
                                                             tag="detect")  
                    
                # Check if rectangle exists
                if self.zone_coords:
                    self.canvas.delete("rect")
                    self.canvas.create_rectangle(self.zone_coords[0], 
                                                 self.zone_coords[1], 
                                                 self.zone_coords[2], 
                                                 self.zone_coords[3], 
                                                 outline="red", 
                                                 tag="rect", 
                                                 width=3)
    
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
                self.zone_coords[2:] = [event.x, event.y]
        
    # Method to stop drawing rectangle
    def __stop_rect(self, event):
        if self.drawing:
            self.drawing = False
            # Current mouse position
            self.zone_coords[2:] = [event.x, event.y]
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
        vs = None
        canvas.delete('all')
        
        if str(video_btn['image']) == str(nocam_icn):
            video_btn.config(image=cam_icn)
        
        # Reset Button Icon
        ppl_btn.config(image=ppl_icn0) 
        car_btn.config(image=car_icn0) 
        bike_btn.config(image=bike_icn0) 
        view_btn.config(image=move_icn)

            
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
    
    if str(file_btn['image']) == str(open_icn):
        # Ask to open file with video file format
        file_types  = [('Video Files', '*.avi;*.mp4;*.mov;*.mkv')]
        file_path   = filedialog.askopenfilename(filetypes=file_types)
        
        # Check if file path exists
        if file_path:
            # Open Canvas from video file
            vs = VideoStream(file_path, master=root, canvas=canvas)
            vs.start()
            
            file_btn.config(image=stop_icn)
    elif str(file_btn['image']) == str(stop_icn):
        file_btn.config(image=open_icn)

def detect_ppl():
    global vs
    
    if vs:
        if str(ppl_btn['image']) == str(ppl_icn0):
            vs.detect.append(person_idx)
            ppl_btn.config(image=ppl_icn1)
        elif str(ppl_btn['image']) == str(ppl_icn1):
            vs.detect.remove(person_idx)
            ppl_btn.config(image=ppl_icn0) 
    
def detect_car():
    global vs
    
    if vs:
        if str(car_btn['image']) == str(car_icn0):
            vs.detect.append(car_idx)
            car_btn.config(image=car_icn1)
        elif str(car_btn['image']) == str(car_icn1):
            vs.detect.remove(car_idx)
            car_btn.config(image=car_icn0) 
    
def detect_bike():
    global vs
    
    if vs:
        if str(bike_btn['image']) == str(bike_icn0):
            vs.detect.append(bike_idx)
            bike_btn.config(image=bike_icn1)
        elif str(bike_btn['image']) == str(bike_icn1):
            vs.detect.remove(bike_idx)
            bike_btn.config(image=bike_icn0) 

def change_view():
    global vs
    
    if vs:
        if str(view_btn['image']) == str(move_icn):
            vs.view = True
            view_btn.config(image=warn_icn)
        elif str(view_btn['image']) == str(warn_icn):
            vs.view = False
            view_btn.config(image=move_icn)
            
def import_model():
    global model
    stop_camera()
    
    if str(model_btn['image']) == str(impo_icn):
        file_types = [('YOLOv5 Model', '*.pt')]
        file_path  = filedialog.askopenfilename(filetypes=file_types)
        model      = torch.load(file_path).eval()
        
        model_btn.config(image=remo_icn)
    elif str(view_btn['image']) == str(remo_icn):
        model = torch.hub.load('ultralytics/yolov5', 
                               'yolov5s', 
                               pretrained=True).to(device)
        
        model_btn.config(image=impo_icn)

def draw_rect():
    global vs
    if vs:
        vs.bind()

def clear_rect():
    global vs
    if vs:
        vs.clear_rect()
    
    
## Initialize Window Settting
vs      = None
root    = tk.Tk()  
root.geometry("1280x750")
root.title("Restricted Zone Detection")
root.resizable(False, False)


## Initialize PyTorch
device = torch.device('cuda') if torch.cuda.is_available() \
    else torch.device('cpu')

model = torch.hub.load('ultralytics/yolov5', 
                       'yolov5s', 
                       pretrained=True).to(device)

# Get model's object index
person_idx  = list(model.names.values()).index('person')
car_idx     = list(model.names.values()).index('car')
bike_idx    = list(model.names.values()).index('motorcycle')


## Frame Components

# Icons
cam_icn   = ImageTk.PhotoImage(Image.open('./icons/video.png'))
nocam_icn = ImageTk.PhotoImage(Image.open('./icons/no-video.png'))

open_icn  = ImageTk.PhotoImage(Image.open('./icons/open-file.png'))
stop_icn  = ImageTk.PhotoImage(Image.open('./icons/stop.png'))

rect_icn  = ImageTk.PhotoImage(Image.open('./icons/rectangle.png'))
erase_icn = ImageTk.PhotoImage(Image.open('./icons/erase.png'))

ppl_icn0  = ImageTk.PhotoImage(Image.open('./icons/human_off.png'))
ppl_icn1  = ImageTk.PhotoImage(Image.open('./icons/human_on.png'))
car_icn0  = ImageTk.PhotoImage(Image.open('./icons/car_off.png'))
car_icn1  = ImageTk.PhotoImage(Image.open('./icons/car_on.png'))
bike_icn0 = ImageTk.PhotoImage(Image.open('./icons/bike_off.png'))
bike_icn1 = ImageTk.PhotoImage(Image.open('./icons/bike_on.png'))

warn_icn  = ImageTk.PhotoImage(Image.open('./icons/warn.png'))
move_icn  = ImageTk.PhotoImage(Image.open('./icons/move.png'))

impo_icn  = ImageTk.PhotoImage(Image.open('./icons/model_off.png'))
remo_icn  = ImageTk.PhotoImage(Image.open('./icons/model_on.png'))

btn_frame = tk.Frame(root)
btn_frame.pack(side=tk.TOP)

# Video Button
video_btn = tk.Button(btn_frame, 
                      image=cam_icn, 
                      height=30, 
                      width=30, 
                      command=video_button)
video_btn.pack(side=tk.LEFT)

# Open File Button
file_btn  = tk.Button(btn_frame, 
                      image=open_icn, 
                      height=30, 
                      width=30, 
                      command=open_file)
file_btn.pack(side=tk.LEFT)

# Spacer
tk.Frame(btn_frame, 
         width=10,
         bd=0,
         relief="ridge") \
    .pack(side=tk.LEFT)

# Draw Rectangle Button
rect_btn  = tk.Button(btn_frame, 
                      image=rect_icn, 
                      height=30, 
                      width=30, 
                      command=draw_rect)
rect_btn.pack(side=tk.LEFT)

# Clear Area Button
clear_btn = tk.Button(btn_frame, 
                      image=erase_icn, 
                      height=30, 
                      width=30, 
                      command=clear_rect)
clear_btn.pack(side=tk.LEFT)

# Spacer
tk.Frame(btn_frame, 
         width=10,
         bd=0,
         relief="ridge") \
    .pack(side=tk.LEFT)
    
# Detect People Button
ppl_btn   = tk.Button(btn_frame,
                      image=ppl_icn0,
                      height=30, 
                      width=30, 
                      command=detect_ppl)
ppl_btn.pack(side=tk.LEFT)
    
# Detect Car Button
car_btn   = tk.Button(btn_frame,
                      image=car_icn0,
                      height=30, 
                      width=30, 
                      command=detect_car)
car_btn.pack(side=tk.LEFT)
    
# Detect Bike Button
bike_btn  = tk.Button(btn_frame,
                      image=bike_icn0,
                      height=30, 
                      width=30, 
                      command=detect_bike)
bike_btn.pack(side=tk.LEFT)

# Spacer
tk.Frame(btn_frame, 
         width=10,
         bd=0,
         relief="ridge") \
    .pack(side=tk.LEFT)
    
# Change View Button
view_btn  = tk.Button(btn_frame,
                      image=move_icn,
                      height=30, 
                      width=30, 
                      command=change_view)
view_btn.pack(side=tk.LEFT)

# Import Model Button
model_btn = tk.Button(btn_frame,
                      image=impo_icn,
                      height=30, 
                      width=30, 
                      command=import_model)
model_btn.pack(side=tk.LEFT)
    
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
# -*- coding: utf-8 -*-
"""
AI Technology Project :
    Full User Interface Part
    
Created on Tue Apr 18 2023

@author: Nonpawit Ekburanawat
"""

import tkinter as     tk
import cv2     as     cv
from   PIL     import Image, ImageTk
from   tkinter import filedialog

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
        self.rect_coords            = None
        self.canvas                 = canvas
        self.drawing                = False

    # Method to start video capture and display
    def start(self):
        self.master.after(0, self.update)

    # Method to continuously update frames in the canvas
    def update(self):
        if not self.stopped:
            # Read frames from camera or video file
            (self.grabbed, self.frame) = self.stream.read()
            if self.grabbed:
                # Convert frames from BGR to RGB and display them in the canvas
                self.frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
                
                # Display current video frame to canvas
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                
                # Check if rectangle exists
                if self.rect_coords:
                    # Redraw rectangle on every frame
                    self.canvas.delete("rect")
                    self.canvas.create_rectangle(self.rect_coords[0], 
                                                 self.rect_coords[1], 
                                                 self.rect_coords[2], 
                                                 self.rect_coords[3], 
                                                 outline="red", 
                                                 tag="rect")

                # Call update method after 10 milliseconds to update frames
                self.master.after(10, self.update)
            else:
                self.stop()

    # Method to stop video capture and release camera resources
    def stop(self):
        self.stopped = True
        self.stream.release()

    # Method to start drawing a rectangle on mouse click
    def start_rect(self, event):
        self.drawing = True
        
        # Initial draw position
        self.rect_coords = [event.x, event.y, event.x, event.y]
    
    # Method to draw rectangle while mouse is down
    def draw_rect(self, event):
        if self.drawing:
            # Check if mouse is moving
            if self.rect_coords[2:] != [event.x, event.y]:
                # Current mouse position
                self.rect_coords[2:]  = [event.x, event.y]
        
    # Method to stop drawing rectangle
    def stop_rect(self, event):
        if self.drawing:
            self.drawing          = False
            
            # Current mouse position
            self.rect_coords[2:]  = [event.x, event.y]
            
            # Unbind Button Events
            canvas.unbind("<Button-1")
            canvas.unbind("<B1-Motion")
            canvas.unbind("<ButtonRelease-1>")
            
    # Method to clear all rectangle
    def clear_rect(self):
        self.rect_coords = None
    
    
## Button Functions

def stop_camera():
    global vs
    if vs:
        vs.stop()
        canvas.delete("all")    

def start_camera():
    # Close all previous camera source
    global vs
    stop_camera()
    
    # Open Canvas from webcam
    vs = VideoStream(master=root, canvas=canvas)
    vs.start()

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
    # Bind Mouse Events
    canvas.bind("<Button-1>",        vs.start_rect)     # On Mouse Click
    canvas.bind("<B1-Motion>",       vs.draw_rect)      # On Mouse Click + Move
    canvas.bind("<ButtonRelease-1>", vs.stop_rect)      # On Mouse Release

def clear_rect():
    global vs
    vs.clear_rect()
    
## Initialize Window Settting

vs      = None
root    = tk.Tk()  
root.geometry("1280x850")
root.title("Restricted Zone Detection")
root.resizable(False, False)

 
## Frame Components

# Create Canvas for Video Capture
canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()

# Start Video Button
start_button = tk.Button(root, text="Start Camera",    command=start_camera)
start_button.pack(side=tk.LEFT, padx=10, pady=10)

# Stop Video Button
stop_button  = tk.Button(root, text="Stop Camera",     command=stop_camera)
stop_button.pack(side=tk.LEFT, padx=10, pady=10)

# Select Video File Button
open_button  = tk.Button(root, text="Open Video File", command=open_file)
open_button.pack(side=tk.LEFT, padx=10, pady=10)

# Draw Restricted Area Button
draw_button  = tk.Button(root, text="Draw Area",       command=draw_rect)
draw_button.pack(side=tk.LEFT, padx=10, pady=10)

# Clear Restricted Area Button
clear_button = tk.Button(root, text="Clear Area",      command=clear_rect)
clear_button.pack(side=tk.LEFT, padx=10, pady=10)


## Main Loop & Callback

def on_closing():
    stop_camera()
    root.destroy()

# Callback function that will be called when window is closing
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
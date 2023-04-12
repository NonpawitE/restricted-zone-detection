# -*- coding: utf-8 -*-
"""
AI Technology Project :
    UI Part
    
Created on Tue Apr 11 2023

@author: Nonpawit Ekburanawat
"""

import tkinter as     tk
import cv2     as     cv
from   PIL     import Image, ImageTk
from   tkinter import filedialog

## Video Capture Class Handler

class VideoStream:
    def __init__(self, src=None, master=None):
        # OpenCV VideoCapture object to capture frames from the camera or a video file
        self.stream = cv.VideoCapture(src) if src else cv.VideoCapture(0)
        
        # Set camera properties.
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.stream.set(cv.CAP_PROP_AUTOFOCUS,    1)
        self.stream.set(cv.CAP_PROP_AUTO_WB,      1)
        self.stream.set(cv.CAP_PROP_FPS,          30)

        # Initialize variables to store frames and camera status
        (self.grabbed, self.frame)  = self.stream.read()
        self.stopped                = False
        self.master                 = master
        
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
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
                canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                # Call update method after 10 milliseconds to update frames
                self.master.after(10, self.update)
            else:
                # Stop video capture and clear the canvas
                self.stop()
                canvas.delete("all")
        
    # Method to stop video capture and release camera resources
    def stop(self):
        self.stopped = True
        self.stream.release()


## Button Functions

def stop_camera():
    global vs
    # Stop video capture and clear the canvas
    if vs:
        vs.stop()
        canvas.delete("all")

def start_camera():
    global vs
    # Stop previous video
    stop_camera()
    # Open new video from camera
    vs          = VideoStream(master=root)
    vs.start()


def open_file():
    file_path   = filedialog.askopenfilename()
    global vs
    # Stop previous video
    stop_camera()
    # Open new video from selected file
    vs          = VideoStream(file_path, master=root)
    vs.start()


## Initialize Window Settting

root = tk.Tk()  
root.geometry("1400x850")
root.title("Restricted Zone Detection")
root.resizable(False, False)


## Frame Components

# Create Canvas for Video Capture
canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()

# Video Buttons
start_button = tk.Button(root, text="Start Camera",    command=start_camera)
start_button.pack(side=tk.LEFT, padx=10, pady=10)

stop_button  = tk.Button(root, text="Stop Camera",     command=stop_camera)
stop_button.pack(side=tk.LEFT, padx=10, pady=10)

open_button  = tk.Button(root, text="Open Video File", command=open_file)
open_button.pack(side=tk.LEFT, padx=10, pady=10)


## Main Loop & Callback

def on_closing():
    stop_camera()
    root.destroy()

# Callback function that will be called when window is closing
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
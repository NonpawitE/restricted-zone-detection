# -*- coding: utf-8 -*-
"""
AI Technology Project :
    UI Part
    
Created on Tue Apr 11 2023

@author: Nonpawit Ekburanawat
"""

import tkinter as tk
import cv2 as cv
from PIL import Image, ImageTk

# Video Capture Class Handler

class VideoStream:
    def __init__(self, src=0, master=None):
        self.stream                 = cv.VideoCapture(src)
        
        self.stream.set(cv.CAP_PROP_FRAME_WIDTH,  640)
        self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        
        (self.grabbed, self.frame)  = self.stream.read()
        self.stopped                = False
        self.master                 = master
        
    def start(self):
        self.master.after(0, self.update)
        
    def update(self):
        (self.grabbed, self.frame)  = self.stream.read()
        self.frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
        canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        if not self.stopped:
            self.master.after(10, self.update)
        
    def stop(self):
        self.stopped = True

def on_close():
    vs.stop()
    vs.stream.release()
    root.destroy()

# Initialize Window Settting

root = tk.Tk()
root.geometry("1000x700")
root.title("Restricted Zone Detection")
root.resizable(False, False)

# Create Canvas for Video Capture

canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Initialize Video Capture

vs = VideoStream(master=root)
vs.start()

# Start Main Loop

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

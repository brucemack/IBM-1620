# Copyright (c) 2024 Bruce MacKinnon
import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk, ImageFilter
from tkinter import simpledialog
import os 
import util 
import math

in_base_dir = "/home/bruce/host/IBM-1620/f_ald/png"
in_fn = "page_82.png"

canvas = None
tk_image = None
original_image = None
tk_transformed_image = None 
helv16 = None
helv24 = None
image_origin = (0, 0)
canvas_size = (1800, 1000)
scale = 0.7
rotation = 0
rotation_tick = 0.1

anchor_point = (0, 0)
press_1_state = False
hair_point = (0, 0)
tk_hair_objects = []

def update_image():
    global scale, original_image, tk_transformed_image, image_origin
    new_size = (int(original_image.size[0] * scale), int(original_image.size[1] * scale))
    transformed_image = original_image.resize(new_size)
    transformed_image = transformed_image.rotate(angle=rotation)
    # IMPORTANT: DON'T LET THIS GO OUT OF SCOPE!
    tk_transformed_image = ImageTk.PhotoImage(transformed_image)

def redraw_image():
    global tk_image, tk_transformed_image, canvas
    # Undraw from the canvas
    if tk_image is not None:
        canvas.delete(tk_image)
        tk_image = None
    # Draw new version 
    tk_image = canvas.create_image(image_origin[0], image_origin[1], anchor=tk.NW, image=tk_transformed_image)

def redraw_hair():
    global tk_hair_objects, canvas, canvas_size
    # Undraw
    for o in tk_hair_objects:
        canvas.delete(o)
    tk_hair_objects = []
    # Redraw
    tk_hair_objects.append(canvas.create_line((hair_point[0], 0), (hair_point[0], canvas_size[1]), fill="black"))
    tk_hair_objects.append(canvas.create_line((0, hair_point[1]), (canvas_size[0], hair_point[1]), fill="black"))

def on_motion(event):
    global hair_point, press_1_state, anchor_point, image_origin
    hair_point = (event.x, event.y)
    if press_1_state and anchor_point is not None:
        delta_x = event.x - anchor_point[0]
        delta_y = event.y - anchor_point[1]
        image_origin = (image_origin[0] + delta_x, image_origin[1] + delta_y)
        # Reset anchor
        anchor_point = (event.x, event.y)
        redraw_image()
    redraw_hair()

def on_button_press_1(event):
    global anchor_point, press_1_state
    anchor_point = (event.x, event.y)
    press_1_state = True

def on_button_release_1(event):
    global press_1_state
    press_1_state = False

def on_pageup(event):
    global scale
    scale = scale + 0.1
    update_image()
    redraw_image()
    redraw_hair()

def on_pagedown(event):
    global scale
    if scale > 0.1:
        scale = scale - 0.1
    update_image()
    redraw_image()
    redraw_hair()

def on_key_q(event):
    global scale, rotation
    rotation = rotation + rotation_tick
    update_image()
    redraw_image()
    redraw_hair()

def on_key_w(event):
    global scale, rotation
    rotation = rotation - rotation_tick
    update_image()
    redraw_image()
    redraw_hair()

# Setup TK
root = tk.Tk()
root.title("ALD Prod 2")
canvas = tk.Canvas(root, width=canvas_size[0], height=canvas_size[1])
helv16 = TkFont.Font(family='Helvetica', size=16, weight='bold')
helv24 = TkFont.Font(family='Arial', size=24, weight='bold', underline=1)
# Pack the canvas into the Frame.
canvas.pack(expand=tk.YES, fill=tk.BOTH)

canvas.bind('<Motion>', on_motion)
canvas.bind("<ButtonPress-1>", on_button_press_1)
canvas.bind("<ButtonRelease-1>", on_button_release_1)
root.bind("<Prior>", on_pageup)
root.bind("<Next>", on_pagedown)
root.bind("q", on_key_q)
root.bind("w", on_key_w)

# Load image
original_image = Image.open(in_base_dir + "/" + in_fn)

update_image()
redraw_image()

root.mainloop()


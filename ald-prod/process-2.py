# Copyright (c) 2024 Bruce MacKinnon
import os 
import util 
import math
import json
import sys
import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk, ImageOps
from tkinter import simpledialog

in_base_dir = "/home/bruce/host/tmp"

canvas = None
tk_image = None
original_image = None
tk_transformed_image = None 
helv16 = None
helv24 = None
image_origin = (0, 0)
canvas_size = (1800, 1000)
scale = 1.0
rotation_tick = 0.1

anchor_point = (0, 0)
press_1_state = False
hair_point = (0, 0)
tk_hair_objects = []
mark_0 = (0,0)
mark_1 = (0,0)
tk_mark_objects = []

image_type = 0
image_name = None 
image_rotation = 0

key_points = []
# 7 row points x 5 column points
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        row.append((0, 0))
    key_points.append(row)

def estimate_key_point(dp):
    if (mark_1[0] == mark_0[0] or mark_1[1] == mark_0[1]):
        return (0,0)
    adj_x = round((dp[0] - mark_0[0]) * (4 / (mark_1[0] - mark_0[0])))
    adj_y = round((dp[1] - mark_0[1]) * (6 / (mark_1[1] - mark_0[1])))
    return (adj_x, adj_y)

def load_image(n):
    global in_fn, original_image, image_type, image_rotation, image_name, mark_0
    image_name = n
    image_type = 0
    # Load image
    original_image = Image.open(in_base_dir + "/" + image_name + ".jpg")
    # Address the rotation issue
    original_image = ImageOps.exif_transpose(original_image)
    print("Original image size", original_image.size)
    print(original_image.format, original_image.size, original_image.mode)
    # Scale and redraw
    if scale != 1.0:
        new_size = (int(original_image.size[0] * scale), int(original_image.size[1] * scale))
        original_image = original_image.resize(new_size)

def update_image():
    global scale, original_image, tk_transformed_image, image_origin, image_rotation
    #new_size = (int(original_image.size[0] * scale), int(original_image.size[1] * scale))
    #transformed_image = original_image.resize(new_size)
    if image_rotation != 0:
        transformed_image = original_image.rotate(angle=image_rotation)
    else:
        transformed_image = original_image
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

def screen_to_design(point):
    global scale, image_origin
    return ((point[0] - image_origin[0]) / scale, (point[1] - image_origin[1]) / scale)

def design_to_screen(point):
    global scale, image_origin
    return (point[0] * scale + image_origin[0], point[1] * scale + image_origin[1])

def redraw_marks():
    global tk_mark_objects, canvas, canvas_size, mark_0, mark_1, key_points
    # Undraw
    for o in tk_mark_objects:
        canvas.delete(o)
    tk_mark_objects = []

    # Mark0/mark1
    s = design_to_screen(mark_0)
    s = (round(s[0]), round(s[1]))
    r = 30
    x = s[0]
    y = s[1]
    tk_mark_objects.append(canvas.create_oval(x-r,y-r,x+r,y+r, outline="red"))
    s = design_to_screen(mark_1)
    s = (round(s[0]), round(s[1]))
    r = 30
    x = s[0]
    y = s[1]
    tk_mark_objects.append(canvas.create_oval(x-r,y-r,x+r,y+r, outline="red"))

    # Key points
    # 7 row points x 5 column points
    for r in range(0, 7):
        for c in range(0, 5):
            rad = 5
            p = design_to_screen(key_points[r][c])
            x = p[0]
            y = p[1]
            tk_mark_objects.append(canvas.create_oval(x-rad,y-rad,x+rad,y+rad, outline="green", width=2))

def redraw_hair():
    global tk_hair_objects, canvas, canvas_size, image_type
    # Undraw
    for o in tk_hair_objects:
        canvas.delete(o)
    tk_hair_objects = []
    # Redraw
    tk_hair_objects.append(canvas.create_line((hair_point[0], 0), (hair_point[0], canvas_size[1]), fill="black"))
    tk_hair_objects.append(canvas.create_line((0, hair_point[1]), (canvas_size[0], hair_point[1]), fill="black"))

    # Text
    design_point = screen_to_design(hair_point)
    key_point = estimate_key_point(design_point)
    cue = "[" + str(int(design_point[0])) + ", " + str(int(design_point[1])) + "] " + str(key_point[0]) + " " + str(key_point[1])
    tk_hair_objects.append(canvas.create_text(
        hair_point[0] + 20, hair_point[1] + 20, anchor=tk.NW, 
        text=cue, fill='#119999', font=helv16))
    
    if image_type == 0:
        txt = "Normal Logic"
    elif image_type == 1:
        txt = "Text"
    else:
        txt = "Other"
    tk_hair_objects.append(canvas.create_text(
        10, 5, anchor=tk.NW, text=txt, fill="red", font=helv16))

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
        redraw_marks()
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
    redraw_marks()
    redraw_hair()

def on_pagedown(event):
    global scale
    if scale > 0.1:
        scale = scale - 0.1
    update_image()
    redraw_image()
    redraw_marks()
    redraw_hair()

def on_up(event):
    global key_points, hair_point
    design_point = screen_to_design(hair_point)
    key_point = estimate_key_point(design_point)
    a = key_points[key_point[1]][key_point[0]]
    b = (a[0], a[1] - 1)
    key_points[key_point[1]][key_point[0]] = b
    redraw_marks()
    redraw_hair()  

def on_down(event):
    global key_points, hair_point
    design_point = screen_to_design(hair_point)
    key_point = estimate_key_point(design_point)
    a = key_points[key_point[1]][key_point[0]]
    b = (a[0], a[1] + 1)
    key_points[key_point[1]][key_point[0]] = b
    redraw_marks()
    redraw_hair()  

def on_left(event):
    global key_points, hair_point
    design_point = screen_to_design(hair_point)
    key_point = estimate_key_point(design_point)
    a = key_points[key_point[1]][key_point[0]]
    b = (a[0] - 1, a[1])
    key_points[key_point[1]][key_point[0]] = b
    redraw_marks()
    redraw_hair()  

def on_right(event):
    global key_points, hair_point
    design_point = screen_to_design(hair_point)
    key_point = estimate_key_point(design_point)
    a = key_points[key_point[1]][key_point[0]]
    b = (a[0] + 1, a[1])
    key_points[key_point[1]][key_point[0]] = b
    redraw_marks()
    redraw_hair()  

def on_key_q(event):
    global scale, image_rotation
    image_rotation = image_rotation + rotation_tick
    update_image()
    redraw_image()
    redraw_marks()
    redraw_hair()

def on_key_w(event):
    global scale, image_rotation
    image_rotation = image_rotation - rotation_tick
    update_image()
    redraw_image()
    redraw_marks()
    redraw_hair()

def on_f1(event):
    global mark_0
    mark_0 = screen_to_design(hair_point)
    redraw_marks()
    redraw_hair()

def on_f2(event):
    global mark_1
    mark_1 = screen_to_design(hair_point)
    redraw_marks()
    redraw_hair()  

def on_f3(event):
    global key_points, hair_point
    # Figure out which point we are at
    design_point = screen_to_design(hair_point)
    key_point = estimate_key_point(design_point)
    key_points[key_point[1]][key_point[0]] = design_point
    redraw_marks()
    redraw_hair()  

    # Write
    with open("./key_points.txt", "w+") as out:
        for r in range(0, 7):
            for c in range(0, 5):
                s = str(r) + "," + str(c) + "," + str(key_points[r][c][1]) + "," + str(key_points[r][c][0])
                out.write(s + "\n")

def on_escape(event):
    quit()

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
root.bind("<F1>", on_f1)
root.bind("<F2>", on_f2)
root.bind("<F3>", on_f3)
root.bind("<Up>", on_up)
root.bind("<Down>", on_down)
root.bind("<Left>", on_left)
root.bind("<Right>", on_right)

in_fn = sys.argv[1]
load_image(in_fn)

update_image()
redraw_image()
redraw_marks()
redraw_hair()

root.mainloop()

# Copyright (c) 2024 Bruce MacKinnon

import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk
from tkinter import simpledialog
import os 
import util 
import math
import glyphs 

glyph_file_name = "./glyph.txt"
glyph_dict = dict()
canvas = None

pitch_x = 10
pitch_y = 10
offset_x = 10
offset_y = 10

active_rows = 25
active_cols = 20
active_name = None
active_data = []
active_glyph = None

hair_point = (0, 0)

grid_objects = []
hair_objects = []
glyph_objects = []

def redraw_glyph():

    global glyph_objects

    # Clear out the old stuff
    for glyph_object in glyph_objects:
        canvas.delete(glyph_object)
    glyph_objects = []

    for r in range(0, active_rows):
        for c in range(0, active_cols):
            pix = active_data[r * active_cols + c]
            if pix == 0:
                glyph_objects.append(canvas.create_rectangle(offset_x + (c * pitch_x), offset_y + (r * pitch_y), 
                                                             offset_x + ((c + 1) * pitch_x), offset_y + ((r + 1) * pitch_y), 
                                                             fill="black"))

def redraw_grid():

    global grid_objects

    # Clear out the old stuff
    for grid_object in grid_objects:
        canvas.delete(grid_object)
    grid_objects = []

    grid_objects.append(canvas.create_line(offset_x, offset_y, 
                                           offset_x + active_cols * pitch_x, offset_y, fill="red", width=1))
    grid_objects.append(canvas.create_line(offset_x + active_cols * pitch_x, offset_y + 0, 
                                           offset_x + active_cols * pitch_x, offset_y + active_rows * pitch_y, fill="red", width=1))
    grid_objects.append(canvas.create_line(offset_x + active_cols * pitch_x, offset_y + active_rows * pitch_y, 
                                           offset_x + 0, offset_y + active_rows * pitch_y, fill="red", width=1))
    grid_objects.append(canvas.create_line(offset_x + 0, offset_y + active_rows * pitch_y, 
                                           offset_x + 0, offset_y + 0, fill="red", width=1))

def screen_to_design(pt):
    return (round((pt[0] - offset_x) / pitch_x), round((pt[1] - offset_y) / pitch_y))

def redraw_hair():

    global hair_objects

    # Clear out the old stuff
    for hair_object in hair_objects:
        canvas.delete(hair_object)
    hair_objects = []

    dp = screen_to_design(hair_point)
    r = dp[1]
    c = dp[0]
    hair_objects.append(canvas.create_rectangle(offset_x + (c * pitch_x), offset_y + (r * pitch_y), 
                        offset_x + ((c + 1) * pitch_x), offset_y + ((r + 1) * pitch_y), outline="green", width=2))

def on_motion(event):

    global hair_point
    
    hair_point = (event.x, event.y)
    redraw_hair()

def on_button_press_1(event):
    dp = screen_to_design(hair_point)
    if dp[0] < active_cols and dp[1] < active_rows:
        i = dp[1] * active_cols + dp[0]
        if active_data[i] == 0:
            active_data[i] = 255
        else:
            active_data[i] = 0
    redraw_glyph()

def on_f1(event):
    glyphs.save_glyphs(glyph_file_name, glyph_dict)
    print("Saved")

def load_glyph(name):    
    global active_rows, active_cols, active_name, active_data, active_glyph
    active_glyph = glyph_dict[name]
    active_cols = active_glyph.cols
    active_rows = active_glyph.rows
    active_data = active_glyph.data
    active_glyph.print()

glyph_dict = glyphs.load_glyphs(glyph_file_name)
root = tk.Tk()
root.title("ALD Glyph Editor")
canvas = tk.Canvas(root, width=500, height=500)
#helv16 = TkFont.Font(family='Helvetica', size=16, weight='bold')
#helv24 = TkFont.Font(family='Arial', size=24, weight='bold', underline=1)

# Pack the canvas into the Frame.
canvas.pack(expand=tk.YES, fill=tk.BOTH)

#canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind('<Motion>', on_motion)
canvas.bind("<ButtonPress-1>", on_button_press_1)
#canvas.bind("<ButtonRelease-1>", on_button_release_1)
#canvas.bind("<Shift-ButtonPress-1>", on_shift_button_press_1)

#root.bind("<BackSpace>", on_backspace)

#root.bind("<Up>", on_up)
#root.bind("<Down>", on_down)
#root.bind("<Left>", on_left)
#root.bind("<Right>", on_right)

#root.bind("<Shift-Up>", on_shift_up)
#root.bind("<Shift-Down>", on_shift_down)
##root.bind("<Shift-Left>", on_shift_left)
#root.bind("<Shift-Right>", on_shift_right)

root.bind("<F1>", on_f1)
#root.bind("<Escape>", on_escape)
#root.bind("q", on_q_key)
#root.bind("<F2>", on_f2)
#root.bind("<F12>", on_f12)
#root.bind("<F11>", on_f11)

load_glyph("q")
redraw_grid()
redraw_glyph()
redraw_hair()

root.mainloop()




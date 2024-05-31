# Copyright (c) 2024 Bruce MacKinnon
import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk
from tkinter import simpledialog
import os 
import util 
import math

class Glyph:
    
    def __init__(self, name, rows, cols, data):
        self.name = name
        self.rows = rows 
        self.cols = cols 
        self.data = data

    def corr(self, rows, cols, data):

        max_rows = max(rows, self.rows)
        max_cols = max(cols, self.cols)

        total = 0
        tests = 0

        for row in range(0, max_rows):
            for col in range(0, max_cols):

                # Get the sample on each side
                if row < self.rows and col < self.cols:
                    our_pixel = self.data[row * cols + col]
                else:
                    our_pixel = 255

                if row < rows and col < cols:
                    their_pixel = data[row * cols + col]
                else:
                    their_pixel = 255

                # Error
                total = total + (our_pixel - their_pixel) * (our_pixel - their_pixel)
                tests = tests + 1 

        return math.sqrt(total / tests)

glyph_dict = dict()

tk_hair_line_h = None
tk_hair_line_v = None
tk_hair_text = None
tk_image = None
canvas = None 
original_image = None
resized_image = None
tk_photo_image = None
scale = 0.5
scale_step = 0.025
need_resize = True
anchor_point = None
press_1_state = False
# Default marks
mark_type = "A"

# All of these are in screen point terms
image_origin = (0, 0)
canvas_size = (1800, 1200)
hair_point = (canvas_size[0] / 2, canvas_size[1] / 2)
last_point = (0, 0)

# All of these are in design point terms
mark_top_left = (100, 100)
mark_top_right = (200, 100)
mark_bottom_right = (200, 200)
mark_bottom_left = (100, 200)
text_grid_h = None
text_grid_v = None

mark_lines = []
cycle = 0
helv16 = None
helv24 = None

dir_name = "c:/users/bruce/Downloads/temp/f_ald/ilovepdf_split"
file_name = "1620_F_ALD_SN11093-82"

def round_p(p):
    return (round(p[0]), round(p[1]))

def load_marks_if_possible():
    global mark_type, mark_top_left, mark_top_right, mark_bottom_left, mark_bottom_right
    txt_fn = dir_name + "/" + file_name + ".txt"
    if os.path.exists(txt_fn):
        with open(txt_fn) as inf:
            lines = inf.readlines()
            if len(lines) > 0:
                tokens = lines[0].split("\t")
                if len(tokens) >= 9:
                    mark_type = tokens[0]
                    mark_top_left = (float(tokens[1]), float(tokens[2]))
                    mark_top_right = (float(tokens[3]), float(tokens[4]))
                    mark_bottom_right = (float(tokens[5]), float(tokens[6]))
                    mark_bottom_left = (float(tokens[7]), float(tokens[8]))

def store_marks():
    with open(dir_name + "/" + file_name + ".txt", "w+") as of:
        line = mark_type + "\t" + \
               fmt1(mark_top_left[0]) + "\t" + fmt1(mark_top_left[1]) + "\t" + \
               fmt1(mark_top_right[0]) + "\t" + fmt1(mark_top_right[1]) + "\t" + \
               fmt1(mark_bottom_right[0]) + "\t" + fmt1(mark_bottom_right[1]) + "\t" + \
               fmt1(mark_bottom_left[0]) + "\t" + fmt1(mark_bottom_left[1]) + "\t" + \
               "\n"
        of.write(line)    

def adj(point):
    # Determine scale 
    scale = resized_image.size[0] / original_image.size[0]
    return round_p((point[0] * scale + image_origin[0], point[1] * scale + image_origin[1]))

def rev_adj(point):
    # Determine scale 
    scale = resized_image.size[0] / original_image.size[0]
    return (int((point[0] - image_origin[0]) / scale), int(point[1] - image_origin[1]) / scale)

def add_pts(point_a, point_b):
    return (point_a[0] + point_b[0], point_a[1] + point_b[1])

def sector(point):

    tl_d = util.get_distance(point, mark_top_left)
    tr_d = util.get_distance(point, mark_top_right)
    bl_d = util.get_distance(point, mark_bottom_left)
    br_d = util.get_distance(point, mark_bottom_right)

    if tl_d < tr_d and tl_d < bl_d and tl_d < br_d:
        return "tl"
    elif tr_d < tl_d and tr_d < bl_d and tr_d < br_d:
        return "tr"
    elif bl_d < tl_d and bl_d < tr_d and bl_d < br_d:
        return "bl"
    else:
        return "br"

def compute_text_grid():

    global text_grid_h, text_grid_v

    col_count = 127
    row_count = 160

    # Extend up the top marks upwards along the slope of the left and right borders
    mark_top_left_ext = util.get_extended_point(mark_top_left, mark_bottom_left, -405)
    mark_top_right_ext = util.get_extended_point(mark_top_right, mark_bottom_right, -405)
    ticks_l = util.get_intermediate_points(mark_top_left_ext, mark_bottom_left, row_count)
    ticks_r = util.get_intermediate_points(mark_top_right_ext, mark_bottom_right, row_count)
    ticks_t = util.get_intermediate_points(mark_top_left_ext, mark_top_right_ext, col_count)
    ticks_b = util.get_intermediate_points(mark_bottom_left, mark_bottom_right, col_count)

    # Generate the connecting lines
    text_grid_h  = []
    text_grid_v  = []
    for i in range(0, len(ticks_l)):
         text_grid_h.append((ticks_l[i], ticks_r[i]))
    for i in range(0, len(ticks_t)):
         text_grid_v.append((ticks_t[i], ticks_b[i]))

def redraw_marks():

    global shift_y

    for mark_line in mark_lines:
        canvas.delete(mark_line)
    color = "red"

    tl = adj(mark_top_left)
    tr = adj(mark_top_right)
    bl = adj(mark_bottom_left)
    br = adj(mark_bottom_right)

    # Circles
    r = 20
    mark_lines.append(canvas.create_oval(tl[0] - r, tl[1] - r, tl[0] + r, tl[1] + r, outline=color, width=1))
    mark_lines.append(canvas.create_oval(tr[0] - r, tr[1] - r, tr[0] + r, tr[1] + r, outline=color, width=1))
    mark_lines.append(canvas.create_oval(br[0] - r, br[1] - r, br[0] + r, br[1] + r, outline=color, width=1))
    mark_lines.append(canvas.create_oval(bl[0] - r, bl[1] - r, bl[0] + r, bl[1] + r, outline=color, width=1))

    # Outer box
    mark_lines.append(canvas.create_line(tl, tr, fill=color, width=1.5)) 
    mark_lines.append(canvas.create_line(tr, br, fill=color, width=1.5)) 
    mark_lines.append(canvas.create_line(br, bl, fill=color, width=1.5)) 
    mark_lines.append(canvas.create_line(bl, tl, fill=color, width=1.5)) 

    # Draw the additional box lines (red dotted)
    # NOTE: All calculations are done in design coordinates and are adjusted to screen
    # coordinates (using adj()) at the last possible minute.

    # Horizontal lines
    row_count = 8
    ticks_l = util.get_intermediate_points(mark_top_left, mark_bottom_left, row_count)
    ticks_r = util.get_intermediate_points(mark_top_right, mark_bottom_right, row_count)
    for i in range(0, len(ticks_l)):
         mark_lines.append(canvas.create_line(adj(ticks_l[i]), adj(ticks_r[i]), fill=color, width=1, dash=(2, 4)))     
    # Vertical lines
    col_count = 7
    ticks_t = util.get_intermediate_points(mark_top_left, mark_top_right, col_count)
    ticks_b = util.get_intermediate_points(mark_bottom_left, mark_bottom_right, col_count)
    for i in range(0, len(ticks_t)):
         mark_lines.append(canvas.create_line(adj(ticks_t[i]), adj(ticks_b[i]), fill=color, width=1, dash=(2, 4)))     

    # Page mark
    p0 = adj((mark_top_left[0] + 2190, mark_top_left[1] - 360))
    p1 = adj((mark_top_left[0] + 2190 + 220, mark_top_left[1] - 360 + 60))
    mark_lines.append(canvas.create_rectangle(p0[0], p0[1], p1[0], p1[1], outline='blue'))

    # Type indicator
    if mark_type == "A":
        cue = "Logic Diagram Type: "
        cue = cue + "A (Normal)"
    elif mark_type == "B":
        cue = "Logic Diagram Type: "
        cue = cue + "B (7A Type)"
    elif mark_type == "X":
        cue = "NOT A LOGIC DIAGRAM!"
    else:
        cue = "UNKNOWN"
    mark_lines.append(canvas.create_text(50, 50, anchor=tk.NW, text=cue, fill=color, font=helv24))

    # ----- Text Grid ---------------------------------------------------------

    rule_color = "#66dddd"

    # Draw connecting lines
    for i in range(0, len(text_grid_h)):
         mark_lines.append(canvas.create_line(adj(text_grid_h[i][0]), adj(text_grid_h[i][1]), fill=rule_color, width=1))     
    # Vertical lines
    for i in range(0, len(text_grid_v)):
         mark_lines.append(canvas.create_line(adj(text_grid_v[i][0]), adj(text_grid_v[i][1]), fill=rule_color, width=1))     

    # Draw a cell for a test
    #p0 = adj(util.line_intersection(lines_h[0], lines_v[0]))
    #p1 = adj(util.line_intersection(lines_h[1], lines_v[1]))
    #mark_lines.append(canvas.create_rectangle(p0[0], p0[1], p1[0], p1[1], fill="green"))

def redraw_image():
    global tk_image, scale, original_image, resized_image, tk_photo_image, canvas
    global image_origin, need_resize 
    # Undraw 
    if tk_image is not None:
        canvas.delete(tk_image)
        tk_image = None
    if need_resize:
        # Scale and redraw
        new_size = (int(original_image.size[0] * scale), int(original_image.size[1] * scale))
        resized_image = original_image.resize(new_size)
        # IMPORTANT: DON'T LET THIS GO OUT OF SCOPE!
        tk_photo_image = ImageTk.PhotoImage(resized_image)
        need_resize = False
    tk_image = canvas.create_image(image_origin[0], image_origin[1], anchor=tk.NW, image=tk_photo_image)

def redraw_hair():
    global tk_hair_line_h, tk_hair_line_v, canvas, canvas_size, tk_hair_text, hair_point
    # Undraw
    if tk_hair_line_v is not None:
        canvas.delete(tk_hair_line_v)
    if tk_hair_line_h is not None:
        canvas.delete(tk_hair_line_h)
    if tk_hair_text is not None:
        canvas.delete(tk_hair_text)
    # Redraw
    tk_hair_line_v = canvas.create_line((hair_point[0], 0), (hair_point[0], canvas_size[1]), fill="black")
    tk_hair_line_h = canvas.create_line((0, hair_point[1]), (canvas_size[0], hair_point[1]), fill="black")
    
    adj_point = rev_adj(hair_point)

    cue = "[" + str(int(adj_point[0])) + ", " + str(int(adj_point[1])) + "] " + \
        sector(adj_point)
    tk_hair_text = canvas.create_text(hair_point[0] + 20, hair_point[1] + 20, anchor=tk.NW, 
                                      text=cue, fill='#119999', font=helv16)

def set_nearest_mark(design_pt):

    global mark_top_left, mark_top_right, mark_bottom_left, mark_bottom_right

    # Figure out which mark the mouse is close to
    s = sector(design_pt)
    # Adjust the right mark
    if s == "tl":
        mark_top_left = design_pt
    elif s == "tr":
        mark_top_right = design_pt
    elif s == "br":
        mark_bottom_right = design_pt
    else:
        mark_bottom_left = design_pt

def adj_nearest_mark(design_pt, adj):

    global mark_top_left, mark_top_right, mark_bottom_left, mark_bottom_right

    # Figure out which mark the mouse is close to
    s = sector(design_pt)
    print(s, adj)
    # Adjust the right mark
    if s == "tl":
        mark_top_left = add_pts(mark_top_left, adj)
    elif s == "tr":
        mark_top_right = add_pts(mark_top_right, adj)
    elif s == "br":
        mark_bottom_right = add_pts(mark_bottom_right, adj)
    else:
        mark_bottom_left = add_pts(mark_bottom_left, adj)

def screen_pt_to_design_pt(screen_pt):
    return rev_adj(screen_pt)

def on_up(event):
    global hair_point
    hair_point = add_pts(hair_point, (0, -1))
    redraw_hair()

def on_down(event):
    global hair_point
    hair_point = add_pts(hair_point, (0, 1))
    redraw_hair()

def on_left(event):
    global hair_point
    hair_point = add_pts(hair_point, (-1, 0))
    redraw_hair()

def on_right(event):
    global hair_point
    hair_point = add_pts(hair_point, (1, 0))
    redraw_hair()

def on_shift_up(event):
    global hair_point
    adj_nearest_mark(screen_pt_to_design_pt(hair_point), (0, -1))
    compute_text_grid()
    redraw_marks()
    redraw_hair()

def on_shift_down(event):
    global hair_point
    adj_nearest_mark(screen_pt_to_design_pt(hair_point), (0, 1))
    compute_text_grid()
    redraw_marks()
    redraw_hair()

def on_shift_left(event):
    global hair_point
    adj_nearest_mark(screen_pt_to_design_pt(hair_point), (-1, 0))
    compute_text_grid()
    redraw_marks()
    redraw_hair()

def on_shift_right(event):
    global hair_point
    adj_nearest_mark(screen_pt_to_design_pt(hair_point), (1, 0))
    compute_text_grid()
    redraw_marks()
    redraw_hair()

def on_mousewheel(event):
    global scale, need_resize
    if event.delta > 0:
        scale = scale + scale_step
        need_resize = True
    elif event.delta < 0:
        if scale > 0:
            scale = scale - scale_step
            need_resize = True
    redraw_image()
    redraw_marks()
    redraw_hair()

def on_motion(event):

    global last_point, image_origin, anchor_point, moved_while_pressed, hair_point

    last_point = (event.x, event.y)
    hair_point = (event.x, event.y)

    if press_1_state and anchor_point is not None:
        moved_while_pressed = True
        delta_x = event.x - anchor_point[0]
        delta_y = event.y - anchor_point[1]
        image_origin = (image_origin[0] + delta_x, image_origin[1] + delta_y)
        # Reset anchor
        anchor_point = (event.x, event.y)
        redraw_image()
        redraw_marks()
    redraw_hair()

def on_button_press_1(event):
    global anchor_point, press_1_state, moved_while_pressed
    print("Press1", event)
    anchor_point = (event.x, event.y)
    press_1_state = True
    moved_while_pressed = False

def on_button_release_1(event):
    global press_1_state, mark_top_left
    print("Release1", event)
    press_1_state = False

def on_escape(event):
    global cycle, mark_top_left, mark_top_right, mark_bottom_left, mark_bottom_right
    print("Escape")

def on_f1(event):
    set_nearest_mark(screen_pt_to_design_pt(hair_point))
    compute_text_grid()
    redraw_marks()
    redraw_hair()

def on_shift_button_press_1(event):
    print("ShiftPress1", event)

def on_backspace(event):
    print("Backspace", event)

def fmt1(f):
    return str(int(f))

def on_q_key(event):
    print("Writing")
    store_marks()
    quit()

# Changing the diagram type
def on_f2(event):
    global mark_type
    if mark_type == "A":
        mark_type = "B"
    elif mark_type == "B":
        mark_type = "X"
    elif mark_type == "X":
        mark_type = "A"    
    redraw_marks()
    redraw_hair()

# Translates screen coordinates into a text coordinates
def get_text_coordinates(screen_pt):
    design_pt = rev_adj(screen_pt)
    for r in range(0, len(text_grid_h) - 1):
        for c in range(0, len(text_grid_v) - 1):
            # Compute the intersections (upper left, lower right), not paying attention 
            # to any skew
            pt_0 = util.line_intersection(text_grid_v[c], text_grid_h[r])
            pt_1 = util.line_intersection(text_grid_v[c + 1], text_grid_h[r + 1])
            if util.point_in_rect(design_pt, (pt_0, pt_1)):
                return (c, r)
            
    return None

# Checking match
def on_f11(event):
    global text_grid_h, text_grid_v
    # Figure out what cell the hair is in
    pt = get_text_coordinates(hair_point)
    if not pt:
        return
    text_c, text_r = pt
    print("Checking", text_c, text_r)
    # Compute the intersections (upper left, lower right), not paying attention 
    # to any skew
    pt_0 = util.line_intersection(text_grid_v[text_c], text_grid_h[text_r])
    pt_1 = util.line_intersection(text_grid_v[text_c + 1], text_grid_h[text_r + 1])
    # Convert back to screen coordinates
    pt_0_screen = adj(pt_0)
    pt_1_screen = adj(pt_1)

    # Shift around a bit
    lowest_score = 1000
    lowest_gylp = None

    for delta_x in [-3, -2, -1, 0, 1, 2, 3]:
        for delta_y in [-3, -2, -1, 0, 1, 2, 3]:
            # Capture that small part of the image
            pt_0_image = round_p((pt_0_screen[0] - image_origin[0] + delta_x, pt_0_screen[1] - image_origin[1] + delta_y))
            pt_1_image = round_p((pt_1_screen[0] - image_origin[0] + delta_x, pt_1_screen[1] - image_origin[1] + delta_y))
            dx = pt_1_image[0] - pt_0_image[0]
            dy = pt_1_image[1] - pt_0_image[1]
            # Scan the mini-image out of the image
            pixel_data = []
            for y in range(0, dy):
                for x in range(0, dx):
                    pt_image = (pt_0_image[0] + x, pt_0_image[1] + y)
                    pixel_data.append(resized_image.getpixel(pt_image)[0])

            # Now compare to each glyph
            for (key, value) in glyph_dict.items():
                corr = value.corr(dy, dx, pixel_data)
                #print(key, value.corr(dy, dx, pixel_data))
                if corr < lowest_score:
                    lowest_score = corr 
                    lowest_gylp = value


    print("Lowest", lowest_score, lowest_gylp.name)

# Locking in a glyph
def on_f12(event):
    global text_grid_h, text_grid_v
    # Figure out what cell the hair is in
    hair_point_design = rev_adj(hair_point)
    hit = None
    for r in range(0, len(text_grid_h) - 1):
        for c in range(0, len(text_grid_v) - 1):
            # Compute the intersections (upper left, lower right), not paying attention 
            # to any skew
            pt_0 = util.line_intersection(text_grid_v[c], text_grid_h[r])
            pt_1 = util.line_intersection(text_grid_v[c + 1], text_grid_h[r + 1])
            if util.point_in_rect(hair_point_design, (pt_0, pt_1)):
                prompt = "Capture character at [" + str(c) + "," + str(r) + "]"
                typed = simpledialog.askstring("Capture Character", prompt)
                if len(typed) > 0:
                    # Convert back to screen coordinates
                    pt_0_screen = adj(pt_0)
                    pt_1_screen = adj(pt_1)
                    # Capture that small part of the image
                    pt_0_image = round_p((pt_0_screen[0] - image_origin[0], pt_0_screen[1] - image_origin[1]))
                    pt_1_image = round_p((pt_1_screen[0] - image_origin[0], pt_1_screen[1] - image_origin[1]))
                    dx = pt_1_image[0] - pt_0_image[0]
                    dy = pt_1_image[1] - pt_0_image[1]
                    # Scan the mini-image
                    pixel_data = []
                    for y in range(0, dy):
                        for x in range(0, dx):
                            pt_image = (pt_0_image[0] + x, pt_0_image[1] + y)
                            pixel_data.append(resized_image.getpixel(pt_image)[0])
                    # Save the glyph
                    glyph_dict[typed] = Glyph(typed, dy, dx, pixel_data)



                return


load_marks_if_possible()
compute_text_grid()

root = tk.Tk()
root.title("ALD Prod")
canvas = tk.Canvas(root, width=canvas_size[0], height=canvas_size[1])
helv16 = TkFont.Font(family='Helvetica', size=16, weight='bold')
helv24 = TkFont.Font(family='Arial', size=24, weight='bold', underline=1)

# Pack the canvas into the Frame.
canvas.pack(expand=tk.YES, fill=tk.BOTH)

canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind('<Motion>', on_motion)
canvas.bind("<ButtonPress-1>", on_button_press_1)
canvas.bind("<ButtonRelease-1>", on_button_release_1)
canvas.bind("<Shift-ButtonPress-1>", on_shift_button_press_1)

root.bind("<BackSpace>", on_backspace)

root.bind("<Up>", on_up)
root.bind("<Down>", on_down)
root.bind("<Left>", on_left)
root.bind("<Right>", on_right)

root.bind("<Shift-Up>", on_shift_up)
root.bind("<Shift-Down>", on_shift_down)
root.bind("<Shift-Left>", on_shift_left)
root.bind("<Shift-Right>", on_shift_right)

root.bind("<F1>", on_f1)
root.bind("<Escape>", on_escape)
root.bind("q", on_q_key)
root.bind("<F2>", on_f2)
root.bind("<F12>", on_f12)
root.bind("<F11>", on_f11)

imgfn = dir_name + "/" + file_name + ".png"

original_image = Image.open(imgfn)

redraw_image()
redraw_marks()
redraw_hair()

root.mainloop()



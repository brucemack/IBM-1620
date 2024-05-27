# Copyright (c) 2024 Bruce MacKinnon
import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk
import os 

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
image_origin = (0, 0)
need_resize = True
anchor_point = None
press_1_state = False
canvas_size = (1800, 1200)

# Default marks
mark_type = "A"
mark_top_left = (100, 100)
mark_top_right = (200, 100)
mark_bottom_right = (200, 200)
mark_bottom_left = (100, 200)

mark_lines = []
last_point = (0, 0)
cycle = 0
helv16 = None
helv24 = None

dir_name = "c:/users/bruce/Downloads/temp/f_ald/ilovepdf_split"
file_name = "1620_F_ALD_SN11093-82"

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
    return (int(point[0] * scale + image_origin[0]), int(point[1] * scale + image_origin[1]))

def rev_adj(point):
    # Determine scale 
    scale = resized_image.size[0] / original_image.size[0]
    return (int((point[0] - image_origin[0]) / scale), int(point[1] - image_origin[1]) / scale)

def redraw_marks():
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

    # Intermediate lines (horizontal)
    steps = 8
    delta_l = ((bl[0] - tl[0]) / steps, (bl[1] - tl[1]) / steps)
    delta_r = ((br[0] - tr[0]) / steps, (br[1] - tr[1]) / steps)
    point_l = tl
    point_r = tr
    for i in range(0, steps):
        point_l = (point_l[0] + delta_l[0], point_l[1] + delta_l[1])
        point_r = (point_r[0] + delta_r[0], point_r[1] + delta_r[1])
        mark_lines.append(canvas.create_line(point_l, point_r, fill=color, width=1, dash=(2, 4))) 
    # Vertical
    steps = 7
    delta_t = ((tr[0] - tl[0]) / steps, (tr[1] - tl[1]) / steps)
    delta_b = ((br[0] - bl[0]) / steps, (br[1] - bl[1]) / steps)
    point_t = tl
    point_b = bl
    for i in range(0, steps):
        point_t = (point_t[0] + delta_t[0], point_t[1] + delta_t[1])
        point_b = (point_b[0] + delta_b[0], point_b[1] + delta_b[1])
        mark_lines.append(canvas.create_line(point_t, point_b, fill=color, width=1, dash=(2, 4))) 

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

def redraw_hair(point):
    global tk_hair_line_h, tk_hair_line_v, canvas, canvas_size, tk_hair_text
    # Undraw
    if tk_hair_line_v is not None:
        canvas.delete(tk_hair_line_v)
    if tk_hair_line_h is not None:
        canvas.delete(tk_hair_line_h)
    if tk_hair_text is not None:
        canvas.delete(tk_hair_text)
    # Redraw
    tk_hair_line_v = canvas.create_line((point[0], 0), (point[0], canvas_size[1]), fill="black")
    tk_hair_line_h = canvas.create_line((0, point[1]), (canvas_size[0], point[1]), fill="black")
    
    adj_point = rev_adj(point)

    cue = "[" + str(int(adj_point[0])) + ", " + str(int(adj_point[1])) + "]"
    tk_hair_text = canvas.create_text(point[0] + 20, point[1] + 20, anchor=tk.NW, text=cue, fill='#119999',
                                      font=helv16)

def on_up(event):
    global image_y

def on_down(event):
    global image_y

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

def on_motion(event):
    global last_point, image_origin, anchor_point, moved_while_pressed
    last_point = (event.x, event.y)
    if press_1_state and anchor_point is not None:
        moved_while_pressed = True
        delta_x = event.x - anchor_point[0]
        delta_y = event.y - anchor_point[1]
        image_origin = (image_origin[0] + delta_x, image_origin[1] + delta_y)
        # Reset anchor
        anchor_point = (event.x, event.y)
        redraw_image()
        redraw_marks()
    redraw_hair(last_point)

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
    cycle = 0

def on_f1(event):

    global cycle, mark_top_left, mark_top_right, mark_bottom_left, mark_bottom_right

    if cycle == 0:
        mark_top_left = rev_adj((event.x, event.y))
        cycle = 1
    elif cycle == 1:
        mark_top_right = rev_adj((event.x, event.y))
        cycle = 2
    elif cycle == 2:
        mark_bottom_right = rev_adj((event.x, event.y))
        cycle = 3
    elif cycle == 3:
        mark_bottom_left = rev_adj((event.x, event.y))
        cycle = 0

    redraw_marks()
    redraw_hair((event.x, event.y))


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
    redraw_hair((event.x, event.y))

load_marks_if_possible()

root = tk.Tk()
root.title("ALD Prod")
canvas = tk.Canvas(root, width=canvas_size[0], height=canvas_size[1])
helv16 = TkFont.Font(family='Helvetica', size=16, weight='bold')
helv24 = TkFont.Font(family='Arial', size=24, weight='bold', underline=1)

# Pack the canvas into the Frame.
canvas.pack(expand=tk.YES, fill=tk.BOTH)
print(canvas.size())

canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind('<Motion>', on_motion)
canvas.bind("<ButtonPress-1>", on_button_press_1)
canvas.bind("<ButtonRelease-1>", on_button_release_1)
canvas.bind("<Shift-ButtonPress-1>", on_shift_button_press_1)

root.bind("<BackSpace>", on_backspace)
root.bind("<Up>", on_up)
root.bind("<Down>", on_down)
root.bind("<F1>", on_f1)
root.bind("<Escape>", on_escape)
root.bind("q", on_q_key)
root.bind("<F2>", on_f2)

imgfn = dir_name + "/" + file_name + ".png"

original_image = Image.open(imgfn)

redraw_image()
redraw_marks()
redraw_hair((100, 100))

root.mainloop()



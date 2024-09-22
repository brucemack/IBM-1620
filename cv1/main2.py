# Editor
import os
import json 
import math
import tkinter as tk
import tkinter.font as TkFont
import tkinter.simpledialog as TkDialog
from PIL import Image, ImageTk, ImageFilter

image_dir = "pages"
meta_dir = "meta"
helv16 = None
vp_size = (1800, 1200)

img_number = 0
imgfn = None
page_type = 0
page_number = "??.??.??.??"

# View-port adjustments
vp_translation = (0, 0)
vp_scale = 0.5
vp_scale_step = 0.1
vp_rotation = 0

# Overlay adjustments
# Positive translation makes the overlay appear to shift right/down
ol_translation = (0, 0)
ol_scale = 1
ol_scale_step = 0.1
# Positive theta causes the overlay to rotate CW
ol_rotation_theta =  0
ol_rotation_step = (0.05 / 360) * (2.0 * 3.1415926)
# Grid pitch
ol_x_pitch = 19.85
ol_y_pitch = 24.95

# Type
page_type = 0
# Cross-hair
hair_point = (0, 0)
# Mouse-down location 
anchor_point = (0, 0)
# Is mouse down?
press_1_state = False

original_image = None
resized_image = None
tk_photo_image = None
tk_image = None 
# Resizing the image takes some time so we try to avoid that
image_needs_resize = True

canvas = None
tk_hair_text = None
tk_hair_line_h = None
tk_hair_line_v = None

grid_objects = []
hair_objects = []

# Compute block corners
tl_corners = []
br_corners = []
r_labels = [ "A", "B", "C", "D", "E", "F", "G", "H", "?" ]

for r in range(1, 8):
    for c in range(2, 7):
        sc = 19 + (c * 17)
        sr = 16 + (r * 18)
        ec = sc + 5
        er = sr + 7
        sx = sc * ol_x_pitch
        sy = sr * ol_y_pitch
        ex = ec * ol_x_pitch
        ey = er * ol_y_pitch
        tl_corners.append({
            "rc": (r, c),
            "rc2": (r_labels[r], str(c)),
            "coord": (sx, sy)
            }
        )
        br_corners.append({
            "rc": (r, c),
            "rc2": (r_labels[r], str(c)),
            "coord": (ex, ey)
            }
        )

def closest_tl_corner(p):
    min_dist = 9999999
    min_corner = None
    for corner in tl_corners:
        d = dist(p, corner["coord"])
        if d < min_dist:
            min_dist = d 
            min_corner = corner
    return min_corner

def closest_br_corner(p):
    min_dist = 9999999
    min_corner = None
    for corner in br_corners:
        d = dist(p, corner["coord"])
        if d < min_dist:
            min_dist = d 
            min_corner = corner
    return min_corner

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

# Makes a vector from two points
def p2v(p0, p1):
    return (p1[0] - p0[0], p1[1] - p0[1])

# Computes angle between two vectors
def ang(w, v):
    return math.atan2(w[1] * v[0] - w[0] * v[1], w[0] * v[0] + w[1] * v[1])

def deg(r):
    return (r / (2 * 3.1415926)) * 360

def pt_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def pt_add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def pt_mult(a, factor):
    return (a[0] * factor, a[1] * factor)

def pt_rot(a, theta):
    return (a[0] * math.cos(theta) - a[1] * math.sin(theta), 
            a[1] * math.cos(theta) + a[0] * math.sin(theta))

def round_pt(p):
    return (round(p[0]), round(p[1]))

# Translate overlay coordinate to base coordinates
def ol_to_base(ol_pt):
    # Rotate the point.  Positive theta is clockwise
    p1 = pt_rot(ol_pt, ol_rotation_theta)
    # Scale up by multiplication
    p2 = pt_mult(p1, ol_scale)
    # Undo translation since we are rotating around (0, 0) 
    return pt_sub(p2, ol_translation)

# Translate base coordinate to screen coordinates
def base_to_vp(base_pt):
    # Scaling up
    p1 = pt_mult(base_pt, vp_scale)
    # Shifting.
    return pt_add(p1, vp_translation)

# Translate screen coordinates to base coordinates
def vp_to_base(vp_pt):
    # Undo shift
    p1 = pt_sub(vp_pt, vp_translation)
    # Undo scaling
    return pt_mult(p1, 1 / vp_scale)

# Translate base to overlay
def base_to_ol(base_pt):
    # Undo the OL translation by adding back
    p1 = pt_add(base_pt, ol_translation)
    # Undo the OL scale
    p2 = pt_mult(p1, 1 / ol_scale)
    # Undo the OL rotation
    return pt_rot(p2, -ol_rotation_theta)

# It's OK to call this regularly since it watches the needs resize
# flag and only resizes when needed.
def resize_image_if_necessary():
    global image_needs_resize, vp_scale, tk_photo_image
    if image_needs_resize:
        new_size = (int(original_image.size[0] * vp_scale), int(original_image.size[1] * vp_scale))
        resized_image = original_image.resize(new_size)
        # IMPORTANT: DON'T LET THIS GO OUT OF SCOPE!
        tk_photo_image = ImageTk.PhotoImage(resized_image)
        image_needs_resize = False

def redraw_image():
    global canvas, tk_photo_image, tk_image
    # Clean up from before
    if tk_image:
        canvas.delete(tk_image)
        tk_image = None
    # Draw the image, taking into account any scaling/translation of the viewport
    resize_image_if_necessary()
    tk_image = canvas.create_image(vp_translation[0], vp_translation[1], anchor=tk.NW, image=tk_photo_image)

def redraw_ol():

    global grid_objects, canvas, original_image

    for o in grid_objects:
        canvas.delete(o)
    grid_objects.clear()

    start_x = -50 * ol_x_pitch
    start_y = -50 * ol_y_pitch

    y = start_y
    while y < original_image.size[1]:
        start_base_pt = ol_to_base((start_x, y))
        end_base_pt = ol_to_base((original_image.size[0], y))
        start_vp_pt = round_pt(base_to_vp(start_base_pt))
        end_vp_pt = round_pt(base_to_vp(end_base_pt))
        grid_objects.append(canvas.create_line(start_vp_pt, end_vp_pt, fill="#555555"))
        y = y + ol_y_pitch

    x = start_x
    while x < original_image.size[0]:
        start_base_pt = ol_to_base((x, start_y))
        end_base_pt = ol_to_base((x, original_image.size[1]))
        start_vp_pt = round_pt(base_to_vp(start_base_pt))
        end_vp_pt = round_pt(base_to_vp(end_base_pt))
        grid_objects.append(canvas.create_line(start_vp_pt, end_vp_pt, fill="#555555"))
        x = x + ol_x_pitch

    # Mark text areas
    origin_corner = closest_tl_corner((-ol_translation[0], -ol_translation[1]))
    start_ol_pt = origin_corner["coord"]
    start_base_pt = ol_to_base(start_ol_pt)

def redraw_hair():

    global tk_hair_text, tk_hair_line_h, tk_hair_line_v, canvas

    for o in hair_objects:
        canvas.delete(o)
    hair_objects.clear()
    
    # Redraw cross-hairs
    hair_objects.append(canvas.create_line((hair_point[0], 0), (hair_point[0], vp_size[1]), fill="red"))
    hair_objects.append(canvas.create_line((0, hair_point[1]), (vp_size[0], hair_point[1]), fill="red"))

    # Make up the coordinates cue
    base_point = vp_to_base(hair_point)
    cue = "[" + str(int(base_point[0])) + ", " + str(int(base_point[1])) + "] "
    # Compute the OL coordinate
    ol_point = base_to_ol(base_point)
    cue = cue + "  " + str(int(ol_point[0])) + ", " + str(int(ol_point[1]))
    # Corner cue
    min_tl_corner = closest_tl_corner(base_point)
    cue = cue + " " + min_tl_corner["rc2"][1] + min_tl_corner["rc2"][0]

    hair_objects.append(canvas.create_text(hair_point[0] + 20, hair_point[1] + 20, anchor=tk.NW, 
                        text=cue, fill="red", font=helv16))

    # Page type
    type_msg = imgfn
    if page_type == 0:
        type_msg = type_msg + " Normal ALD"
    else:        
        type_msg = type_msg + " Non-Standard"
    hair_objects.append(canvas.create_text(0, 0, anchor=tk.NW,
                        text=type_msg, fill="red", font=helv16))

    # Page number
    hair_objects.append(canvas.create_text(1300, 10, anchor=tk.NW,
                        text=page_number, fill="red", font=helv16))

def on_mousewheel(event):
    global vp_scale, image_needs_resize
    if event.delta > 0:
        vp_scale = vp_scale + vp_scale_step
        image_needs_resize = True
    elif event.delta < 0:
        if vp_scale > 0:
            vp_scale = vp_scale - vp_scale_step
            image_needs_resize = True
    redraw_image()
    redraw_ol()
    redraw_hair()

def on_motion(event):

    global anchor_point, press_1_state, hair_point, vp_translation

    hair_point = (event.x, event.y)

    if press_1_state and anchor_point is not None:
        # Track movement from last anchor
        delta_x = event.x - anchor_point[0]
        delta_y = event.y - anchor_point[1]
        vp_translation = (vp_translation[0] + delta_x, vp_translation[1] + delta_y)
        # Reset anchor
        anchor_point = (event.x, event.y)
        redraw_image()
        redraw_ol()

    redraw_hair()

def on_button_press_1(event):
    global anchor_point, press_1_state
    anchor_point = (event.x, event.y)
    press_1_state = True

def on_button_release_1(event):
    global press_1_state
    press_1_state = False

def on_f3(event):
    global hair_point, ol_translation
    # Establish the center of rotation
    base_pt = vp_to_base(hair_point)
    ol_pt = (0, 0)
    ol_translation = pt_sub(ol_pt, base_pt)
    print(ol_translation)

    redraw_ol()
    redraw_hair()

def on_f4(event):

    global ol_rotation_theta, ol_scale, ol_x_pitch, ol_y_pitch

    # Assume origin is at the top left of a box
    ol_pt_0 = (0, 0)
    base_pt_0 = ol_to_base(ol_pt_0)
    base_pt_1 = vp_to_base(hair_point)

    # Estimate row/col
    base_x_delta = base_pt_1[0] - base_pt_0[0]
    base_y_delta = base_pt_1[1] - base_pt_0[1]
    c = int(base_x_delta / (17 * ol_x_pitch))
    r = int(base_y_delta / (18 * ol_y_pitch))

    # Assume point is at the bottom/right of a box
    ol_pt_1 = (((c * 17) + 5) * ol_x_pitch, ((r * 18) + 7) * ol_y_pitch)

    # Calculate rotation
    base_v = p2v(base_pt_0, base_pt_1)
    ol_v = p2v(ol_pt_0, ol_pt_1)
    ol_rotation_theta = ang(base_v, ol_v)

    redraw_ol()
    redraw_hair()

# CW
def on_f1(event):
    global ol_rotation_theta, ol_rotation_step
    ol_rotation_theta = ol_rotation_theta - ol_rotation_step
    redraw_ol()

# CCW
def on_f2(event):
    global ol_rotation_theta, ol_rotation_step
    ol_rotation_theta = ol_rotation_theta + ol_rotation_step
    redraw_ol()

def on_shift_up(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (0, 1))
    redraw_ol()

def on_shift_down(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (0, -1))
    redraw_ol()

def on_shift_left(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (1, 0))
    redraw_ol()

def on_shift_right(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (-1, 0))
    redraw_ol()

def on_alt_up(event):
    global ol_y_pitch
    ol_y_pitch = ol_y_pitch + 0.05
    redraw_ol()

def on_alt_down(event):
    global ol_y_pitch
    ol_y_pitch = ol_y_pitch - 0.05
    redraw_ol()

def on_alt_left(event):
    global ol_x_pitch
    ol_x_pitch = ol_x_pitch - 0.05
    redraw_ol()

def on_alt_right(event):
    global ol_x_pitch
    ol_x_pitch = ol_x_pitch + 0.05
    redraw_ol()

def on_up(event):
    global hair_point
    hair_point = pt_add(hair_point, (0, -1))
    redraw_hair()

def on_down(event):
    global hair_point
    hair_point = pt_add(hair_point, (0, 1))
    redraw_hair()

def on_left(event):
    global hair_point
    hair_point = pt_add(hair_point, (-1, 0))
    redraw_hair()

def on_right(event):
    global hair_point
    hair_point = pt_add(hair_point, (1, 0))
    redraw_hair()

def load_image(fn):
    global original_image, image_needs_resize
    complete_fn = image_dir + "/" + fn + ".png"
    original_image = Image.open(complete_fn)
    image_needs_resize = True

def save_image_meta(fn):
    complete_fn = meta_dir + "/" + fn + ".json"
    meta = {}
    meta["page_type"] = page_type
    meta["page_number"] = page_number
    meta["ol_translation"] = ol_translation
    meta["ol_scale"] = ol_scale
    meta["ol_rotation_theta"] = ol_rotation_theta
    meta["ol_x_pitch"] = ol_x_pitch
    meta["ol_y_pitch"] = ol_y_pitch
    print(json.dumps(meta))
    with open(complete_fn, "w") as f:
        json.dump(meta, f)

def load_image_meta(fn):
    global ol_translation, ol_scale, ol_rotation_theta, ol_x_pitch, ol_y_pitch, page_type, page_number
    complete_fn = meta_dir + "/" + fn + ".json"
    if os.path.isfile(complete_fn):
        with open(complete_fn) as f:
            meta = json.load(f)
            page_type = meta["page_type"]
            page_number = meta["page_number"]
            ol_translation = meta["ol_translation"]
            ol_scale = meta["ol_scale"]
            ol_rotation_theta = meta["ol_rotation_theta"]
            ol_x_pitch = meta["ol_x_pitch"]
            ol_y_pitch = meta["ol_y_pitch"]
    else:
        print("Unable to file meta for", fn)

def advance(step):
    global img_number, imgfn, page_type, page_number
    img_number = img_number + step
    imgfn = f"ald_{img_number:03d}_bw"
    page_type = 0
    page_number = "??.??.??.??"
    load_image(imgfn)
    load_image_meta(imgfn)
    redraw_image()
    redraw_hair()
    redraw_ol()

def on_return(event):
    save_image_meta(imgfn)
    advance(1)

def on_esc(event):
    advance(1)

def on_backspace(event):
    advance(-1)

def on_space(event):
    global page_type
    if page_type == 0:
        page_type = 1
    else:
        page_type = 0
    redraw_hair()

def on_f5(event):
    global page_number
    page_number = TkDialog.askstring("Page Number", "Enter Page Number")
    redraw_hair()

root = tk.Tk()
root.title("ALD Prod")
canvas = tk.Canvas(root, width=vp_size[0], height=vp_size[1])
# Pack the canvas into the Frame.
canvas.pack(expand=tk.YES, fill=tk.BOTH)
helv16 = TkFont.Font(family='Helvetica', size=16, weight='bold')

canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind('<Motion>', on_motion)
canvas.bind("<ButtonPress-1>", on_button_press_1)
canvas.bind("<ButtonRelease-1>", on_button_release_1)

root.bind("<F1>", on_f1)
root.bind("<F2>", on_f2)
root.bind("<F3>", on_f3)
root.bind("<F4>", on_f4)
root.bind("<F5>", on_f5)
root.bind("<Up>", on_up)
root.bind("<Down>", on_down)
root.bind("<Left>", on_left)
root.bind("<Right>", on_right)
root.bind("<Shift-Up>", on_shift_up)
root.bind("<Shift-Down>", on_shift_down)
root.bind("<Shift-Left>", on_shift_left)
root.bind("<Shift-Right>", on_shift_right)
root.bind("<Return>", on_return)
root.bind("<Escape>", on_esc)
root.bind("<space>", on_space)
root.bind("<BackSpace>", on_backspace)

root.bind("<Alt-Up>", on_alt_up)
root.bind("<Alt-Down>", on_alt_down)
root.bind("<Alt-Left>", on_alt_left)
root.bind("<Alt-Right>", on_alt_right)

# Load
advance(1)
redraw_image()
redraw_hair()
redraw_ol()

root.mainloop()

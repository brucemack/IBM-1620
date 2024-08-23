import math
import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk, ImageFilter

helv16 = None
vp_size = (1800, 1200)

# View-port adjustments
vp_translation = (0, 0)
vp_scale = 1
vp_scale_step = 0.1
vp_rotation = 0

# Overlay adjustments
# Positive translation makes the overlay appear to shift right/down
ol_translation = (0, 0)
ol_scale = 1
ol_scale_step = 0.1
# Positive theta causes the overlay to rotate CW
ol_rotation_theta =  3.1415926 / 8
ol_rotation_step =  (0.1 / 360) * (2.0 * 3.1415926)
# This rotation point is computed in the scaled coordinate system.  For example,
# if the center is (200, 0) and the ol_scale = 2 then the center of rotation 
# appears to be the (400, 0) point in the base coordinate system.
ol_rotation_center = (200, 0)

ol_x_pitch = 19.80
ol_y_pitch = 25

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

# Translate and overlay coordinate to base
def ol_to_base(ol_pt):
    global ol_rotation_center, ol_scale
    # Translate so that the origin is at the center of rotation 
    p1 = pt_sub(ol_pt, ol_rotation_center)
    # Rotate the point 
    p2 = pt_rot(p1, ol_rotation_theta)
    # Re-translate
    p3 = pt_add(p2, ol_rotation_center)
    # Scale
    p4 = pt_mult(p3, ol_scale)
    # Translate 
    p5 = pt_add(p4, ol_translation)
    return p5

def base_to_vp(base_pt):
    p1 = pt_mult(base_pt, vp_scale)
    return pt_add(p1, vp_translation)

def vp_to_base(vp_pt):
    p1 = pt_sub(vp_pt, vp_translation)
    return pt_mult(p1, 1 / vp_scale)

def base_to_ol(base_pt):
    p1 = pt_sub(base_pt, ol_translation)
    p2 = pt_mult(p1, 1 / ol_scale)
    p3 = pt_sub(p2, ol_rotation_center)
    p4 = pt_rot(p3, -ol_rotation_theta)
    p5 = pt_add(p4, ol_rotation_center)
    return p5

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

    y = 0 
    while y < original_image.size[1]:
        start_base_pt = ol_to_base((0, y))
        end_base_pt = ol_to_base((original_image.size[0], y))
        start_vp_pt = round_pt(base_to_vp(start_base_pt))
        end_vp_pt = round_pt(base_to_vp(end_base_pt))
        grid_objects.append(canvas.create_line(start_vp_pt, end_vp_pt, fill="#555555"))
        y = y + ol_y_pitch

    x = 0 
    while x < original_image.size[0]:
        start_base_pt = ol_to_base((x, 0))
        end_base_pt = ol_to_base((x, original_image.size[1]))
        start_vp_pt = round_pt(base_to_vp(start_base_pt))
        end_vp_pt = round_pt(base_to_vp(end_base_pt))
        grid_objects.append(canvas.create_line(start_vp_pt, end_vp_pt, fill="#555555"))
        x = x + ol_x_pitch

def redraw_hair():

    global tk_hair_text, tk_hair_line_h, tk_hair_line_v, canvas

    for o in hair_objects:
        canvas.delete(o)
    hair_objects.clear()
    
    # Redraw
    hair_objects.append(canvas.create_line((hair_point[0], 0), (hair_point[0], vp_size[1]), fill="red"))
    hair_objects.append(canvas.create_line((0, hair_point[1]), (vp_size[0], hair_point[1]), fill="red"))

    base_point = vp_to_base(hair_point)
    cue = "[" + str(int(base_point[0])) + ", " + str(int(base_point[1])) + "] "
    cue = cue + "  " + str(int(base_point[0] / ol_x_pitch)) + ", " + str(int(base_point[1] / ol_y_pitch))
    hair_objects.append(canvas.create_text(hair_point[0] + 20, hair_point[1] + 20, anchor=tk.NW, 
                        text=cue, fill="red", font=helv16))

# Block corners
corners = []

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
        corners.append((sx, sy))
        corners.append((ex, ey))

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

    global last_point, image_origin, anchor_point, press_1_state, hair_point

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
    global hair_point, shift, img_center_point
    pass

def on_f4(event):
    global hair_point, shift, img_center_point, theta
    pass

def on_f1(event):
    global ol_rotation_theta, ol_rotation_step
    ol_rotation_theta = ol_rotation_theta + ol_rotation_step
    redraw_ol()

def on_f2(event):
    global ol_rotation_theta, ol_rotation_step
    ol_rotation_theta = ol_rotation_theta - ol_rotation_step
    redraw_ol()

def on_shift_up(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (0, -1))
    redraw_ol()

def on_shift_down(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (0, 1))
    redraw_ol()

def on_shift_left(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (-1, 0))
    redraw_ol()

def on_shift_right(event):
    global ol_translation
    ol_translation = pt_add(ol_translation, (1, 0))
    redraw_ol()

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
root.bind("<Shift-Up>", on_shift_up)
root.bind("<Shift-Down>", on_shift_down)
root.bind("<Shift-Left>", on_shift_left)
root.bind("<Shift-Right>", on_shift_right)

# Load
imgfn = "pages/ald_126_bw.png"
original_image = Image.open(imgfn)

redraw_image()
redraw_hair()
redraw_ol()

root.mainloop()
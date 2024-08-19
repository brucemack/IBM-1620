import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk, ImageFilter

helv16 = None
canvas_size = (1800, 1200)
image_origin = (0, 0)
last_point = None 
anchor_point = None 
press_1_state = False
hair_point = (0, 0)

scale = 0.5
scale_step = 0.1
original_image = None
resized_image = None
tk_photo_image = None
tk_image = None 
need_resize = True
canvas = None

tk_hair_text = None
tk_hair_line_h = None
tk_hair_line_v = None

def rev_adj(point):
    # Determine scale 
    scale = resized_image.size[0] / original_image.size[0]
    return (round((point[0] - image_origin[0]) / scale), round(point[1] - image_origin[1]) / scale)

def redraw_hair():

    global tk_hair_text, tk_hair_line_h, tk_hair_line_v, canvas, canvas_size
    
    # Undraw
    if tk_hair_line_v is not None:
        canvas.delete(tk_hair_line_v)
    if tk_hair_line_h is not None:
        canvas.delete(tk_hair_line_h)
    if tk_hair_text is not None:
        canvas.delete(tk_hair_text)

    # Redraw
    tk_hair_line_v = canvas.create_line((hair_point[0], 0), (hair_point[0], canvas_size[1]), fill="red")
    tk_hair_line_h = canvas.create_line((0, hair_point[1]), (canvas_size[0], hair_point[1]), fill="red")

    adj_point = rev_adj(hair_point)

    cue = "[" + str(int(adj_point[0])) + ", " + str(int(adj_point[1])) + "] "
    tk_hair_text = canvas.create_text(hair_point[0] + 20, hair_point[1] + 20, anchor=tk.NW, 
                                      text=cue, fill="red", font=helv16)

def redraw_image():
    global canvas, scale, original_image, tk_photo_image, tk_image, need_resize, resized_image

    if tk_image:
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
    redraw_hair()

def on_motion(event):

    global last_point, image_origin, anchor_point, press_1_state, hair_point

    last_point = (event.x, event.y)
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

root = tk.Tk()
root.title("ALD Prod")
canvas = tk.Canvas(root, width=canvas_size[0], height=canvas_size[1])
# Pack the canvas into the Frame.
canvas.pack(expand=tk.YES, fill=tk.BOTH)
helv16 = TkFont.Font(family='Helvetica', size=16, weight='bold')

canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind('<Motion>', on_motion)
canvas.bind("<ButtonPress-1>", on_button_press_1)
canvas.bind("<ButtonRelease-1>", on_button_release_1)

# Load
imgfn = "pages/ald_126_bw.png"
original_image = Image.open(imgfn)

redraw_image()
redraw_hair()

root.mainloop()

# Copyright (c) 2024 Bruce MacKinnon
import tkinter as tk
import tkinter.font as TkFont
from PIL import Image, ImageTk

tk_hair_line_h = None
tk_hair_line_v = None
tk_image = None
canvas = None 
original_image = None
resized_image = None
tk_photo_image = None
scale = 0.2
scale_step = 0.025
image_origin = (0, 0)
need_resize = True
anchor_point = None
press_1_state = False

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
    print(canvas.winfo_reqheight(), canvas.winfo_reqwidth())

def redraw_hair(point):
    global tk_hair_line_h, tk_hair_line_v, canvas
    # Undraw
    if tk_hair_line_v is not None:
        canvas.delete(tk_hair_line_v)
    if tk_hair_line_h is not None:
        canvas.delete(tk_hair_line_h)
    # Redraw
    tk_hair_line_v = canvas.create_line((point[0], 0), (point[0], 1000), fill="red")
    tk_hair_line_h = canvas.create_line((0, point[1]), (1000, point[1]), fill="red")

def on_up(event):
    global image_y
    image_y = image_y + 20
    redraw_image()

def on_down(event):
    global image_y
    image_y = image_y - 20
    redraw_image()

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

def on_motion(event):
    global image_origin, anchor_point
    point = event.x, event.y
    if press_1_state and anchor_point is not None:
        delta_x = event.x - anchor_point[0]
        delta_y = event.y - anchor_point[1]
        image_origin = (image_origin[0] + delta_x, image_origin[1] + delta_y)
        anchor_point = (event.x, event.y)
        redraw_image()

    redraw_hair(point)


def on_button_press_1(event):
    global anchor_point, press_1_state
    print("Press1", event)
    anchor_point = (event.x, event.y)
    press_1_state = True

def on_button_release_1(event):
    global press_1_state
    print("Release1", event)
    press_1_state = False

def on_shift_button_press_1(event):
    print("ShiftPress1", event)

def on_backspace(event):
    print("Backspace", event)



root = tk.Tk()
root.title("ALD Prod")
canvas = tk.Canvas(root, width=1200, height=1200)
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

imgfn = "c:/users/bruce/Downloads/temp/f_ald/ilovepdf_split/1620_F_ALD_SN11093-82.png"
original_image = Image.open(imgfn)

redraw_image()
redraw_hair((100, 100))

#canvas.pack()

root.mainloop()



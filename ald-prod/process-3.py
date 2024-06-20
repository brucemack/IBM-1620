import math
import numpy as np 
import matplotlib.pyplot as plt 
from PIL import Image, ImageTk, ImageFilter, ImageOps

import util

PI = 3.1415926
in_base_dir = "/home/bruce/host/tmp"

# Positive angle = CCW
# +X is right, -Y is up
def trans(pt, center, angle_rad):
    pt2 = (pt[0] - center[0], pt[1] - center[1])
    x = pt2[0] * math.cos(angle_rad) - pt2[1] * math.sin(angle_rad)
    y = pt2[0] * math.sin(angle_rad) + pt2[1] * math.cos(angle_rad)
    return (center[0] + x, center[1] + y)

key_points = []
# 7 row points x 5 column points
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        row.append((0, 0))
    key_points.append(row)

with open("key_points.txt", "r") as pf:
    lines = pf.readlines()
    for line in lines:
        tokens = line.split(",")
        r = int(tokens[0])
        c = int(tokens[1])
        y = float(tokens[2])
        x = float(tokens[3])
        key_points[r][c] = (x, y)

# Compute skew angle 
center = key_points[3][2]
top_center = key_points[0][2]
len = util.line_length(center, top_center)
# Factor that converts grid squares to design units
scale = len / 3
skew_angle = util.line_angle(center, top_center) - (PI / 2)
skew_angle_degrees = math.degrees(skew_angle)
print(top_center, scale, skew_angle_degrees)

# Rotate the actual key points so that everything is square
key_points_rotated = []
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        row.append(trans(key_points[r][c], center, skew_angle))
    key_points_rotated.append(row)

# Make a polar version of the actual key points, relative to the center
key_points_polar = []
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        row.append(util.cart_to_polar(key_points_rotated[r][c], center))
    key_points_polar.append(row)

# Calculate the expected locations of the key points, assuming no distortions
key_points_expected = []
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        expected_pt = (((c - 2) * scale) + center[0], ((r - 3) * scale) + center[1])
        row.append(expected_pt)
    key_points_expected.append(row)

# Calculate the error vectors
key_points_error = []
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        row.append(util.diff_vector(key_points_expected[r][c], key_points[r][c]))
    key_points_error.append(row)

X = []
Y = []
U = []
V = []

# Compute errors
for r in range(0, 7):
    row = ""
    for c in range(0, 5):
        #actual_pt = key_points_rotated[r][c]
        expected_pt = key_points_expected[r][c]
        #error_len = util.line_length(expected_pt, actual_pt)
        #error_angle = math.degrees(util.line_angle(expected_pt, actual_pt))
        error_len = util.line_length((0,0), key_points_error[r][c])
        error_angle = math.degrees(util.line_angle((0,0), key_points_error[r][c]))

        #row = row + str(int(error_angle)) + "\t"
        row = row + str(int(error_len)) + "\t"

        X.append(expected_pt[0])
        Y.append(expected_pt[1])
        # Vector from expected to actual
        #U.append(actual_pt[0] - expected_pt[0])
        #U.append(actual_pt[0] - expected_pt[0])
        U.append(key_points_error[r][c][0])
        V.append(key_points_error[r][c][1])

    print(row)

# Plot a vector field
plt.quiver(X, Y, U, V, color='g', units='xy')
plt.title("Scanner Lense Distortion Vector Field (Y-Reversed)")
plt.xlim(400, 2700) 
plt.ylim(400, 4200) 
plt.grid()
plt.show()

center_pt = center
range_x = (625, 2300)
range_y = ( 900, 3500)

# ----- Adjust An Image --------------------------------------------------------------------

image_name = "IMG_1027"
out_image_name = image_name + "_corr"

image = Image.open(in_base_dir + "/" + image_name + ".jpg")
# Address the rotation issue
image = ImageOps.exif_transpose(image)

# Translate to black and white
image = image.convert("L")
# Rotate the original
#image = image.rotate(-skew_angle_degrees)

# Make a new image 
#new_w = range_x[1] - range_x[0]
#new_h = range_y[1] - range_y[0]
new_image = Image.new("L", image.size)

# Deform
for y in range(0, image.size[1]):
    for x in range(0, image.size[0]):
        grid_pt = util.image_pt_to_grid((x, y), key_points_expected[0][0], scale)
        #image_pt_polar = util.get_interpolated_value_2d(7, 5, key_points_polar, grid_pt)
        image_error = util.get_interpolated_value_2d(7, 5, key_points_error, grid_pt)
        # Convert the interpolated polar coordinate back to cartesian
        #image_pt = util.polar_to_cart(image_pt_polar, center_pt)
        # Pull a pixel out of the original image 
        adj_x = round(x + image_error[0])
        adj_y = round(y + image_error[1])
        if adj_x < 0:
            adj_x = 0
        elif adj_x >= image.size[0]:
            adj_x = image.size[0] - 1
        if adj_y < 0:
            adj_y = 0
        elif adj_y >= image.size[1]:
            adj_y = image.size[1] - 1
        p = image.getpixel((adj_x, adj_y))
        # Drop the pixel into the corrected location
        new_image.putpixel((x, y), p)

new_image.save(in_base_dir + "/" + out_image_name + ".jpg")
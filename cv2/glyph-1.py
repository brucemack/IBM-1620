import math
import numpy as np
import cv2 as cv2

img = cv2.imread("../glyphs/b.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Remove noise via blurring
kernel_size = 3
#blur_gray = cv2.medianBlur(gray, kernel_size)
blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

# Invert
#blur_gray = (255 - blur_gray)

# Perform edge detection. We get out a BW image with the edge 
# pixels =255 and the non-edge pixels =0
low_threshold = 50 
high_threshold = 150
edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

# Scan the edge diagram and pick sample points
height, width = edges.shape
print("Edges height, width", height, width)

for y in range(0, height):
    line = ""
    for x in range(0, width):
        # NOTICE: Row index is first, column is second
        if edges[y, x] == 255:
            line = line + "*"
        else:
            line = line + " "
    print(line)

img_final = edges

# Show the image
(h, w) = img_final.shape[:2]
width = 50
r = width / float(w)
dim = (width, int(h * r))
img_final = cv2.resize(img_final, dim, interpolation=cv2.INTER_AREA)

cv2.imshow("output", img_final)
k = cv2.waitKey(0) # Wait for a keystroke in the window


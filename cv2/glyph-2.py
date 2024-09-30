import math
import numpy as np
import cv2 as cv2
import contour

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

img = cv2.imread("../glyphs/d.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Remove noise via blurring
kernel_size = 3
#blur_gray = cv2.medianBlur(gray, kernel_size)
blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
# Invert
blur_gray = (255 - blur_gray)

# Perform edge detection. We get out a BW image with the edge 
# pixels =255 and the non-edge pixels =0
low_threshold = 50 
high_threshold = 150
edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

# Threshold
ret, thresh = cv2.threshold(blur_gray, 127, 255, 0)

# Find countours
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("Contour count", len(contours))

contour.generate_samples(contours, 32)

"""
# Now traverse all contours and distribute sample points
# Number of sample points
n = 32
# The desired distance between two sample points
target_len = total_len / n
work_seg_len = 0
work_seg_rem_len = 0
# The amount of the current target remaining
target_rem_len = target_len

for work_seg in segment_list:
    # Initialize for this segment
    work_seg_len = dist(work_seg[0], work_seg[1])
    work_seg_rem_len = work_seg_len
    # Keeping working along this segment
    while work_seg_rem_len > 0:
"""

cv2.drawContours(img, contours, 0, (0,255,0), 1)

img_final = img

# Show the image
(h, w) = img_final.shape[:2]
width = 50
r = width / float(w)
dim = (width, int(h * r))
img_final = cv2.resize(img_final, dim, interpolation=cv2.INTER_AREA)

cv2.imshow("output", img_final)
k = cv2.waitKey(0) # Wait for a keystroke in the window


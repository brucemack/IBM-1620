import math
import numpy as np
import cv2 as cv2
import contour

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

img = cv2.imread("../glyphs/b.png")
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

sample_points = contour.generate_samples(contours, 16)

# Draw the sample points on the original 
for sample_point in sample_points:
    center = (int(sample_point[0]), int(sample_point[1]))
    cv2.line(img, (center[0] - 1, center[1]), (center[0] + 1, center[1]), (0,255,0), 1)
    cv2.line(img, (center[0], center[1] - 1), (center[0], center[1] + 1), (0,255,0), 1)

img_final = img

# Show the image
(h, w) = img_final.shape[:2]
width = 50
r = width / float(w)
dim = (width, int(h * r))
img_final = cv2.resize(img_final, dim, interpolation=cv2.INTER_AREA)

cv2.imshow("output", img_final)
k = cv2.waitKey(0) # Wait for a keystroke in the window


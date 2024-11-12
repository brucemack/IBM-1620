import math
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2
import contour
from scipy.optimize import linear_sum_assignment

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

def add(p0, p1):
    return (p0[0] + p1[0], p0[1] + p1[1])

def img_to_hist_series(img, sample_point_count):

    # Invert the grey scale image so that the glyph is white and 
    # the background is black
    blur_gray = (255 - img)

    # Threshold to create a binary image
    _, thresh = cv2.threshold(blur_gray, 127, 255, 0)

    # Find countours on the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Create a set of equally-spaced sample points along the countours
    sample_points = contour.generate_samples(contours, sample_point_count)

    # Make a histogram for each point
    result = []
    for sample_point in sample_points:
        H, x_edges, y_edges = contour.generate_shape_context(sample_point, sample_points)
        # (H is not in standard cartesian form apparently)
        H = H.T
        result.append(H)
    
    return result, sample_points

# Computes the cost between two histograms.  Less is better
def compute_cost(histogram_i, histogram_j):
    fi = histogram_i.flatten()
    fj = histogram_j.flatten()
    s = 0
    for k in range(0, len(fi)):
        hi = fi[k]
        hj = fj[k]
        if hi == 0 and hj == 0:
            continue
        s += ((hi - hj) ** 2.0) / (hi + hj)
    return s / 2.0

kernel_size = 3
sample_point_count = 20

# Load prototype image
img_proto = cv2.imread("../glyphs/a.png")
# First element is rows, second is cols, third is color channels
print(img_proto.shape)
gray_proto = cv2.cvtColor(img_proto, cv2.COLOR_BGR2GRAY)
# Remove noise via blurring
blur_gray_proto = cv2.GaussianBlur(gray_proto, (kernel_size, kernel_size), 0)
# Compute the series of histograms for the prototype.  
histograms_proto, sample_points_proto = img_to_hist_series(blur_gray_proto, sample_point_count)

# Load target image
img_target = cv2.imread("demo/target-a.png")
gray_target = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)
# Remove noise via blurring
blur_gray_target = cv2.GaussianBlur(gray_target, (kernel_size, kernel_size), 0)
# Compute the series of histograms for the target
histograms_target, sample_points_target = img_to_hist_series(blur_gray_target, sample_point_count)

cost_size = sample_point_count

# Make a cost matrix.  Rows are the prototype and cols are the target
cost = np.zeros((cost_size, cost_size))

for i in range(0, sample_point_count):
    for j in range(0, sample_point_count):
        cost[i][j] = compute_cost(histograms_proto[i], histograms_target[j])

# TODO: FILL IN DUMMIES

# Optimize to find the least-cost pairing
row_ind, col_ind = linear_sum_assignment(cost)
print("row_ind", row_ind)
print("col_ind", col_ind)
best_cost = cost[row_ind, col_ind].sum()
print("Optimal cost", best_cost)

# Display cost list
for i in range(0, cost_size):
    print(i, cost[row_ind[i], col_ind[i]])

"""
# https://numpy.org/doc/stable/reference/generated/numpy.histogram2d.html
H = histograms_target[0]
# Display 2D histogram
fig = plt.figure(figsize=(7, 3))
ax = fig.add_subplot(131, title='Shape Context Histogram')
# The extent argument makes the axis legends look right
plt.imshow(H, interpolation='nearest', origin='lower')
#        extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]])
plt.show()
"""
# Create a new image that composes the two glyphs
comp_img = np.zeros((img_proto.shape[0], img_proto.shape[1] * 2, img_proto.shape[2]))
# Compose the two images onto the composite
comp_img[0:25,0:20,0:3] = img_proto[0:25,0:20,0:3] / 256
comp_img[0:25,20:40,0:3] = img_target[0:25,0:20,0:3] / 256

"""
# Draw the sample points on the original images
for sample_point in sample_points_proto:
    center = (int(sample_point[0]), int(sample_point[1]))
    cv2.line(comp_img, (center[0] - 1, center[1]), (center[0] + 1, center[1]), (0,255,0), 1)
    cv2.line(comp_img, (center[0], center[1] - 1), (center[0], center[1] + 1), (0,255,0), 1)

for sample_point in sample_points_target:
    center = (int(sample_point[0]), int(sample_point[1]))
    cv2.line(comp_img, (center[0] - 1 + 20, center[1]), (center[0] + 1 + 20, center[1]), (255,255,0), 1)
    cv2.line(comp_img, (center[0] + 20, center[1] - 1), (center[0] + 20, center[1] + 1), (255,255,0), 1)
"""

# Connect
#cv2.line(comp_img, (0,0), (20,20), (0,255,0), 1)

img_final = comp_img

# Show the image
(h, w) = img_final.shape[:2]
width = 800
r = round(width / float(w))
dim = (w * r, h * r)
img_final = cv2.resize(img_final, dim, interpolation=cv2.INTER_AREA)

font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5

i = 0
for sample_point in sample_points_proto:
    center = (int(sample_point[0]), int(sample_point[1]))
    cv2.line(img_final, add((center[0] * r, center[1] * r), (-2, 0)), add((center[0] * r, center[1] * r), (2, 0)), (0,255,0), 1)
    cv2.line(img_final, add((center[0] * r, center[1] * r), (0, -2)), add((center[0] * r, center[1] * r), (0, 2)), (0,255,0), 1)
    cv2.putText(img_final, str(i), (center[0] * r, center[1] * r), font, fontScale, (0,0,255), 1, cv2.LINE_AA)
    i += 1

for sample_point in sample_points_target:
    center = (int(sample_point[0]) + 20, int(sample_point[1]))
    cv2.line(img_final, add((center[0] * r, center[1] * r), (-2, 0)), add((center[0] * r, center[1] * r), (2, 0)), (255,255,0), 1)
    cv2.line(img_final, add((center[0] * r, center[1] * r), (0, -2)), add((center[0] * r, center[1] * r), (0, 2)), (255,255,0), 1)

# Connecting lines
for i in range(0, sample_point_count):
    center0 = (int(sample_points_proto[i][0]), int(sample_points_proto[i][1]))
    center1 = (int(sample_points_target[col_ind[i]][0] + 20), int(sample_points_target[col_ind[i]][1]))
    cv2.line(img_final, (center0[0] * r, center0[1] * r), (center1[0] * r, center1[1] * r), (0,0,255), 1)

cv2.imshow("output", img_final)

k = cv2.waitKey(0) # Wait for a keystroke in the window

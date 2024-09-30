import math
import numpy as np
import cv2 as cv2

img = cv2.imread("../pages/ald_055.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
kernel_size = 5
#blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
blur_gray = cv2.medianBlur(gray, 5)
# Invert
blur_gray = (255 - blur_gray)

#low_threshold = 50 
#high_threshold = 150
#edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

ret, edges = cv2.threshold(blur_gray, 128, 255, cv2.THRESH_BINARY)

# Line detection
rho = 2 # distance resolution in pixels of the Hough grid
theta = (np.pi / 180) / 8 # angular resolution in radians of the Hough grid
threshold = 1200  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 400  # minimum number of pixels making up a line
max_line_gap = 8  # maximum gap in pixels between connectable line segments

# Create a blank to draw lines on
line_image = np.copy(img) * 0  

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
print("Line Count", len(lines))

horz_angles = []

for line in lines:
    for x1, y1, x2, y2 in line:
        cv2.line(line_image,(x1,y1), (x2,y2), (0,255,0), 2)
        delta_x = x2 - x1 
        delta_y = y2 - y1
        theta = math.atan2(delta_y, delta_x)
        theta_d = math.degrees(theta)

        if theta_d > -2 and theta_d < 2:
            print("Horizontal Line", theta_d, delta_x, delta_y)
            horz_angles.append(theta_d)
        elif theta_d > 88 and theta_d < 92:
            print("Vertical Line", theta_d)
            # Convert to a horizontal angle
            horz_angles.append(theta_d - 90)
        elif theta_d > -92 and theta_d < -88:
            print("Vertical Line", theta_d)
            # Convert to a horizontal angle
            horz_angles.append(theta_d + 90)
        else:
            print("ERROR", theta_d)

# Add box around "1620"
pt0 = (2200, 100)
pt1 = (2600, 250)
cv2.rectangle(line_image, pt0, pt1, (255, 255, 0), 5)

# Build the histograms
# Note: edges is right-open, except for the last bin.  edges[0] is the left
# side of bin 0 and edges[1] is the right (open) side.
horz_hist_bin_counts, horz_hist_bin_edges = np.histogram(horz_angles, bins="auto")
print(horz_hist_bin_counts)
print(horz_hist_bin_edges)
# Find max bin
horz_max_bin = np.argmax(horz_hist_bin_counts)
# Assume the angle is the center of max histogram bin
horz_max = (horz_hist_bin_edges[horz_max_bin] + horz_hist_bin_edges[horz_max_bin + 1]) / 2.0

print("Rotation Angle", horz_max)
rot_degrees = horz_max

# Draw the lines on the image
#lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
lines_edges = cv2.addWeighted(img, 1.0, line_image, 0, 0)

# Rotate
image_center = tuple(np.array(lines_edges.shape[1::-1]) / 2)
print("center", image_center)
# Angle is positive for CCW!
rot_mat = cv2.getRotationMatrix2D(image_center, rot_degrees, 1.0)
lines_edges = cv2.warpAffine(lines_edges, rot_mat, lines_edges.shape[1::-1], flags=cv2.INTER_LINEAR)

img_final = lines_edges

# Write the image
cv2.imwrite("./rotated_055.png", img_final)

# Show the image
(h, w) = img_final.shape[:2]
width = 1000
r = width / float(w)
dim = (width, int(h * r))
img_final = cv2.resize(img_final, dim, interpolation=cv2.INTER_AREA)

cv2.imshow("output", img_final)
k = cv2.waitKey(0) # Wait for a keystroke in the window



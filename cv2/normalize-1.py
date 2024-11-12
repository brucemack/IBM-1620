# A bulk normalization process
import os
import math
import numpy as np
import cv2 as cv2

debug_image_width = 800

# Load 1620 logo  search target
target_image = cv2.imread("../glyphs/1620.png")
target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
# This is the UPPER LIMIT for the match condition on the 1620 logo
# NOTE: PAGE 269 is very bad (0.32), thus the generous threshold
target_threshold = 0.33
# This is the specific place where we search for the "1620" logo
crop_origin = (2200, 50)
crop_size = (450, 350)
# Character pitch (approximate)
#ol_x_pitch = 20
ol_x_pitch = 19.85
ol_y_pitch = 25

def normalize(fn):

    img = cv2.imread(fn + ".png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel_size = 5
    blur_gray = cv2.medianBlur(gray, 5)
    # Invert
    blur_gray = (255 - blur_gray)
    # Makea  binary version of the image
    ret, binary_img = cv2.threshold(blur_gray, 128, 255, cv2.THRESH_BINARY)

    # Clear out some areas that we don't want considered for the line detection
    # Clear left
    binary_img[0:binary_img.shape[1], 0:800] = 0
    # Clear right
    binary_img[0:binary_img.shape[1], 2600:binary_img.shape[0]] = 0
    # Clear top
    binary_img[0:500, 0:binary_img.shape[0]] = 0
    # Clear bottom
    binary_img[4300:binary_img.shape[1], 0:binary_img.shape[0]] = 0

    # Line detection
    rho = 2 # distance resolution in pixels of the Hough grid
    theta = (np.pi / 180) / 8 # angular resolution in radians of the Hough grid
    #threshold = 1200  # minimum number of votes (intersections in Hough grid cell)
    threshold = 1000  # minimum number of votes (intersections in Hough grid cell)
    #min_line_length = 400  # minimum number of pixels making up a line
    # Force a longer line
    min_line_length = 800  # minimum number of pixels making up a line
    max_line_gap = 8  # maximum gap in pixels between connectable line segments
    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(binary_img, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)

    # DEBUG: Create a blank to draw lines on 
    line_image = np.copy(img) * 0  

    # Assemble a list of the angles of the lines in the image. This is used
    # to determine the dominate rotation.
    horz_angles = []

    for line in lines:
        for x1, y1, x2, y2 in line:
            # For debug:
            cv2.line(line_image, (x1,y1), (x2,y2), (0,255,0), 2)
            delta_x = x2 - x1 
            delta_y = y2 - y1
            theta = math.atan2(delta_y, delta_x)
            theta_d = math.degrees(theta)

            if theta_d > -2 and theta_d < 2:
                #print("Horizontal Line", theta_d, delta_x, delta_y)
                horz_angles.append(theta_d)
            elif theta_d > 88 and theta_d < 92:
                #print("Vertical Line", theta_d)
                # Convert to a horizontal angle
                horz_angles.append(theta_d - 90)
            elif theta_d > -92 and theta_d < -88:
                #print("Vertical Line", theta_d)
                # Convert to a horizontal angle
                horz_angles.append(theta_d + 90)
            else:
                print("Unexpected line", theta_d)

    # Build the histograms
    # Note: edges is right-open, except for the last bin.  edges[0] is the left
    # side of bin 0 and edges[1] is the right (open) side.
    horz_hist_bin_counts, horz_hist_bin_edges = np.histogram(horz_angles, bins="auto")
    #print(horz_hist_bin_counts)
    #print(horz_hist_bin_edges)
    # Find max bin
    horz_max_bin = np.argmax(horz_hist_bin_counts)
    # Assume the angle is the center of max histogram bin
    rot_degrees = (horz_hist_bin_edges[horz_max_bin] + horz_hist_bin_edges[horz_max_bin + 1]) / 2.0

    # DEBUG: Merge the lines onto the original image
    lines_edges = cv2.addWeighted(img, 1.0, line_image, 1.0, 0)
    # DEBUG: Scale the image
    (h, w) = lines_edges.shape[:2]
    r = debug_image_width / float(w)
    dim = (debug_image_width, int(h * r))
    lines_edges_scaled = cv2.resize(lines_edges, dim, interpolation=cv2.INTER_AREA)
    # DEBUG: Show the scaled image
    cv2.imshow('DEBUG', lines_edges_scaled)
    cv2.waitKey(0)  
    # Window shown waits for any key pressing event
    cv2.destroyAllWindows()

    # Rotate the original image based on the lines analysis
    image_center = tuple(np.array(img.shape[1::-1]) / 2)
    # Make a transformation matrix so that we can fix the original image.
    # Angle is positive for CCW!
    rot_mat = cv2.getRotationMatrix2D(image_center, rot_degrees, 1.0)
    deskewd_img = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    deskewd_img_gray = cv2.cvtColor(deskewd_img, cv2.COLOR_BGR2GRAY)

    # Now re-detect the logo
    # Crop out a piece that should have the "1620" logo in it
    deskewd_img_gray = deskewd_img_gray[crop_origin[1] : crop_origin[1] + crop_size[1], 
                        crop_origin[0] : crop_origin[0] + crop_size[0]]
    # Find the template
    res = cv2.matchTemplate(deskewd_img_gray, target_gray, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # Uncrop
    min_loc = (min_loc[0] + crop_origin[0], min_loc[1] + crop_origin[1])
    #print("Logo start:", min_loc)

    # Shift the image based on the location of the "1620"
    # Nominal location is c=95,r=0.
    # We include a 10x10 character buffer on the left/top just in case
    desired_logo_loc = ((95 + 10) * ol_x_pitch, (0 + 10) * ol_y_pitch)
    shift_delta = (desired_logo_loc[0] - min_loc[0], desired_logo_loc[1] - min_loc[1])
    # Transformation matrix
    M = np.float32([
    	[1, 0, shift_delta[0]],
	    [0, 1, shift_delta[1]]
    ])
    deskewd_shifted_img = cv2.warpAffine(deskewd_img, M, (deskewd_img.shape[1], deskewd_img.shape[0]))

    # Write the image
    cv2.imwrite(fn + "_deskewd.png", deskewd_shifted_img)
    print(fn, "Angle", rot_degrees, "Shift", shift_delta)

    # DEBUG: Crop out the page number from the deskewed/shifted image to see 
    # what it looks like.
    # Page number is at c=108,r=0
    logo_img = deskewd_shifted_img[int((0 + 10) * ol_y_pitch - 5) : int((0 + 10) * ol_y_pitch + 25 + 5), 
            int((108 + 10) * ol_x_pitch - 5) : int((108 + 10) * ol_x_pitch + (20 * 10) + 5) ]
    cv2.imshow('DEBUG ' + fn, logo_img)
    cv2.waitKey(0)  
    # Window shown waits for any key pressing event
    cv2.destroyAllWindows()

base_folder = "../pages"
# NOTE: Page 454 is the last, but we know about a bunch of pages that 
# aren't in standard ALD format
page_range = range(39, 393)

for page_num in page_range:

    in_file_name = base_folder + f"/ald_{page_num:03d}"
    # Load image and determine whether it contains a "1620" marker
    image = cv2.imread(in_file_name + ".png")
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Crop out a piece that should have the "1620" logo in it
    image_gray = image_gray[crop_origin[1] : crop_origin[1] + crop_size[1], 
                            crop_origin[0] : crop_origin[0] + crop_size[0]]
    # Match using the "1620" template.
    res = cv2.matchTemplate(image_gray, target_gray, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    min_loc = (min_loc[0] + crop_origin[0], min_loc[1] + crop_origin[1])

    # Apply a threshold to determine if we have a valid ALD diagram
    if min_val < target_threshold:
        print("YES", in_file_name)
        normalize(in_file_name)
    else:
        print("NO", min_val, page_num)
        #cv2.imshow('Grayscale', image_gray)
        #cv2.waitKey(0)  
        # Window shown waits for any key pressing event
        #cv2.destroyAllWindows()

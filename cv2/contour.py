import math 
import numpy as np

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

# Makes a vector from two points
def p2v(p0, p1):
    return (p1[0] - p0[0], p1[1] - p0[1])

# Computes angle between two vectors
def ang(w, v):
    return math.atan2(w[1] * v[0] - w[0] * v[1], w[0] * v[0] + w[1] * v[1])

def max_dist(ref_point, points):
    max_distance = 0
    for point in points:
        distance = dist(point, ref_point)
        if distance > max_distance: 
            max_distance = distance
    return max_distance

def make_mid_point(start, end, fraction):
    delta_x = (end[0] - start[0]) * fraction 
    delta_y = (end[1] - start[1]) * fraction 
    return (start[0] + delta_x, start[1] + delta_y)

"""
Assumptions:
1. The contour is is not closed (meaning the first and last point
   are not the same).
"""
def generate_samples(contours, n):

    # Compute the total length of all contours so that we
    # can determine the ideal spacing.
    total_len = 0

    for contour in contours:
        previous_point = None
        # Notice that we are adding the first vertex to the end of
        # the list of vertices to ensure a closed contour.
        for segment in list(contour) + [ contour[0] ]:
            point = segment[0]
            if not previous_point is None:
                total_len += dist(previous_point, point)
            previous_point = point

    # Now traverse all contours and distribute sample points.
    # The desired distance between two sample points
    gap_len = total_len / n
    gap_len_used = 0
    sample_points = []

    for contour in contours:

        # Make a list of the segments for this contour. Each segment 
        # is a straight line represented by a tuple made up of the start 
        # point and send point.
        segments = []
        previous_point = None

        # Notice here that we append the first vertex to the end to ensure
        # that we have a closed contour.
        for vertex in list(contour) + [ contour[0] ]:
            if not previous_point is None:
                segments.append((previous_point, vertex[0]))
            previous_point = vertex[0]

        # Process each segment
        for segment in segments:        
            seg_start = segment[0]
            seg_end = segment[1]
            seg_len = dist(seg_start, seg_end)
            seg_len_used = 0
            # Work across the segment, adding sample points along the way
            while seg_len_used < seg_len:
                # We step to the end of the current gap or the end of the 
                # current segment, which ever comes first.
                step = min(seg_len - seg_len_used, gap_len - gap_len_used)
                seg_len_used += step 
                gap_len_used += step 
                # If the gap is consumed then place a sample point and reset 
                # for the next gap.
                if gap_len_used == gap_len:
                    sample_points.append(make_mid_point(seg_start, seg_end, 
                                                        seg_len_used / seg_len))
                    gap_len_used = 0
            
    # If we fell short (due to precision issues) then add one more point
    if len(sample_points) < n:
        sample_points.append((contours[0][0][0][0], contours[0][0][0][1]))
    
    return sample_points

def generate_shape_context(ref_point, sample_points):
    log_r_list = []
    theta_list = []
    for sample_point in sample_points:
        if not (sample_point[0] == ref_point[0] and sample_point[1] == ref_point[1]):
            # Log radius from reference to sample
            log_r_list.append(math.log10(dist(ref_point, sample_point)))
            # Vector from reference point to sample point
            v = p2v(ref_point, sample_point)
            # Angle of the vector from refernce to sample
            theta_list.append(math.atan2(v[1], v[0]))
    # Following Belongie et. all, 12 bins of resolution on theta and 5 on log(r)
    return np.histogram2d(theta_list, log_r_list, [12, 5])

def test_1():

    contours = []
    contour = []
    contour.append([[1,1]])
    contour.append([[1,0]])
    contour.append([[0,0]])
    contours.append(contour)
    assert len(generate_samples(contours, 5)) == 5

    # Two independent contours
    contours = []
    contour = []
    contour.append([[0,0]])
    contour.append([[1,0]])
    contour.append([[1,1]])
    contours.append(contour)
    contour = []
    contour.append([[2,2]])
    contour.append([[3,2]])
    contour.append([[3,3]])
    contours.append(contour)

    print(generate_samples(contours, 5)) 


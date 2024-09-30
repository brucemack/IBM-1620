import math 

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

def make_mid_point(start, end, fraction):
    delta_x = (end[0] - start[0]) * fraction 
    delta_y = (end[1] - start[1]) * fraction 
    return (start[0] + delta_x, start[1] + delta_y)

def generate_samples(contours, n):

    sample_points = []

    # Compute the total length of all contours so that we
    # can determine the ideal spacing.
    total_len = 0
    for contour in contours:
        previous_point = None
        for segment in contour:
            point = segment[0]
            # (x,y)
            # The segment only has one point, so we skip the first one
            if not previous_point is None:
                total_len += dist(previous_point, point)
            previous_point = point

    print("Total len", total_len)                

    # Now traverse all contours and distribute sample points

    # The desired distance between two sample points
    gap_len = total_len / n
    gap_len_used = 0

    for contour in contours:
        previous_point = None
        for segment in contour:
            # The segment only has one point, so we skip the first one
            if not previous_point is None:
                seg_start = previous_point
                seg_end = segment[0]
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
                    # for the next gap
                    if gap_len_used == gap_len:
                        sample_points.append(make_mid_point(seg_start, seg_end, 
                                                            seg_len_used / seg_len))
                        gap_len_used = 0

                    if gap_rem_len <= 0:




            # Prepare for next
            previous_point = segment[0]
        
    """
        # Initialize for this segment
        work_seg_len = dist(work_seg[0], work_seg[1])
        work_seg_rem_len = work_seg_len
        # Keeping working along this segment
        while work_seg_rem_len > 0:
    """

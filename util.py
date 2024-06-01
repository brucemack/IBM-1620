import math

def get_extended_point(start_point, end_point, ext):
    dx = (end_point[0] - start_point[0]) 
    dy = (end_point[1] - start_point[1])
    length = math.sqrt(dx * dx + dy * dy)
    dx = dx / length
    dy = dy / length
    return (start_point[0] + dx * ext, start_point[1] + dy * ext)

def get_intermediate_points(start_point, end_point, count, offset_x = 0, offset_y = 0):
    """
    Takes a starting and ending point and creates count intermediate points,
    covering the start point and the end point
    """
    dx = (end_point[0] - start_point[0]) / count
    dy = (end_point[1] - start_point[1]) / count
    x = start_point[0]
    y = start_point[1]
    result = []
    for i in range(0, count + 1):
        result.append(((x + i * dx)  + offset_x, (y + i * dy) + offset_y))
    return result

def get_distance(point_a, point_b):
    dx = abs(point_b[0] - point_a[0])
    dy = abs(point_b[1] - point_a[1])
    return math.sqrt(dy * dy + dx * dx)


def interpolate_2d(tl, tr, bl, br, row_count, col_count, row, col):
    # Compute the x coordinate
    dx_t = (tr[0] - tl[0]) / col_count
    dx_b = (br[0] - bl[0]) / col_count

def line_intersection(line_0, line_1):

    xdiff = (line_0[0][0] - line_0[1][0], line_1[0][0] - line_1[1][0])
    ydiff = (line_0[0][1] - line_0[1][1], line_1[0][1] - line_1[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]
    div = det(xdiff, ydiff)

    if div == 0:
       raise Exception("Lines do not intersect")

    d = (det(*line_0), det(*line_1))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    return x, y

def point_in_rect(pt, rect):
    return pt[0] >= rect[0][0] and pt[0] <= rect[1][0] and pt[1] >= rect[0][1] and pt[1] <= rect[1][1]


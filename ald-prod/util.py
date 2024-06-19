
import math

# Performs bilinear interpolation assuming a unit square.
def bilinear_interpolation_1u(q00, q01, q10, q11, p):
    # Interpolate in the x direction first
    ix0 = q00 * (1 - p[0]) + q01 * (p[0])
    ix1 = q10 * (1 - p[0]) + q11 * (p[0])
    # Interpolate in the y direction
    return ix0 * (1 - p[1]) + ix1 * (p[1])

# Performs bilinear interpolation assuming a unit square.
# The points are all 2-tuples 
def bilinear_interpolation_1u_2d(q00, q01, q10, q11, p):
    # Interpolate in the x direction first
    ix0 = (q00[0] * (1 - p[0]) + q01[0] * (p[0]), q00[1] * (1 - p[0]) + q01[1] * (p[0]))
    ix1 = (q10[0] * (1 - p[0]) + q11[0] * (p[0]), q10[1] * (1 - p[0]) + q11[1] * (p[0]))
    # Interpolate in the y direction
    return (ix0[0] * (1 - p[1]) + ix1[0] * (p[1]), ix0[1] * (1 - p[1]) + ix1[1] * (p[1]))

# Compute the difference vector from a->b
def diff_vector(a, b):
    return (b[0] - a[0], b[1] - a[1])

def line_length(a, b):
    d_x = b[0] - a[0]
    d_y = b[1] - a[1]
    return math.sqrt(d_x ** 2 + d_y ** 2)

# Computes angle in radians of a vector, relative to the horizontal/right vector.
# -Y is up (per image coordinate system)
def line_angle(a, b):
    d_x = b[0] - a[0]
    # Y axis is upside down
    d_y = -(b[1] - a[1])
    return math.atan2(d_y, d_x)

def image_pt_to_grid(pt, grid_top_left_pt, scale):
    return ((pt[0] - grid_top_left_pt[0]) / scale, (pt[1] - grid_top_left_pt[1]) / scale)

def get_interpolated_value(grid_rows, grid_cols, grid, grid_pt):

    x0 = math.floor(grid_pt[0])
    x1 = int(x0 + 1)
    dx = grid_pt[0] - x0
    y0 = math.floor(grid_pt[1])
    y1 = int(y0 + 1)
    dy = grid_pt[1] - y0

    # Enforce bounds
    if x0 < 0:
        x0 = 0
    elif x0 > grid_cols - 1:
        x0 = grid_cols - 1
    if x1 < 0:
        x1 = 0
    elif x1 > grid_cols - 1:
        x1 = grid_cols - 1
    if y0 < 0:
        y0 = 0
    elif y0 > grid_rows - 1:
        y0 = grid_rows - 1
    if y1 < 0:
        y1 = 0
    elif y1 > grid_rows - 1:
        y1 = grid_rows - 1

    q00 = grid[y0][x0]
    q01 = grid[y0][x1]
    q10 = grid[y1][x0]
    q11 = grid[y1][x1]

    return bilinear_interpolation_1u(q00, q01, q10, q11, (dx, dy))

def get_interpolated_value_2d(grid_rows, grid_cols, grid, grid_pt):

    x0 = math.floor(grid_pt[0])
    x1 = int(x0 + 1)
    dx = grid_pt[0] - x0
    y0 = math.floor(grid_pt[1])
    y1 = int(y0 + 1)
    dy = grid_pt[1] - y0

    # Enforce bounds
    if x0 < 0:
        x0 = 0
    elif x0 > grid_cols - 1:
        x0 = grid_cols - 1
    if x1 < 0:
        x1 = 0
    elif x1 > grid_cols - 1:
        x1 = grid_cols - 1
    if y0 < 0:
        y0 = 0
    elif y0 > grid_rows - 1:
        y0 = grid_rows - 1
    if y1 < 0:
        y1 = 0
    elif y1 > grid_rows - 1:
        y1 = grid_rows - 1

    q00 = grid[y0][x0]
    q01 = grid[y0][x1]
    q10 = grid[y1][x0]
    q11 = grid[y1][x1]

    return bilinear_interpolation_1u_2d(q00, q01, q10, q11, (dx, dy))

# Converts from Cartesian to polar coordinates
# -Y is up (per image coordinate system)
def cart_to_polar(cart_pt, cart_center_pt = (0,0)):
    return (line_length(cart_center_pt, cart_pt), line_angle(cart_center_pt, cart_pt))

# -Y is up (per image coordinate system)
def polar_to_cart(polar_pt, cart_center_pt = (0, 0)):
    x = polar_pt[0] * math.cos(polar_pt[1])
    y = -polar_pt[0] * math.sin(polar_pt[1])
    return (x + cart_center_pt[0], y + cart_center_pt[1])

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


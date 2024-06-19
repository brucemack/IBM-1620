import math

PI = 3.1415926

def pt_diff(a, b):
    return (b[0] - a[0], b[1] - a[1])

def line_length(a, b):
    d_x = b[0] - a[0]
    d_y = b[1] - a[1]
    return math.sqrt(d_x ** 2 + d_y ** 2)

# Positive angle = CCW
# +X is right, +Y is up
def trans(pt, center, angle_rad):
    pt2 = (pt[0] - center[0], pt[1] - center[1])
    x = pt2[0] * math.cos(angle_rad) - pt2[1] * math.sin(angle_rad)
    y = pt2[0] * math.sin(angle_rad) + pt2[1] * math.cos(angle_rad)
    return (center[0] + x, center[1] + y)

key_points = []
# 7 row points x 5 column points
for r in range(0, 7):
    row = []
    for c in range(0, 5):
        row.append((0, 0))
    key_points.append(row)

with open("key_points.txt", "r") as pf:
    lines = pf.readlines()
    for line in lines:
        tokens = line.split(",")
        r = int(tokens[0])
        c = int(tokens[1])
        y = float(tokens[2])
        x = float(tokens[3])
        key_points[r][c] = (x, y)

# Compute skew angle 
center = key_points[3][2]
top_center = key_points[0][2]
len = line_length(center, top_center)
# Factor that converts grid squares to design units
scale = len / 3
dx = center[0] - top_center[0]
skew_angle = math.asin(dx / len)
skew_angle_degrees = skew_angle * (360 / (2 * PI))
#print(top_center, dx, scale, skew_angle_degrees)

bottom_center = key_points[6][2]
len2 = line_length(center, top_center)
scale2 = len2 / 3
dx2 = bottom_center[0] - center[0]
skew_angle2 = math.asin(dx2 / len2)
skew_angle_degrees2 = skew_angle2 * (360 / (2 * PI))
#print(bottom_center, dx2, scale, skew_angle_degrees2)

# Compute deltas
for r in range(0, 7):
    row = ""
    for c in range(0, 5):
        kp = key_points[r][c]
        # Fix skew
        kp2 = trans(kp, center, skew_angle)
        # Compute expected location
        expected_pt = (((c - 2) * scale) + center[0], ((r - 3) * scale) + center[1])
        len = line_length(kp2, expected_pt)
        #print("(" + str(c) + "," + str(r) + ")", kp2, expected_pt)
        #print("(" + str(c) + "," + str(r) + ")", pt_diff(kp2, expected_pt))
        #row = row + str(int(kp2[0] - expected_pt[0])) + "\t"
        #row = row + str(int(kp2[1] - expected_pt[1])) + "\t"
        row = row + str(int(len)) + "\t"

    print(row)






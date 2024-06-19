import util
import math 

def test_1():
    q00 = 1
    q01 = 3
    q10 = 3
    q11 = 5
    p = (0.5, 0.5)
    assert util.bilinear_interpolation_1u(q00, q01, q10, q11, p) == 3

def test_2():
    assert util.diff_vector((0,0), (1,-1)) == (1, -1)
    assert util.line_angle((0, 0), (0, -1)) == math.radians(90)
    assert util.cart_to_polar((0, -1)) == (1, math.radians(90))
    assert util.cart_to_polar((1, -1), (1, 1)) == (2, math.radians(90))

def test_3():
    grid_rows = 2
    grid_cols = 2
    grid = [ [ 1, 2], [ 3, 4] ]
    assert util.get_interpolated_value(grid_rows, grid_cols, grid, (0, 0)) == 1
    assert util.get_interpolated_value(grid_rows, grid_cols, grid, (0.5, 0)) == 1.5
    assert util.get_interpolated_value(grid_rows, grid_cols, grid, (-1, 0)) == 1
    assert util.get_interpolated_value(grid_rows, grid_cols, grid, (5, 5)) == 4

def test_4():
    grid_rows = 2
    grid_cols = 2
    grid = [ [ (1,1), (2,3)], [ (3,3), (4,6)] ]
    assert util.get_interpolated_value_2d(grid_rows, grid_cols, grid, (0, 0)) == (1, 1)
    assert util.get_interpolated_value_2d(grid_rows, grid_cols, grid, (0.5, 0)) == (1.5, 2.0)
    assert util.get_interpolated_value_2d(grid_rows, grid_cols, grid, (-1, 0)) == (1, 1)
    assert util.get_interpolated_value_2d(grid_rows, grid_cols, grid, (5, 5)) == (4, 6)

def test_5():
    p = (100, math.radians(90))
    assert util.polar_to_cart(p, (100, 100)) == (100, 0)
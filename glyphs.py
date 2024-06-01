import math 
import os 

class Glyph:
    
    def __init__(self, name, rows, cols, data):
        self.name = name
        self.rows = rows 
        self.cols = cols 
        self.data = data

    def rmsd(self, other):
        """
        A simplistic root mean squared error between two glyphs
        """
        # We can only scan on the part that both glyphs have in common
        min_rows = min(other.rows, self.rows)
        min_cols = min(other.cols, self.cols)

        # Compute the RMS deviation
        msd = 0
        N = min_rows * min_cols

        for row in range(0, min_rows):
            for col in range(0, min_cols):
                # Get the sample on each side
                self_pixel = self.data[row * self.cols + col]
                other_pixel = other.data[row * other.cols + col]
                msd = msd + ((self_pixel - other_pixel) ** 2)

        return math.sqrt(msd / N)

    def is_all_white(self, threshold = 0):
        for i in range(0, self.rows * self.cols):
            if self.data[i] != 255:
                return False
        return True

    def print(self):
        for row in range(0, self.rows):
            s = ""
            for col in range(0, self.cols):
                self_pixel = self.data[row * self.cols + col]
                if self_pixel == 0:
                    s = s + "*"
                elif self_pixel == 255:
                    s = s + " "
                else: 
                    s = s + "?"
            print(s)

def save_glyphs(out_fn: str, g):
    s = ""
    for _, glyph in g.items():
        s = s + glyph.name
        s = s + "\t"
        s = s + str(glyph.rows)
        s = s + "\t"
        s = s + str(glyph.cols)
        for r in range(0, glyph.rows):
            for c in range(0, glyph.cols):
                s = s + "\t"
                s = s + str(glyph.data[r * glyph.cols + c])
        s = s + "\n"
    with open("./glyph.txt", "w+") as outf:
        outf.write(s)

def load_glyphs(in_fn: str):
    result = dict()
    with open(in_fn) as inf:
        lines = inf.readlines()
        for line in lines:
            tokens = line.split("\t")
            name = tokens[0]
            rows = int(tokens[1])
            cols = int(tokens[2])
            i = 3
            data = []
            for r in range(0, rows):
                for c in range(0, cols):
                    data.append(int(tokens[i]))
                    i = i + 1
            result[name] = Glyph(name, rows, cols, data)
    return result
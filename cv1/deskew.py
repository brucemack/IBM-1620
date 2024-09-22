import skimage as ski
from skimage.color import rgb2gray, rgba2rgb, gray2rgb
from skimage.transform import rotate
from skimage.filters import threshold_otsu

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import median_filter

image_dir = "pages"

def convert(fn):

    print("Working on", fn)

    # Load image and drop the alpha
    i = ski.io.imread(image_dir + "/" + fn + ".png")
    i2 = rgba2rgb(i)
    i3 = rgb2gray(i2)
    # Filter out some noise 
    i3 = median_filter(i3, size=3)

    # Optimal threshold
    thresh = threshold_otsu(i3)
    # Binarize the data
    i3 = i3 > thresh

    # Convert to greyscale RGB
    i3 = 1 * i3
    i4 = gray2rgb(i3)
    i4 *= 255
    i4 = i4.astype(np.uint8)
    # Despeckel
    i4 = median_filter(i4, size=3)

    # Dump
    ski.io.imsave(image_dir + "/" + fn + "_bw.png", i4)

for k in range(1, 455):
    f = f"ald_{k:03d}"
    convert(f)


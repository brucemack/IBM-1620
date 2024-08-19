import skimage as ski
from skimage.color import rgb2gray, rgba2rgb, gray2rgb
from skimage.transform import rotate
from skimage.filters import threshold_otsu

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import median_filter

# Load image and drop the alpha
i = ski.io.imread("pages/ald_126.png")
print(i.shape)

i2 = rgba2rgb(i)
print(i2.shape)

i3 = rgb2gray(i2)
print(i3.shape)
# Filter out some noise 
i3 = median_filter(i3, size=3)

# Optimal threshold
thresh = threshold_otsu(i3)
# Binarize the data
i3 = i3 > thresh
# Compute true count for each row
row_count = np.sum(i3, axis=1)
h = np.histogram(row_count, 100)

plt.hist(h, bins=100)  # arguments are passed to np.histogram

# Convert to greyscale RGB
i3 = 1 * i3
i4 = gray2rgb(i3)
i4 *= 255
i4 = i4.astype(np.uint8)

#i4 = median_filter(i4, size=3)

# Dump
ski.io.imsave("pages/ald_126_bw.png", i4)
#ski.io.imshow(i4)

plt.show()
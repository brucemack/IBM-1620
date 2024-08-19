import os
page_range = range(1, 455)

for i in page_range:
    cmd = f'magick -density 300 pages/ald_{i:03d}.pdf pages/ald_{i:03d}.png'
    print(cmd)
    os.system(cmd)
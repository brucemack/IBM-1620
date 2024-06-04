"""
This utility was used to convert very page of the PDF to a PNG.
This assumed that the PDF was split into individual pages in 
advance.
"""
from pdf2image import convert_from_path

in_base_dir = "/home/bruce/host/IBM-1620/f_ald/ilovepdf_split"
in_page_fn = "1620_F_ALD_SN11093-"

out_base_dir = "/home/bruce/host/IBM-1620/f_ald/png"

for i in range(1, 483):

    fn = in_base_dir + "/" + in_page_fn + str(i)
    print(fn)

    pages = convert_from_path(fn + ".pdf")

    # Save each page as a JPEG file using Pillow
    for j, page in enumerate(pages):
        page.save(f'{out_base_dir}/page_{i}.png', 'PNG')


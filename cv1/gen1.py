import os
import json 
import math
import shutil 

image_dir = "pages"
meta_dir = "meta"
out_file = "out/index.html"

def load_image_meta(fn):
    global ol_translation, ol_scale, ol_rotation_theta, ol_x_pitch, ol_y_pitch, page_type, page_number
    complete_fn = meta_dir + "/" + fn + ".json"
    if os.path.isfile(complete_fn):
        with open(complete_fn) as f:
            return json.load(f)
    else:
        print("Unable to file meta for", fn)

with open(out_file, "w+") as of:

    of.write("<html>\n")
    of.write("<head>")
    of.write("<title>IBM 1620 F</title>")
    of.write("<link rel=\"stylesheet\" href=\"main.css\">")
    of.write("</head>")
    of.write("<body>\n")

    of.write("<h1>IBM 1620 F - EC404750C</h1>\n")

    of.write("<ul class=\"page-list\">\n")

    for img_number in range(2, 455):

        img_fn = f"ald_{img_number:03d}"
        meta = load_image_meta(img_fn + "_bw")
        pn = meta["page_number"]
        if pn == "??.??.??.??":
            continue
        
        if pn.startswith("00.") or pn.startswith("01.") or pn.startswith("02.") or pn.startswith("C."):
            img_file_name = pn + ".png"
        else:
            img_file_name = img_fn + ".png"
        
        # Copy the file
        #shutil.copyfile(image_dir + "/" + img_fn + ".png", "out/" + img_file_name)

        of.write("<li>\n")
        of.write("<a href=\"" + img_file_name + "\">")
        of.write(meta["page_number"])
        of.write("</a>\n")
        of.write("</li>\n")

    of.write("</ul>\n")
    of.write("</body>\n")
    of.write("</html>\n")




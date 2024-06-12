from pathlib import Path
import csv
from datetime import datetime

out_base = "/home/bruce/IBM1620/hardware/sms-cards"

def escape(s):
    return s.replace("\"", "\\\"")

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

base = "/home/bruce/IBM-1620/sms-cards"
pinNames = [ "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R" ]

with open("/home/bruce/host/sms.csv", "r") as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    count = 0
    for tokens in reader:
        if count > 0:
            code = tokens[0]
            if tokens[23] == "1620G":
                Path(out_base + "/" + code).mkdir(parents=True, exist_ok=True)
                with open(out_base + "/" + code + "/" + code + ".yaml", "+w") as outf:
                    outf.write("# IBM 1620 Logic Reproduction Project\n")
                    outf.write("# Generated from https://github.com/IBM-1620/IBM1620/blob/main/hardware/IBM%201620%20SMS%20Cards.xls\n")
                    outf.write("# " + now + "\n")
                    outf.write("code: " + code + "\n")            
                    outf.write("description: \"" + escape(tokens[22]) + "\"\n")
                    outf.write("function: \"" + escape(tokens[21]) + "\"\n")
                    outf.write("pins:\n")
                    # Pins
                    for p in range(0, 16):
                        outf.write("  " + pinNames[p] + ":\n")
                        name = tokens[1 + p]
                        type = "UNKNOWN"
                        if name.startswith("I"):
                            type = "INPUT"
                        elif name.startswith("O"):
                            type = "OUTPUT"
                        elif name == "-":
                            type = "NC"
                            name = ""
                        elif name == "GND":
                            type = "GND"
                        elif name == "-12V":
                            type = "VN12"
                        elif name == "+12VM":
                            type = "VP12"
                        outf.write("    type: " + type + "\n")
                        outf.write("    name: \"" + name + "\"\n")

        count = count + 1
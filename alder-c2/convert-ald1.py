import yaml
import schem2
import sys 

# Load up the ALD1 pages
ald_dir = "../daves-1f/pages"
sms_meta_dir = "../../IBM1620/hardware/sms-cards"
util_dir = "../../IBM1620/hardware/sms-cards/util"

pages_file = "core-pages.yaml"
#pages_file = "typewriter-pages.yaml"
out_file = "./core.v"

machine = schem2.Machine(sms_meta_dir, util_dir)

with open(ald_dir + "/" + pages_file) as file:
    p = yaml.safe_load(file)
    for ald_fn in p["pages"]:
        print(ald_fn)
        machine.load_from_ald1(ald_dir + "/" + ald_fn + ".yaml")
"""
def v2(pin):
    print("  ", pin.get_id())
    for c in pin.get_connections():
        print("       Conn :", c.get_global_id())

def v1(device):
    print(device.get_id())
    device.visit_pins(v2)

machine.visit_devices(v1)        
"""

machine.create_nodes()

# Look for single-pin nodes
for node in machine.get_nodes():
    if node.get_pin_count() == 1:
        print("Single pin node", node.get_name(), " -> ", node.get_pins()[0].get_global_id())
    
# Look for multi-driver node
for node in machine.get_nodes():
    if node.is_multidriver():
        print("Multi-driver node", node.get_name())
        for pin in node.get_pins():
            if pin.is_driver():
                print("  ", pin.get_global_id(), pin.device.get_type_name())
        
# Dump verilog
with open(out_file, "w+") as ostr:

    #ostr = sys.stdout
    s = "module machine();\n"
    ostr.write(s)

    machine.visit_nodes(lambda node: node.generate_verilog(ostr))

    def device_visitor(device):
        if device.get_name() != "_ALIASES": 
            device.generate_verilog(ostr)

    machine.visit_devices(device_visitor)

    # Setup the initial block
    ostr.write("initial begin" + "\n")
    ostr.write("  #64;" + "\n")
    ostr.write("  $finish;" + "\n")
    ostr.write("end" + "\n")

    s = "endmodule;\n"
    ostr.write(s)

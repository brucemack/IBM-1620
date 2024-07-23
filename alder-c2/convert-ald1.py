import yaml
import schem2
import sys 

# Load up the ALD1 pages
ald_dir = "../daves-1f/pages"
sms_meta_dir = "../../IBM1620/hardware/sms-cards"

machine = schem2.Machine(sms_meta_dir)

with open(ald_dir + "/core-pages.yaml") as file:
    p = yaml.safe_load(file)
    for ald_fn in p["pages"]:
        print(ald_fn)
        machine.load_from_ald1(ald_dir + "/" + ald_fn + ".yaml")

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
        
for node in machine.get_nodes():
    node.generate_verilog(sys.stdout)
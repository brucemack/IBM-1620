import yaml
import util 
import schem 
import net2 as net
import numpy as np
import logicbox

indir = "../daves-1f/pages"

class Device:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def get_name(self) -> str: return self.name
    def get_type(self) -> str: return self.type
  
class Pin:
    def __init__(self, name, fixed_name = False):
        self.connections = []
        self.name = name
        self.fixed_name = fixed_name
        self.node = None
    
    def get_neighbors(self): return self.connections
    
    def is_fixed_name(self): return self.fixed_name
    
    def get_name(self): return self.name 

    def add_neighbor(self, p):
        # Prevent duplicates
        if not (p in self.connections):
            self.connections.append(p)

    def set_node(self, n): self.node = n
    
    def get_node(self): return self.node

class Node:
    def __init__(self, name):
        self.edges = []
        self.name = name
        self.current = True

    def get_name(self) -> str: return self.name

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_edges(self):
        return self.edges

    # Added to allow the graph traversal code to work
    def get_neighbors(self):
        return self.edges
    
    def __str__(self):
        return self.name

    def tick(self):
        self.current = False

    def set_current(self): self.current = True

# First phase: Create the universe of devices and pins, including
# all cross-connections.
def load_page_1a(p, devices, pins):

    # First pass registers all known devices/pins
    if "devices" in p:
        for device in p["devices"]:
            device_name = device["name"].upper()
            device_type = device["type"]
            if not device_name in devices:
                devices[device_name] = Device(device_name, device_type)
            else:
                # Check for type consistency
                if devices[device_name].get_type() != device_type:
                    raise Exception("Device type consistency error " + device_name + " " + device_type)
            for pin_name, _ in device["pins"].items():
                local_pin_name = device_name + "." + pin_name.upper()
                local_pin = Pin(local_pin_name, False)
                if local_pin_name in pins:
                    raise Exception("Duplicate definition of pin " + local_pin_name)
                pins[local_pin_name] = local_pin

# Second pass: Creates connections
def load_page_1b(p, devices, pins):

    if "devices" in p:
        for device in p["devices"]:
            device_name = device["name"].upper()
            for pin_name, pin_connections in device["pins"].items():
                local_pin_name = device_name + "." + pin_name.upper()
                local_pin = pins[local_pin_name]
                if pin_connections:
                    # Get the list of connection targets
                    if pin_connections.__class__ == list:
                        connections = [x.upper() for x in pin_connections]
                    else:
                        connections = [ pin_connections.upper() ]
                    for connection in connections:
                        # Any connection that is not to a known pin will
                        # be assumed to be a net name
                        if not (connection in pins):
                            target_pin = Pin(connection, True)
                            pins[target_pin.get_name()] = target_pin

                        else:
                            target_pin = pins[connection]
                        # Cross-connect
                        local_pin.add_neighbor(target_pin)
                        target_pin.add_neighbor(local_pin)

unique_id = 1

# Second phase: create electrical nodes
def load_page_2(p, devices, pins, nodes):
    
    global unique_id 

    # Now start from every pin and traverse the electrical connectivity
    for _, pin in pins.items():
        # If the pin is connected then we've already traversed it
        if pin.get_node() == None:

            # Assemble a list of everything that is connected to the pin 
            connected_pins = set()

            def pin_visitor(pin, _):
                if not pin in connected_pins:
                    connected_pins.add(pin)
                return True

            # Pursue all paths that start with this pin, assembling a full net
            util.traverse_graph([ pin ], pin_visitor)

            if len(connected_pins) > 0:
                # Check to see if we have a case of multiple fixed names
                name_list = []
                for p in connected_pins:
                    if p.is_fixed_name():
                        name_list.append(p.get_name())
                if len(name_list) > 1:
                    print("Multiple names: ", name_list)
                    raise Exception("Multiple fixed names on same net")

                # Check to see if any of the pins have fixed names, if 
                # so that has priority in node naming
                pin_with_fixed_name = None
                node = None
                for p in connected_pins:
                    if p.is_fixed_name():
                        pin_with_fixed_name = p
                        break
                if pin_with_fixed_name:
                    node = Node(pin_with_fixed_name.get_name())
                else:
                    # If we reach this point with no node connections 
                    # Then we can make a new node and connect all related
                    # pins to it.
                    unique_id = unique_id + 1
                    node_name = "_NODE" + str(unique_id) + "_" + pin.get_name()
                    node = Node(node_name)
                
                nodes[node.get_name()] = node

                # All pins that were in this connection set
                for connected_pin in connected_pins:
                    connected_pin.set_node(node)

def load_page_from_file_1a(infile: str, devices, pins):
    with open(indir + "/" + infile) as file:
        p = yaml.safe_load(file)
    load_page_1a(p, devices, pins)

def load_page_from_file_1b(infile: str, devices, pins):
    with open(indir + "/" + infile) as file:
        p = yaml.safe_load(file)
    load_page_1b(p, devices, pins)

def load_page_from_file_2(infile: str, devices, pins, nodes):
    with open(indir + "/" + infile) as file:
        p = yaml.safe_load(file)
    load_page_2(p, devices, pins, nodes)
   
def get_conn(pins, device, pin_name):
    full_pin_name = device.get_name().upper() + "." + pin_name.upper()
    if not (full_pin_name in pins):
        return None
    return pins[full_pin_name].get_node()

def fmt_path(path):
    s = ""
    for m in path:
        m.set_current()
        s = s + str(m) + " -> "
    return s

devices = {}
pins = {}
nodes = {}

# Some virtual pins
pins["GND"] = Pin("GND", True)
pins["VP48"] = Pin("VP48", True)

infiles = [
    "01.81.50.1.yaml",
    "01.81.55.1.yaml",
    "01.82.70.1.yaml",
    "01.82.72.1.yaml",
    "01.82.75.1.yaml",
    "01.82.80.1.yaml",
    "01.82.82.1.yaml",
    "01.82.84.1.yaml",
    "01.82.86.1.yaml",
    "controls-2.yaml"
]

for infile in infiles:    
    try:
        load_page_from_file_1a(infile, devices, pins)
    except Exception as ex:
        print("Failed on page", infile, ex)
        raise ex
        quit()
for infile in infiles:    
    load_page_from_file_1b(infile, devices, pins)
for infile in infiles:    
    load_page_from_file_2(infile, devices, pins, nodes)

# Diag
for _, pin in pins.items():
    print(pin.get_name(), pin.get_node().get_name())
    #for n in pin.get_neighbors():
    #    print("   ", n.get_name())    

SHORT_R = 0.001
OPEN_R = 100000000
COIL_R = 50 

def setup_switch(name: str, pins):

    parts = []

    pin_c_name = name + ".C"
    pin_no_name = name + ".NO"
    dev_name = name.lower() + "_no_sw"

    if pin_c_name in pins and pin_no_name in pins:
        node_c_name = pins[pin_c_name].get_node().get_name()
        node_no_name = pins[pin_no_name].get_node().get_name()
        parts.append(schem.Component(dev_name, "sw", [ node_no_name, node_c_name ], 
                { "r0": OPEN_R, "r1": SHORT_R }))

    return parts

def setup_duo_relay(name: str, pins):

    parts = []

    # Pick coil
    pin_pa = pins[name + ".PA"]
    node_pa = pin_pa.get_node().get_name()
    pin_pb = pins[name + ".PB"]
    node_pb = pin_pb.get_node().get_name()
    node_px = name + ".px"
    parts.append(schem.Component(name.lower() + "_pick_current", "v", [ node_pa, node_px ], { "v": 0 } ))
    parts.append(schem.Component(name.lower() + "_pcoil", "r", [ node_px, node_pb ], { "r": COIL_R } ))

    # Hold coil
    pin_ha = pins[name + ".HA"]
    node_ha = pin_ha.get_node().get_name()
    pin_hb = pins[name + ".HB"]
    node_hb = pin_hb.get_node().get_name()
    node_hx = name + ".hx"
    parts.append(schem.Component(name.lower() + "_hold_current", "v", [ node_ha, node_hx ], { "v": 0 } ))
    parts.append(schem.Component(name.lower() + "_hcoil", "r", [ node_hx, node_hb ], { "r": COIL_R } ))

    # Stacks
    for s in range(0, 13):
        pin_c_name = name + "." + str(s) + "C"
        if not pin_c_name in pins:
            continue
        node_c_name = pins[pin_c_name].get_node().get_name()

        pin_no_name = name + "." + str(s) + "NO"
        dev_no_name = name.lower() + "_" + str(s) + "no_sw"
        if pin_no_name in pins:
            node_no_name = pins[pin_no_name].get_node().get_name()
            parts.append(schem.Component(dev_no_name, "sw", [ node_no_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R }))

        pin_nc_name = name + "." + str(s) + "NC"
        dev_nc_name = name.lower() + "_" + str(s) + "nc_sw"
        if pin_nc_name in pins:
            node_nc_name = pins[pin_nc_name].get_node().get_name()
            parts.append(schem.Component(dev_nc_name, "sw", [ node_nc_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R, "state": True }))

    return parts

def setup_latching_relay(name: str, pins):

    parts = []

    # Pick coil
    pin_pa = pins[name + ".LPA"]
    node_pa = pin_pa.get_node().get_name()
    pin_pb = pins[name + ".LPB"]
    node_pb = pin_pb.get_node().get_name()
    node_px = name + ".px"
    parts.append(schem.Component(name.lower() + "_pick_current", "v", [ node_pa, node_px ], { "v": 0 } ))
    parts.append(schem.Component(name.lower() + "_pcoil", "r", [ node_px, node_pb ], { "r": COIL_R } ))

    # Hold coil
    pin_ha = pins[name + ".LTA"]
    node_ha = pin_ha.get_node().get_name()
    pin_hb = pins[name + ".LTB"]
    node_hb = pin_hb.get_node().get_name()
    node_hx = name + ".tx"
    parts.append(schem.Component(name.lower() + "_trip_current", "v", [ node_ha, node_hx ], { "v": 0 } ))
    parts.append(schem.Component(name.lower() + "_tcoil", "r", [ node_hx, node_hb ], { "r": COIL_R } ))

    # Stacks
    for s in range(0, 13):
        pin_c_name = name + "." + str(s) + "C"
        if not pin_c_name in pins:
            continue
        node_c_name = pins[pin_c_name].get_node().get_name()

        pin_no_name = name + "." + str(s) + "NO"
        dev_no_name = name.lower() + "_" + str(s) + "no_sw"
        if pin_no_name in pins:
            node_no_name = pins[pin_no_name].get_node().get_name()
            parts.append(schem.Component(dev_no_name, "sw", [ node_no_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R }))

        pin_nc_name = name + "." + str(s) + "NC"
        dev_nc_name = name.lower() + "_" + str(s) + "nc_sw"
        if pin_nc_name in pins:
            node_nc_name = pins[pin_nc_name].get_node().get_name()
            parts.append(schem.Component(dev_nc_name, "sw", [ node_nc_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R, "state": True }))

    return parts

# NOTE POLARITY!
def setup_tb78(name: str, pins):

    parts = []

    pin_1a_name = name + ".1A"
    node_1a_name = pins[pin_1a_name].get_node().get_name()
    pin_1b_name = name + ".1B"
    node_1b_name = pins[pin_1b_name].get_node().get_name()
    dev_1_name = name.lower() + ".1"
    parts.append(schem.Component(dev_1_name, "d", [ node_1a_name, node_1b_name ]))

    pin_2a_name = name + ".2A"
    node_2a_name = pins[pin_2a_name].get_node().get_name()
    pin_2b_name = name + ".2B"
    node_2b_name = pins[pin_2b_name].get_node().get_name()
    dev_2_name = name.lower() + ".2"
    parts.append(schem.Component(dev_2_name, "d", [ node_2b_name, node_2a_name ]))

    return parts

# NOTE POLARITY!
def setup_tb74(name: str, pins):

    parts = []

    pin_4a_name = name + ".4A"
    node_4a_name = pins[pin_4a_name].get_node().get_name()
    pin_4b_name = name + ".4B"
    node_4b_name = pins[pin_4b_name].get_node().get_name()
    dev_4_name = name.lower() + ".4"
    parts.append(schem.Component(dev_4_name, "d", [ node_4b_name, node_4a_name ]))

    pin_7a_name = name + ".7A"
    node_7a_name = pins[pin_7a_name].get_node().get_name()
    pin_7b_name = name + ".7B"
    node_7b_name = pins[pin_7b_name].get_node().get_name()
    dev_7_name = name.lower() + ".7"
    parts.append(schem.Component(dev_7_name, "d", [ node_7a_name, node_7b_name ]))

    return parts

def setup_crcb(name: str, pins):

    parts = []

    pin_c_name = name + ".C"
    node_c_name = pins[pin_c_name].get_node().get_name()

    for i in range(1,7):
        pin_name = name + ".OUT" + str(i)
        node_name = pins[pin_name].get_node().get_name()
        dev_name = name.lower() + "_" + str(i) + "no_sw"
        parts.append(schem.Component(dev_name, "sw", [ node_name, node_c_name ], 
                                    { "r0": OPEN_R, "r1": SHORT_R }))

    return parts

def setup_solenoid(name: str, pins):

    parts = []

    pin_a = pins[name + ".A"]
    node_a = pin_a.get_node().get_name()
    pin_b = pins[name + ".B"]
    node_b = pin_b.get_node().get_name()
    node_x = name + ".x"
    parts.append(schem.Component(name.lower() + "_current", "v", [ node_a, node_x ], { "v": 0 } ))
    parts.append(schem.Component(name.lower() + "_coil", "r", [ node_x, node_b ], { "r": COIL_R } ))

    return parts

# NOTE POLARITY!
def setup_diode(name: str, pins):

    parts = []

    pin_a_name = name + ".A"
    node_a_name = pins[pin_a_name].get_node().get_name()
    pin_b_name = name + ".B"
    node_b_name = pins[pin_b_name].get_node().get_name()
    dev_name = name.lower()
    parts.append(schem.Component(dev_name, "d", [ node_a_name, node_b_name ]))

    return parts

def setup_pass(name: str, pins):

    parts = []

    pin_a_name = name + ".A"
    node_a_name = pins[pin_a_name].get_node().get_name()
    pin_b_name = name + ".B"
    node_b_name = pins[pin_b_name].get_node().get_name()
    dev_name = name.lower()
    parts.append(schem.Component(dev_name, "r", [ node_a_name, node_b_name ], { "r": 1 } ))

    return parts

# Setup devices
out_devices = []

# Supply and ground
out_devices.append(schem.Component("VP48", "v", [ "VP48", "0" ], { "v": 48 } ))
out_devices.append(schem.Component("GND", "r", [ "GND", "0" ], { "r": 1 } ))

for name, device in devices.items():
    if device.get_type() == "relay":
        out_devices.extend(setup_duo_relay(name, pins))
    elif device.get_type() == "relaylatching":
        out_devices.extend(setup_latching_relay(name, pins))
    elif device.get_type() == "switch":
        out_devices.extend(setup_switch(name, pins))
    elif device.get_type() == "tb74":
        out_devices.extend(setup_tb74(name, pins))
    elif device.get_type() == "tb78":
        out_devices.extend(setup_tb78(name, pins))
    elif device.get_type() == "crcb":
        out_devices.extend(setup_crcb(name, pins))
    elif device.get_type() == "solenoid":
        out_devices.extend(setup_solenoid(name, pins))
    elif device.get_type() == "diode":
        out_devices.extend(setup_diode(name, pins))
    elif device.get_type() == "pass":
        out_devices.extend(setup_pass(name, pins))
    else:
        raise Exception("Problem with device " + device.get_type())

c1 = schem.Circuit(out_devices, [ ])

for c in out_devices:
    print(c)

net_nodes = {}
net_nodes["0"] = net.Node("0")
net_edges = []

def get_or_create_node(node_name):
    global net_nodes
    if not node_name in net_nodes:
        net_nodes[node_name] = net.Node(node_name)
    return net_nodes[node_name]

# Instantiate the final network
def net_setup_visitor(name, type, io_names, params):
    print(type, name, io_names, params)
    if type == "r":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "r" in params:
            raise Exception("Parameter missing for device " + name)
        edge = net.ResistorEdge(name, 
            get_or_create_node(io_names[0]), get_or_create_node(io_names[1]),
            float(params["r"]))
        net_edges.append(edge)
    elif type == "d":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        edge = net.DiodeEdge(name, 
            get_or_create_node(io_names[0]), get_or_create_node(io_names[1]))
        net_edges.append(edge)
    elif type == "sw":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "r0" in params or not "r1" in params:
            raise Exception("Parameter missing for device " + name)
        state = False
        if "state" in params:
            state = params["state"]
        edge = net.SwitchEdge(name, 
            get_or_create_node(io_names[0]), get_or_create_node(io_names[1]),
            float(params["r0"]), float(params["r1"]), state)
        net_edges.append(edge)
    elif type == "v":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "v" in params:
            raise Exception("Parameter missing for device " + name)
        edge = net.VoltageSourceEdge(name, 
            get_or_create_node(io_names[0]), 
            get_or_create_node(io_names[1]),
            get_or_create_node("#" + name),
            float(params["v"]))
        net_edges.append(edge)
    else:
        raise Exception("Unable to create device " + name)

c1.visit_leaves({ }, None, [ ], net_setup_visitor)

# Assign node numbers
node_count = 1
for node in net_nodes.values():
    if node.get_name() != "0":
        node.set_index(node_count)
        print("Node", node.get_name(), node.get_index())
        node_count = node_count + 1

# Get node names
edge_names = {}
for edge in net_edges:
    edge_names[edge.get_name()] = edge

# Setup linear algebra
A = net.Matrix(node_count - 1, node_count - 1)
b = net.Vector(node_count - 1)
x = np.zeros((node_count - 1))

# LogicBox Related

# Interface to allow the LogicBox to pull values out of the solved network
class Source:
    def __init__(self):
        self.threshold = 0.1
    def set_x(self, x):
        self.x = x
    def get(self, name):
        #print("Get", name)
        node = net_nodes["#" + name]
        # Turn the current into a boolean
        # TODO: INVESTIGATE SIGN OF COIL CURRENT!
        return (abs(x[node.get_index() - 1]) > self.threshold)

lb_source = Source()
lb = logicbox.LogicBox("../daves-1f/typewriter-mechanical.logic", lb_source)    

# Time steps
for i in range(0, 360 * 3):

    print("-----", int(i / 360), (i % 360), "---------")

    A.clear()
    b.clear()

    # Stamp all devices into A/b matrices
    for edge in net_edges:
        edge.stamp(A, b, x)

    # Calculate the network
    x = np.linalg.inv(A.data).dot(b.data)

    # Display values
    """
    for node in net_nodes.values():
        if node.get_index() == 0:
            pass
        else:
            print("Node", node.get_name(), x[node.get_index() - 1])

    """

    for name, node in net_nodes.items():
        if name.startswith("#") and abs(x[node.get_index() - 1]) > 0.1:
            if not name == "#VP48":
                print("Current in node", name, abs(x[node.get_index() - 1]))

    print("_NODE19_R38.1C",x[net_nodes["_NODE19_R38.1C"].get_index() - 1])

    lb_source.set_x(x)      
    lb.tick()

    # Transfer all of the switch values
    for logic_name in lb.get_names():
        if logic_name.endswith("_sw"):
            if not logic_name in edge_names:
                pass
            else:
                changed = edge_names[logic_name].set_state(lb.get(logic_name))
                if changed:
                    print(logic_name, "changed to", lb.get(logic_name))
          


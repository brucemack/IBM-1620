import yaml
import util 

indir = "../daves-1f/pages"

class Device:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.type
  
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
        return "Node: " + self.name

    def tick(self):
        self.current = False

    def set_current(self): self.current = True

class Edge:

    def __init__(self, device: Device, to_node: Node):
        self.device = device
        self.to_node = to_node
        self.current = False
        self.last_current = False
        self.tick_count = 0

    def get_device(self):
        return self.device
    
    def is_conductive(self):
        return True
    
    # Added to allow the graph traversal code to work.  Note
    # that the connection is only good if this edge is 
    # currently conductive.
    def get_neighbors(self):
        if self.is_conductive():
            return [ self.to_node ]
        else:
            return [ ]

    def tick(self):
        self.last_current = self.current
        self.current = False
        self.tick = self.tick + 1

    def get_last_current(self):
        return self.last_current

    def set_current(self): 
        self.current = True

class CRCBEdge(Edge):

    def __init__(self, to_node: Node, make_angle: int, break_angle: int):
        super().__init__(device, to_node)
        self.make_angle = make_angle
        self.break_angle = break_angle

    def __str__(self):
        return "CRCB " + self.device.get_name()

    def is_conductive(self):
        angle = (self.tick * 5) % 360
        if self.make_angle <= angle and angle <= self.break_angle:
            return True
        else:
            return False

class ShortEdge(Edge):

    def __init__(self, device: Device, to_node: Node):
        super().__init__(device, to_node)

    def __str__(self):
        return "ShortEdge " + self.device.get_name()

class SolenoidEdge(Edge):

    def __init__(self, device: Device, to_node: Node):
        super().__init__(device, to_node)

    def __str__(self):
        return "SolenoidEdge " + self.device.get_name()

    def set_current(self): 
        super().set_current()
        print("Current in", self.get_device().get_name())

class NormallyOpenLatchingEdge(Edge):

    def __init__(self, device: Device, to_node: Node, pick_coil: Edge, trip_coil: Edge):
        super().__init__(device, to_node)
        self.pick_coil = pick_coil
        self.trip_coil = trip_coil
        self.state = False
        self.last_state = False

    def set_current(self): 
        super().set_current()
        print("Current in (NO)", self.get_device().get_name())

    def is_conductive(self):
        # Use the coil currents to decide if the transfer state has 
        # changed.
        if self.pick_coil.get_last_current():
            self.state = True
        elif self.trip_coil.get_last_current():             
            self.state = False
        # IMPORTANT: If there is no current in either coil the state
        # remains unchanged!

        if self.state:
            return True
        else:
            return False

# TODO: CONSOLIDATE WITH ABOVE

class NormallyClosedLatchingEdge(Edge):

    def __init__(self, device: Device, to_node: Node, pick_coil: Edge, trip_coil: Edge):
        super().__init__(device, to_node)
        self.pick_coil = pick_coil
        self.trip_coil = trip_coil
        self.state = False
        self.last_state = False

    def set_current(self): 
        super().set_current()
        print("Current in (NC)", self.get_device().get_name())

    def is_conductive(self):
        # Use the coil currents to decide if the transfer state has 
        # changed.
        if self.pick_coil.get_last_current():
            self.state = True
        elif self.trip_coil.get_last_current():             
            self.state = False
        # IMPORTANT: If there is no current in either coil the state
        # remains unchanged!

        if self.state:
            return False
        else:
            return True

class NormallyOpenEdge(Edge):

    def __init__(self, device: Device, to_node: Node, coil0: Edge, coil1: Edge):
        super().__init__(device, to_node)
        self.coil0 = coil0
        self.coil1 = coil1

    def __str__(self):
        return "NormallyOpen " + self.device.get_name()

    def set_current(self): 
        super().set_current()
        print("Current in (NO)", self.get_device().get_name())

    def is_conductive(self):
        if self.coil0 != None and self.coil0.get_last_current():
            return True
        if self.coil1 != None and self.coil1.get_last_current():
            return True
        return False

class NormallyClosedEdge(Edge):

    def __init__(self, device: Device, to_node: Node, coil0: Edge, coil1: Edge):
        super().__init__(device, to_node)
        self.coil0 = coil0
        self.coil1 = coil1

    def __str__(self):
        return "NormallyClosed " + self.device.get_name()

    def set_current(self): 
        super().set_current()
        print("Current in (NC)", self.get_device().get_name())

    def is_conductive(self):
        if self.coil0 != None and self.coil0.get_last_current():
            return False
        if self.coil1 != None and self.coil1.get_last_current():
            return False
        return True

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
    full_pin_name = device.get_name() + "." + pin_name
    if not (full_pin_name in pins):
        return None
    return pins[full_pin_name].get_node()

devices = {}
pins = {}
nodes = {}
edges = []

# Some virtual pins
pins["GND"] = Pin("GND", True)
pins["VP48"] = Pin("VP48", True)

infiles = [
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
    load_page_from_file_1a(infile, devices, pins)
for infile in infiles:    
    load_page_from_file_1b(infile, devices, pins)
for infile in infiles:    
    load_page_from_file_2(infile, devices, pins, nodes)

# Setup edges
for device_name, device in devices.items():

    if device.get_type() == "relay":
        
        # Pick coil 
        a = get_conn(pins, device, "PA")
        b = get_conn(pins, device, "PB")
        pick_coil = None
        if a != None and b != None:
            # NOTICE: Edge only goes in one direction
            pick_coil = SolenoidEdge(device, b) 
            a.add_edge(pick_coil)
            edges.append(pick_coil)
        else:
            raise Exception("Pick coil missing for relay " + device.get_name())
        
        # Hold coil (if used)
        a = get_conn(pins, device, "HA")
        b = get_conn(pins, device, "HB")
        hold_coil = None
        if a != None and b != None:
            # NOTICE: Edge only goes in one direction
            hold_coil = SolenoidEdge(device, b) 
            a.add_edge(hold_coil)
            edges.append(hold_coil)

        # Contacts
        for i in range(1, 12):
            a = get_conn(pins, device, str(i) + "C")            

            b = get_conn(pins, device, str(i) + "NC")
            if a != None and b != None:
                edge = NormallyClosedEdge(device, b, pick_coil, hold_coil)
                a.add_edge(edge)
                edges.append(edge)
                edge = NormallyClosedEdge(device, a, pick_coil, hold_coil)
                b.add_edge(edge)

                edges.append(edge)

            b = get_conn(pins, device, str(i) + "NO")
            if a != None and b != None:
                edge = NormallyOpenEdge(device, b, pick_coil, hold_coil)
                a.add_edge(edge)
                edges.append(edge)
                edge = NormallyOpenEdge(device, a, pick_coil, hold_coil)
                b.add_edge(edge)
                edges.append(edge)
    
    elif device.get_type() == "relaylatching":
        
        # Pick coil
        a = get_conn(pins, device, "LPA")
        b = get_conn(pins, device, "LPB")
        pick_coil = None
        if a != None and b != None:
            # NOTICE: Edge only goes in one direction
            pick_coil = SolenoidEdge(device, b) 
            a.add_edge(pick_coil)
            edges.append(pick_coil)
        else:
            raise Exception("Pick coil missing for relay " + device.get_name())
        
        # Trip coil 
        a = get_conn(pins, device, "LTA")
        b = get_conn(pins, device, "LTB")
        trip_coil = None
        if a != None and b != None:
            # NOTICE: Edge only goes in one direction
            trip_coil = SolenoidEdge(device, b) 
            a.add_edge(trip_coil)
            edges.append(trip_coil)
        else:
            raise Exception("Trip coil missing for relay " + device.get_name())

        # Contacts
        for i in range(1, 12):
            a = get_conn(pins, device, str(i) + "C")            

            b = get_conn(pins, device, str(i) + "NC")
            if a != None and b != None:
                edge = NormallyClosedLatchingEdge(device, b, pick_coil, trip_coil)
                a.add_edge(edge)
                edges.append(edge)
                edge = NormallyClosedLatchingEdge(device, a, pick_coil, trip_coil)
                b.add_edge(edge)

                edges.append(edge)

            b = get_conn(pins, device, str(i) + "NO")
            if a != None and b != None:
                edge = NormallyOpenLatchingEdge(device, b, pick_coil, trip_coil)
                a.add_edge(edge)
                edges.append(edge)
                edge = NormallyOpenLatchingEdge(device, a, pick_coil, trip_coil)
                b.add_edge(edge)
                edges.append(edge)
                               
    elif device.get_type() == "pass":
        a = get_conn(pins, device, "A")
        b = get_conn(pins, device, "B")
        if a != None and b != None:
            edge = ShortEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)
            edge = ShortEdge(device, a)
            b.add_edge(edge)
            edges.append(edge)
    elif device.get_type() == "solenoid":
        a = get_conn(pins, device, "A")
        b = get_conn(pins, device, "B")
        if a != None and b != None:
            edge = SolenoidEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)
            edge = SolenoidEdge(device, a)
            b.add_edge(edge)
            edges.append(edge)
    elif device.get_type() == "crcb":
        a = get_conn(pins, device, "c")
        # Different phases
        b = get_conn(pins, device, "out3")
        if a != None and b != None:
            edge = CRCBEdge(device, b, 99, 309)
            a.add_edge(edge)
            edges.append(edge)
            edge = CRCBEdge(device, a, 99, 309)
            b.add_edge(edge)
            edges.append(edge)
        b = get_conn(pins, device, "out4")
        if a != None and b != None:
            edge = CRCBEdge(device, b, 171, 221)
            a.add_edge(edge)
            edges.append(edge)
            edge = CRCBEdge(device, a, 171, 221)
            b.add_edge(edge)
            edges.append(edge)

        b = get_conn(pins, device, "out5")
        if a != None and b != None:
            edge = CRCBEdge(device, b, 220, 300)
            a.add_edge(edge)
            edges.append(edge)
            edge = CRCBEdge(device, a, 220, 300)
            b.add_edge(edge)
            edges.append(edge)

        b = get_conn(pins, device, "out6")
        if a != None and b != None:
            edge = CRCBEdge(device, b, 310, 360)
            a.add_edge(edge)
            edges.append(edge)
            edge = CRCBEdge(device, a, 310, 360)
            b.add_edge(edge)
            edges.append(edge)

    elif device.get_type() == "switch":
        # ALL SWITCHES OPEN FOR NOW
        pass
    # Special diode array
    elif device.get_type() == "tb74":
        a = get_conn(pins, device, "4b")
        b = get_conn(pins, device, "4a")
        if a != None and b != None:
            # One direction
            edge = ShortEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)
        a = get_conn(pins, device, "7a")
        b = get_conn(pins, device, "7b")
        if a != None and b != None:
            # One direction
            edge = ShortEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)
    # Special diode array
    elif device.get_type() == "tb78":
        a = get_conn(pins, device, "1b")
        b = get_conn(pins, device, "1a")
        if a != None and b != None:
            # One direction
            edge = ShortEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)
        a = get_conn(pins, device, "2b")
        b = get_conn(pins, device, "2a")
        if a != None and b != None:
            # One direction
            edge = ShortEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)
    elif device.get_type() == "diode":
        a = get_conn(pins, device, "a")
        b = get_conn(pins, device, "b")
        if a != None and b != None:
            # One direction
            edge = ShortEdge(device, b)
            a.add_edge(edge)
            edges.append(edge)

    else:
        raise Exception("Device has unrecognized type " + device.get_name() + " " + device.get_type())

"""
# Diag
for _, node in nodes.items():
    print("Node", node.get_name())
    # Edges
    for edge in node.get_edges():
        print("    Edge " + edge.get_device().get_name() + " to ", edge.get_neighbors()[0])        
"""

start = nodes["VP48"]
end = nodes["GND"]

# Do a traversal from the supply
def visit1(node, path):
    # Any successful path?
    if node == end:
        s = ""
        for m in path:
            m.set_current()
            #s = s + str(m) + " "
        #print(s)
        return False
    else:
        return True

for t in range(0, 20):

    angle = (t * 5) % 360
    print(t, "Angle=" , angle)
    
    # Prepare
    for node in nodes.values():
        node.tick()
    for edge in edges:
        edge.tick()

    # Do a traversal from the supply
    util.traverse_graph([ start ], visit1, False)




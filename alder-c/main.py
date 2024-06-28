import yaml

indir = "../daves-1f/pages"


class Device:
    def __init__(self, name):
        self.name = name

class Node:
    def __init__(self, name, fixed = False):
        self.edges = []
        self.name = name
        self.fixed = fixed

    def get_name(self) -> str:
        return self.name

    def add_edge(self, edge):
        self.edges.append(edge)

class DirectedEdge:
    def __init__(self, from_node: Node, to_node: Node):
        self.from_node = from_node
        self.to_node = to_node

# First pass: create the universe of devices and pins. Start 
# to build the list of nodes.
def load_page_1(p, devices, pins, nodes):

    if "devices" in p:
        for device in p["devices"]:
            device_name = device["name"].upper();
            devices[device_name] = Device(device_name)
            for pin_name, pin_connections in device["pins"].items():
                # Put a blank mapping for the pin for now
                pins[device_name + "." + pin_name.upper()] = None
    if "wires" in p:
        for wire in p["wires"]:
            node_name = wire.upper()
            if not node_name in nodes:
                nodes[node_name] = Node(node_name, True)

unique_id = 1

def load_page_2(p, devices, pins, nodes):
    
    global unique_id 

    # On the second pass we connect the nodes
    if "devices" in p:
        for device in p["devices"]:
            device_name = device["name"].upper();
            for pin_name, pin_connections in device["pins"].items():
                full_pin_name_a = device_name + "." + pin_name.upper()
                # If the pin has no connections then skip 
                if pin_connections is None:
                    continue
                # Make sure that this pin hasn't already been linked to a 
                # node from previous activity.  If so, then we don't need 
                # any more work.
                if pins[full_pin_name_a] is None:
                    node = None
                    # Get the list of connection targets
                    if pin_connections.__class__ == list:
                        connections = [x.upper() for x in pin_connections]
                    else:
                        connections = [ pin_connections.upper() ]
                    # Now sweep across the connections and see if any are 
                    # already node names.  If so, we use that.
                    for connection in connections:
                        if connection in nodes:
                            node = nodes[connection]
                            break
                    if node is None:
                        # Now sweep across the pins that we are connected to 
                        # and see if any have already been connected to a node.
                        # If so, inherit that relationship.
                        for connection in connections:
                            if connection in pins:
                                if pins[connection] != None:
                                    node = pins[connection]
                                    break
                            else:
                                raise Exception("Unable to resolve connection: " + connection)
                    if node is None:
                        # If we reach this point with no node connections 
                        # Then we can make a new node and connect all related
                        # pins to it.
                        unique_id = unique_id + 1
                        node_name = "_NODE" + str(unique_id)
                        node = Node(node_name)
                        nodes[node_name] = node
                    # One way or the other, we have a node assignment for the pin
                    pins[full_pin_name_a] = node
                    # Connect all connected pins to the same node (this should 
                    # be fine because we already checked if any were connected
                    # previously).
                    for connection in connections:
                        connection = connection.upper()
                        if connection in pins:
                            pins[connection] = node


def load_page_from_file_1(infile: str, devices, pins, nodes):
    with open(indir + "/" + infile) as file:
        p = yaml.safe_load(file)
    load_page_1(p, devices, pins, nodes)

def load_page_from_file_2(infile: str, devices, pins, nodes):
    with open(indir + "/" + infile) as file:
        p = yaml.safe_load(file)
    load_page_2(p, devices, pins, nodes)
   
devices = {}
pins = {}
nodes = {}

infile = "01.82.84.1.yaml"
load_page_from_file_1(infile, devices, pins, nodes)
infile = "controls-2.yaml"
load_page_from_file_1(infile, devices, pins, nodes)

infile = "01.82.84.1.yaml"
load_page_from_file_2(infile, devices, pins, nodes)
infile = "controls-2.yaml"
load_page_from_file_2(infile, devices, pins, nodes)

print("Nodes", nodes)
print("Pins", pins)

print("What are nodes connected to")

for _, node in nodes.items():
    print("Node", node.get_name())
    s = ""
    for pin_name, pin_node in pins.items():
        if node == pin_node:
            s = s + pin_name + " "
    print("   ", s)




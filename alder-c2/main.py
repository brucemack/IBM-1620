import numpy as np
import net2 as net
import schem as schem 

nodes = {}
nodes["0"] = net.Node("0")
nodes["0"].set_index(0)
edges = []
edge_names = {}

def get_or_create_node(nodes, node_name):
    if not node_name in nodes:
        nodes[node_name] = net.Node(node_name)
    return nodes[node_name]

# Instantiate an instance of the the circuit
def visitor(name, type, io_names, params):
    print(type, name, io_names, params)
    if type == "r":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "r" in params:
            raise Exception("Parameter missing for device " + name)
        edge = net.ResistorEdge(name, 
            get_or_create_node(nodes, io_names[0]), get_or_create_node(nodes, io_names[1]),
            float(params["r"]))
        edges.append(edge)
    elif type == "r2":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "r0" in params or not "r1" in params or not "s0" in params or not "s1" in params:
            raise Exception("Parameter missing for device " + name)
        edge = net.CurrentControlledResistorEdge(name, 
            get_or_create_node(nodes, io_names[0]), get_or_create_node(nodes, io_names[1]),
            get_or_create_node(nodes,  "#" + params["s0"]), get_or_create_node(nodes, "#" + params["s1"]),
            float(params["r0"]), float(params["r1"]))
        edges.append(edge)
    elif type == "v":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "v" in params:
            raise Exception("Parameter missing for device " + name)
        edge = net.VoltageSourceEdge(name, 
            get_or_create_node(nodes, io_names[0]), 
            get_or_create_node(nodes, io_names[1]),
            get_or_create_node(nodes, "#" + name),
            float(params["v"]))
        edges.append(edge)
    else:
        raise Exception("Unable to create device " + name)

schem.test_2(visitor)

# Assign node numbers
node_count = 1
for node in nodes.values():
    if node.get_name() != "0":
        node.set_index(node_count)
        print("Node", node.get_name(), node.get_index())
        node_count = node_count + 1

a = net.Matrix(node_count - 1, node_count - 1)
b = net.Vector(node_count - 1)
x = np.zeros((node_count - 1))

# Two iterations
for i in range(0, 2):

    print("-----", i, "---------")

    a.clear()
    b.clear()

    # Stamp all devices
    for edge in edges:
        edge.stamp(a, b, x)

    # Calculate the network
    #print("A", a.data)    
    #print("b", b.data)
    x = np.linalg.inv(a.data).dot(b.data)

    # Display values
    for node in nodes.values():
        if node.get_index() == 0:
            pass
        else:
            print("Node", node.get_name(), x[node.get_index() - 1])


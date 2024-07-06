import numpy as np
import network as net
import schem as schem 

rt = net.ResistorEdgeType()
cst = net.CurrentSourceEdgeType()
vst = net.VoltageSourceEdgeType()

nodes = {}
nodes["0"] = net.Node("0")
nodes["0"].set_index(0)

edges = []

"""
node_0 = net.Node("0")
node_1 = net.Node("1")
node_2 = net.Node("2")
node_3 = net.Node("3")

nodes.append(node_0)
nodes.append(node_1)
nodes.append(node_2)
nodes.append(node_3)

i = 0
for node in nodes:
    node.set_index(i)
    i = i + 1

va = vst.create(node_1, node_0)
va.set_v(5)
edges.append(va)

ra = rt.create(node_1, node_2)
ra.set_r(1)
edges.append(ra)

vb = vst.create(node_2, node_3)
vb.set_v(1)
edges.append(vb)

rb = rt.create(node_3, node_0)
rb.set_r(1)
edges.append(rb)

nodes = 4

# Hand out the additional variables needed
for edge in edges:
    for i in range(0, edge.get_aux_variable_count()):
        edge.assign_aux_variable(i, nodes)
        nodes = nodes + 1
"""

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
        edge = rt.create(name, get_or_create_node(nodes, io_names[0]), get_or_create_node(nodes, io_names[1]))
        edge.set_r(float(params["r"]))
        edges.append(edge)
    elif type == "v":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "v" in params:
            raise Exception("Parameter missing for device " + name)
        edge = vst.create(name, get_or_create_node(nodes, io_names[0]), get_or_create_node(nodes, io_names[1]))
        edge.set_v(float(params["v"]))
        edges.append(edge)
    else:
        raise Exception("Unable to create device " + name)

schem.test_2(visitor)

# Assign node numbers
node_count = 1
for node in nodes.values():
    if node.get_name() != "0":
        node.set_index(node_count)
        node_count = node_count + 1

# Hand out the additional variables as needed
for edge in edges:
    for i in range(0, edge.get_aux_variable_count()):
        edge.assign_aux_variable(i, node_count)
        node_count = node_count + 1

a = net.Matrix(node_count - 1, node_count - 1)
b = net.Vector(node_count - 1)

# Stamp all devices
for edge in edges:
    edge.stamp(a, b)

print("A", a.data)    
print("b", b.data)
x = np.linalg.inv(a.data).dot(b.data)

# Display values
for node in nodes.values():
    if node.get_index() == 0:
        pass
    else:
        print("Node Voltage", node.get_name(), x[node.get_index() - 1])
for edge in edges:
    if edge.get_aux_variable_count() > 0:
        print("Edge Variable", edge.get_name(), x[edge.get_aux_variable(0) - 1])


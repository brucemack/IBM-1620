import pytest 
import numpy as np
import net2 as net

# This test contains a constant current source attached to ground
def test_1():

    nodes = []
    edges = []

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

    # IMPORTANT: NOTICE NEGATIVE CURRENT
    ia = net.CurrentSourceEdge("ia", node_1, node_0, -5)
    edges.append(ia)

    ra = net.ResistorEdge("ra", node_1, node_2, 1)
    edges.append(ra)

    rb = net.ResistorEdge("rb", node_2, node_0, 2)
    edges.append(rb)

    rc = net.ResistorEdge("rc", node_2, node_3, 1)
    edges.append(rc)

    rd = net.ResistorEdge("rd", node_3, node_0, 1)
    edges.append(rd)

    nodes = 3

    a = net.Matrix(nodes, nodes)
    b = net.Vector(nodes)

    # Stamp all devices
    for edge in edges:
        edge.stamp(a, b)

    x = np.linalg.inv(a.data).dot(b.data)

    # Total resistance is 2 ohms, so node 2 is half voltage
    assert x[1] == 5
    # Node 3 is half way again
    assert pytest.approx(x[2]) == 2.5

# This test has a constant voltage source connected to ground
def test_2():

    nodes = []
    edges = []

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

    va = net.VoltageSourceEdge("va", node_1, node_0, node_3, 5)
    edges.append(va)

    ra = net.ResistorEdge("ra", node_1, node_2, 1)
    edges.append(ra)

    rb = net.ResistorEdge("rb", node_2, node_0, 1)
    edges.append(rb)

    nodes = 4

    a = net.Matrix(nodes - 1, nodes - 1)
    b = net.Vector(nodes - 1)

    # Stamp all devices
    for edge in edges:
        edge.stamp(a, b)

    x = np.linalg.inv(a.data).dot(b.data)

    # Node 2 is half
    assert pytest.approx(x[1]) == 2.5

# Two voltage sources, one not connected to ground. Using 
#  this to check sign conventions.
def test_3():

    nodes = []
    edges = []

    node_0 = net.Node("0")
    node_1 = net.Node("1")
    node_2 = net.Node("2")
    node_3 = net.Node("3")
    node_4 = net.Node("4")
    node_5 = net.Node("5")

    nodes.append(node_0)
    nodes.append(node_1)
    nodes.append(node_2)
    nodes.append(node_3)
    nodes.append(node_4)
    nodes.append(node_5)

    i = 0
    for node in nodes:
        node.set_index(i)
        i = i + 1

    va = net.VoltageSourceEdge("va", node_1, node_0, node_4, 5)
    edges.append(va)

    ra = net.ResistorEdge("ra", node_1, node_2, 1)
    edges.append(ra)

    vb = net.VoltageSourceEdge("vb", node_2, node_3, node_5, 1)
    edges.append(vb)

    rb = net.ResistorEdge("rb", node_3, node_0, 1)
    edges.append(rb)

    nodes = 6

    a = net.Matrix(nodes - 1, nodes - 1)
    b = net.Vector(nodes - 1)

    # Stamp all devices
    for edge in edges:
        edge.stamp(a, b)

    print("A", a.data)    
    print("b", b.data)
    x = np.linalg.inv(a.data).dot(b.data)
    assert x[1] == 3
    assert x[2] == 2

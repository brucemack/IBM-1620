import pytest 
import numpy as np
import network as net

# This test contains a constant current source attached to ground
def test_1():

    rt = net.ResistorEdgeType()
    cst = net.CurrentSourceEdgeType()

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

    ia = cst.create("ia", node_1, node_0)
    # IMPORTANT: NOTICE NEGATIVE CURRENT
    ia.set_i(-5)
    edges.append(ia)

    ra = rt.create("ra", node_1, node_2)
    ra.set_r(1)
    edges.append(ra)

    rb = rt.create("rb", node_2, node_0)
    rb.set_r(2)
    edges.append(rb)

    rc = rt.create("rc", node_2, node_3)
    rc.set_r(1)
    edges.append(rc)

    rd = rt.create("rd", node_3, node_0)
    rd.set_r(1)
    edges.append(rd)

    nodes = 3

    # Hand out the additional variables needed
    for edge in edges:
        for i in range(0, edge.get_aux_variable_count()):
            edge.assign_aux_variable(i, nodes)
            nodes = nodes + 1

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

    rt = net.ResistorEdgeType()
    cst = net.CurrentSourceEdgeType()
    vst = net.VoltageSourceEdgeType()

    nodes = []
    edges = []

    node_0 = net.Node("0")
    node_1 = net.Node("1")
    node_2 = net.Node("2")

    nodes.append(node_0)
    nodes.append(node_1)
    nodes.append(node_2)

    i = 0
    for node in nodes:
        node.set_index(i)
        i = i + 1

    va = vst.create("va", node_1, node_0)
    va.set_v(5)
    edges.append(va)

    ra = rt.create("ra", node_1, node_2)
    ra.set_r(1)
    edges.append(ra)

    rb = rt.create("rb", node_2, node_0)
    rb.set_r(1)
    edges.append(rb)

    nodes = 3

    # Hand out the additional variables needed
    for edge in edges:
        for i in range(0, edge.get_aux_variable_count()):
            edge.assign_aux_variable(i, nodes)
            nodes = nodes + 1

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

    rt = net.ResistorEdgeType()
    cst = net.CurrentSourceEdgeType()
    vst = net.VoltageSourceEdgeType()

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

    va = vst.create("va", node_1, node_0)
    va.set_v(5)
    edges.append(va)

    ra = rt.create("ra", node_1, node_2)
    ra.set_r(1)
    edges.append(ra)

    vb = vst.create("vb", node_2, node_3)
    vb.set_v(1)
    edges.append(vb)

    rb = rt.create("rb", node_3, node_0)
    rb.set_r(1)
    edges.append(rb)

    nodes = 4

    # Hand out the additional variables needed
    for edge in edges:
        for i in range(0, edge.get_aux_variable_count()):
            edge.assign_aux_variable(i, nodes)
            nodes = nodes + 1

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

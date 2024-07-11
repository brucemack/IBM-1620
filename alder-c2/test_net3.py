import pytest 
import numpy as np
import net3 as net

# This test contains a constant current source attached to ground
def test_1():

    devices = []

    # IMPORTANT: NOTICE NEGATIVE CURRENT
    # Positive current flows from 1->0
    # Negative current flows from 0->1
    devices.append(net.CurrentSource("ia", "1", "0", -5))
    devices.append(net.Resistor("ra", "1", "2", 1))
    devices.append(net.Resistor("rb", "2", "0", 2))
    devices.append(net.Resistor("rc", "2", "3", 1))
    devices.append(net.Resistor("rd", "3", "0", 1))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    A = np.zeros((mapper.get_size(), mapper.get_size()))
    b = np.zeros((mapper.get_size()))
    x = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A, b, None, None)
    
    x = np.linalg.inv(A).dot(b)

    # Total resistance is 2 ohms, so node 2 is half voltage
    assert x[1] == 5
    # Node 3 is half way again
    assert pytest.approx(x[mapper.get("3")]) == 2.5

test_1()

# This test has a constant voltage source connected to ground
def test_2():

    devices = []

    devices.append(net.VoltageSource("va", "1", "0", 5))
    devices.append(net.Resistor("ra", "1", "2", 1))
    devices.append(net.Resistor("rb", "2", "0", 1))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    A = np.zeros((mapper.get_size(), mapper.get_size()))
    b = np.zeros((mapper.get_size()))
    x = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A, b, None, None)
    
    print(A)

    x = np.linalg.inv(A).dot(b)

    # Node 2 is half
    assert pytest.approx(x[mapper.get("2")]) == 2.5

# Two voltage sources, one not connected to ground. Using 
#  this to check sign conventions.
def test_3():

    devices = []

    devices.append(net.VoltageSource("va", "1", "0", 5))
    devices.append(net.Resistor("ra", "1", "2", 1))
    devices.append(net.VoltageSource("vb", "2", "3", 1))
    devices.append(net.Resistor("rb", "3", "0", 1))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    A = np.zeros((mapper.get_size(), mapper.get_size()))
    b = np.zeros((mapper.get_size()))
    x = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A, b, None, None)
    
    x = np.linalg.inv(A).dot(b)

    assert x[mapper.get("2")] == 3
    assert x[mapper.get("3")] == 2

# Checking sign convention on current source.  Source is not
# connected to ground.
def test_4():

    devices = []

    devices.append(net.Resistor("ra", "0", "1", 1))
    # We are assuming that a positive current enters the first node and 
    # leaves the second node. 1->2
    devices.append(net.CurrentSource("ia", "1", "2", 1))
    devices.append(net.Resistor("rb", "2", "0", 2))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    A = np.zeros((mapper.get_size(), mapper.get_size()))
    b = np.zeros((mapper.get_size()))
    x = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A, b, None, None)
    
    x = np.linalg.inv(A).dot(b)

    assert x[mapper.get("1")] == -1
    assert x[mapper.get("2")] == 2

# Checking sign convention on current source that is connected to 
# ground.
def test_5():

    devices = []

    # We are assuming that a positive current enters the first node and 
    # leaves the second node. 1->0
    devices.append(net.CurrentSource("ia", "1", "0", 1))
    devices.append(net.Resistor("rb", "1", "0", 1))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    A = np.zeros((mapper.get_size(), mapper.get_size()))
    b = np.zeros((mapper.get_size()))
    x = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A, b, None, None)
    
    x = np.linalg.inv(A).dot(b)

    assert x[mapper.get("1")] == -1

# Two voltage sources, one not connected to ground. Using 
#  this to check sign conventions.
def test_6():

    devices = []

    devices.append(net.VoltageSource("va", "2", "0", 10))
    devices.append(net.Resistor("ra", "2", "1", 100))
    devices.append(net.Diode("d", "0", "1"))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))

    # Initial guess
    x[mapper.get("1")] = 1

    for i in range(0, 50):

        A = np.zeros((mapper.get_size(), mapper.get_size()))
        b = np.zeros((mapper.get_size()))

        # Stamp all devices
        for device in devices:
            device.stamp(A, b, None, x)

        x = np.linalg.inv(A).dot(b)

        print(str(x[mapper.get("#va")]) + "\t" + str(x[mapper.get("2")] - x[mapper.get("1")]))

    #assert x[mapper.get("2")] == 3
    #assert x[mapper.get("3")] == 2

test_6()

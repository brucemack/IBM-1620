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

    # Current should be very low
    assert abs(x[mapper.get("#va")]) < 0.000001
    # Voltage should be close to 10
    assert abs(x[mapper.get("1")]) > 9.6

def test_7():

    OPEN_R = 100000000
    SHORT_R = 0.001
    COIL_R = 50

    devices = []
    devices.append(net.VoltageSource("vp48", "vp48", "0", 48))
    devices.append(net.Resistor("ra", "vp48", "1", OPEN_R))
    devices.append(net.Diode("d", "1", "3"))
    devices.append(net.Resistor("rb", "vp48", "2", SHORT_R))
    devices.append(net.Resistor("rc", "2", "3", SHORT_R))
    devices.append(net.Resistor("rd", "3", "0", COIL_R))

    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))

    # Initial guess
    x[mapper.get("1")] = 1
    x[mapper.get("3")] = 0

    for i in range(0, 50):

        A = np.zeros((mapper.get_size(), mapper.get_size()))
        b = np.zeros((mapper.get_size()))

        # Stamp all devices
        for device in devices:
            device.stamp(A, b, None, x)

        x = np.linalg.inv(A).dot(b)

    #print("Coil voltage", int(x[mapper.get("3")]))
    #print("Diode voltage", mapper.diff(x, "1", "3"))
    assert x[mapper.get("3")] > 47
    assert mapper.diff(x, "1", "3") < 0.01

# Demonstration of a loop with no voltage source.
def test_8():

    devices = []
    # This loop doesn't have a source in it
    devices.append(net.Resistor("ra", "1", "vp48", 1))
    devices.append(net.Resistor("rb", "1", "vp48", 1))
    # This loop is normal
    devices.append(net.VoltageSource("vp48", "vp48", "0", 48))
    devices.append(net.Resistor("rc", "vp48", "0", 1))
    
    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))

    for i in range(0, 50):

        A = np.zeros((mapper.get_size(), mapper.get_size()))
        b = np.zeros((mapper.get_size()))

        # Stamp all devices
        for device in devices:
            device.stamp(A, b, None, x)

        x = np.linalg.inv(A).dot(b)

    assert x[mapper.get("1")] == 48

# Demonstration of an open loop
def test_9():

    devices = []
    # Open loop, but still has a path to ground via the voltage source
    devices.append(net.Resistor("ra", "1", "vp48", 1))
    # This loop is normal
    devices.append(net.VoltageSource("vp48", "vp48", "0", 48))
    devices.append(net.Resistor("rc", "vp48", "0", 1))
    
    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))

    for i in range(0, 50):

        A = np.zeros((mapper.get_size(), mapper.get_size()))
        b = np.zeros((mapper.get_size()))

        # Stamp all devices
        for device in devices:
            device.stamp(A, b, None, x)

        x = np.linalg.inv(A).dot(b)

    assert x[mapper.get("1")] == 48

def test_10():

    devices = []
    # Open loop with a current source
    devices.append(net.Resistor("ra", "0", "1", .1))
    devices.append(net.CurrentSource("ia", "1", "2", 2))
    # This loop is normal
    devices.append(net.VoltageSource("vp48", "vp48", "0", 48))
    devices.append(net.Resistor("rc", "vp48", "0", 1))
    
    mapper = net.Mapper()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))
    A = np.zeros((mapper.get_size(), mapper.get_size()))
    b = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A, b, None, x)

    try:
        # This will fail with a singular matrix
        x = np.linalg.inv(A).dot(b)
        assert False
    except:
        pass

def test_11():

    devices = []
    devices.append(net.VoltageSource("vp48", "vp48", "0", 48))
    devices.append(net.Resistor("rc", "vp48", "2", 1))
    # Notice that node 1 is between the two switches
    sw0 = net.Switch2("sw0", "2", "1", True)
    devices.append(sw0)
    sw1 = net.Switch2("sw0", "1", "0", True)
    devices.append(sw1)

    mapper = net.Mapper()

    # First phase, switch is closed
    mapper.clear()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))
    A0 = np.zeros((mapper.get_size(), mapper.get_size()))
    b0 = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A0, b0, None, x)

    x = np.linalg.inv(A0).dot(b0)

    # Current should be flowing through short
    assert pytest.approx(x[mapper.get("#vp48")], 0.1) == -48

    # Second phase, switches open
    sw0.set_state(False)
    sw1.set_state(False)
    mapper.clear()
    for device in devices:
        device.register_node_names(mapper)

    x = np.zeros((mapper.get_size()))
    A1 = np.zeros((mapper.get_size(), mapper.get_size()))
    b1 = np.zeros((mapper.get_size()))

    # Stamp all devices
    for device in devices:
        device.stamp(A1, b1, None, x)

    x = np.linalg.inv(A1).dot(b1)

    # No current should be flowing 
    assert pytest.approx(x[mapper.get("#vp48")], 0.1) == 0

    # The second matrix should be smaller because there are some nodes missing
    assert A1.shape[0] < A0.shape[0]

def test_12():

    devices = []
    devices.append(net.VoltageSource("vp48", "vp48", "0", 48))
    devices.append(net.Resistor("rc", "vp48", "2", 1))
    # Notice that node 1 is between the two switches
    sw0 = net.Switch2("sw0", "2", "1", True)
    devices.append(sw0)
    sw1 = net.Switch2("sw0", "1", "0", True)
    devices.append(sw1)

    node_name_to_devices = {}
    name_to_device = {}

    for dev in devices:
        name_to_device[dev.get_name()] = dev
        for node_name in dev.get_connected_node_names():
            if not node_name in node_name_to_devices:
                node_name_to_devices[node_name] = []
            node_name_to_devices[node_name].append(dev)

    counter = 0

    def visitor(node_name, name_path):
        nonlocal counter
        #print("Visited", node_name, name_path)
        counter = counter + 1
        # Stop at 0
        if node_name == "0":
            return False
        return True

    net.traverse_graph_2(node_name_to_devices, name_to_device, [ "vp48" ], visitor)

    assert counter == 4

test_12()

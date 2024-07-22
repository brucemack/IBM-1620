import util 
import schem 
import schem2
import net3 as net
import numpy as np
import logicbox
import time 

indir = "../daves-1f/pages"
  
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

def setup_switch(device: schem2.Device):

    parts = []

    dev_name = device.get_name().lower() + "_no_sw"
    pin_c_name = "C"
    pin_no_name = "NO"

    if device.uses_pin(pin_c_name) and device.uses_pin(pin_no_name):
        node_c_name = device.get_node_name_for_pin(pin_c_name)
        node_no_name = device.get_node_name_for_pin(pin_no_name)
        parts.append(schem.Component(dev_name, "sw", [ node_no_name, node_c_name ], 
                { "r0": OPEN_R, "r1": SHORT_R }))

    return parts

def setup_duo_relay(device: schem2.Device):

    parts = []

    # Pick coil
    node_pa = device.get_node_name_for_pin("PA")
    node_pb = device.get_node_name_for_pin("PB")
    parts.append(schem.Component(device.get_name().lower() + "_pick_coil", "co", 
                                 [ node_pa, node_pb ]))

    # Hold coil
    node_ha = device.get_node_name_for_pin("HA")
    node_hb = device.get_node_name_for_pin("HB")
    parts.append(schem.Component(device.get_name().lower() + "_hold_coil", "co", 
                                 [ node_ha, node_hb ] ))

    # Stacks
    for s in range(0, 13):

        pin_c_name = str(s) + "C"
        if not device.uses_pin(pin_c_name):
            continue
        node_c_name = device.get_node_name_for_pin(pin_c_name)

        pin_no_name = str(s) + "NO"
        dev_no_name = device.get_name().lower() + "_" + str(s) + "no_sw"
        if device.uses_pin(pin_no_name):
            node_no_name = device.get_node_name_for_pin(pin_no_name)
            parts.append(schem.Component(dev_no_name, "sw", [ node_no_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R }))

        pin_nc_name = str(s) + "NC"
        dev_nc_name = device.get_name().lower() + "_" + str(s) + "nc_sw"
        if device.uses_pin(pin_nc_name):
            node_nc_name = device.get_node_name_for_pin(pin_nc_name)
            parts.append(schem.Component(dev_nc_name, "sw", [ node_nc_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R, "state": True }))

    return parts

def setup_latching_relay(device: schem2.Device):

    parts = []

    # Pick coil
    node_pa = device.get_node_name_for_pin("LPA")
    node_pb = device.get_node_name_for_pin("LPB")
    parts.append(schem.Component(device.get_name().lower() + "_pick_coil", "co", 
                                 [ node_pa, node_pb ] ))

    # Trip coil
    node_ta = device.get_node_name_for_pin("LTA")
    node_tb = device.get_node_name_for_pin("LTB")
    parts.append(schem.Component(device.get_name().lower() + "_trip_coil", "co", 
                                 [ node_ta, node_tb ]))

    # Stacks
    for s in range(0, 13):
        
        pin_c_name = str(s) + "C"
        if not device.uses_pin(pin_c_name):
            continue
        node_c_name = device.get_node_name_for_pin(pin_c_name)

        pin_no_name = str(s) + "NO"
        dev_no_name = device.get_name().lower() + "_" + str(s) + "no_sw"
        if device.uses_pin(pin_no_name):
            node_no_name = device.get_node_name_for_pin(pin_no_name)
            parts.append(schem.Component(dev_no_name, "sw", 
                                         [ node_no_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R }))

        pin_nc_name = str(s) + "NC"
        dev_nc_name = device.get_name().lower() + "_" + str(s) + "nc_sw"
        if device.uses_pin(pin_nc_name):
            node_nc_name = device.get_node_name_for_pin(pin_nc_name)
            parts.append(schem.Component(dev_nc_name, "sw", 
                                         [ node_nc_name, node_c_name ], 
                                         { "r0": OPEN_R, "r1": SHORT_R, "state": True }))

    return parts

def setup_tb78(device: schem2.Device):

    parts = []

    node_1a_name = device.get_node_name_for_pin("1A")
    node_1b_name = device.get_node_name_for_pin("1B")
    dev_1_name = device.get_name().lower() + ".1"
    # NOTE POLARITY!
    parts.append(schem.Component(dev_1_name, "d", [ node_1a_name, node_1b_name ]))

    node_2a_name = device.get_node_name_for_pin("2A")
    node_2b_name = device.get_node_name_for_pin("2B")
    dev_2_name = device.get_name().lower() + ".2"
    # NOTE POLARITY!
    parts.append(schem.Component(dev_2_name, "d", [ node_2b_name, node_2a_name ]))

    return parts

def setup_tb74(device: schem2.Device):

    parts = []

    node_4a_name = device.get_node_name_for_pin("4A")
    node_4b_name = device.get_node_name_for_pin("4B")
    dev_4_name = device.get_name().lower() + ".4"
    # NOTE POLARITY!
    parts.append(schem.Component(dev_4_name, "d", [ node_4b_name, node_4a_name ]))

    node_7a_name = device.get_node_name_for_pin("7A")
    node_7b_name = device.get_node_name_for_pin("7B")
    dev_7_name = device.get_name().lower() + ".7"
    # NOTE POLARITY!
    parts.append(schem.Component(dev_7_name, "d", [ node_7a_name, node_7b_name ]))

    return parts

def setup_crcb(device: schem2.Device):

    parts = []

    node_c_name = device.get_node_name_for_pin("C")

    for i in range(1,7):
        pin_name = "OUT" + str(i)
        node_name = device.get_node_name_for_pin(pin_name)
        dev_name = device.get_name().lower() + "_" + str(i) + "no_sw"
        parts.append(schem.Component(dev_name, "sw", 
                                    [ node_name, node_c_name ], 
                                    { "r0": OPEN_R, "r1": SHORT_R }))

    return parts

def setup_solenoid(device: schem2.Device):

    parts = []

    node_a = device.get_node_name_for_pin("A")
    node_b = device.get_node_name_for_pin("B")
    parts.append(schem.Component(device.get_name().lower() + "_sol", "co", 
                                 [ node_a, node_b ] ))

    return parts

def setup_diode(device: schem2.Device):

    parts = []

    node_a_name = device.get_node_name_for_pin("A")
    node_b_name = device.get_node_name_for_pin("B")
    dev_name = device.get_name().lower()
    # NOTE POLARITY!
    parts.append(schem.Component(dev_name, "d", 
                                 [ node_a_name, node_b_name ]))

    return parts

def setup_pass(device: schem2.Device):

    parts = []

    node_a_name = device.get_node_name_for_pin("A")
    node_b_name = device.get_node_name_for_pin("B")
    dev_name = device.get_name().lower()
    parts.append(schem.Component(dev_name, "r", 
                                 [ node_a_name, node_b_name ], 
                                 { "r": SHORT_R } ))

    return parts

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

SHORT_R = 0.0000000001
OPEN_R = 100000000
COIL_R = 10

# Load machine
machine = schem2.Machine()
machine.load_from_ald2s(indir, infiles)
machine.create_nodes()


# Setup devices
out_devices = []

# Supply and ground
out_devices.append(schem.Component("VP48", "v", [ "_ALIASES.VP48", "0" ], { "v": 48 } ))
out_devices.append(schem.Component("GND", "r", [ "_ALIASES.GND", "0" ], { "r": SHORT_R } ))

def device_internal_setup(device):
    global out_devices
    if device.get_type_name().lower() == "relay":
        out_devices.extend(setup_duo_relay(device))
    elif device.get_type_name().lower() == "relaylatching":
        out_devices.extend(setup_latching_relay(device))
    elif device.get_type_name().lower() == "switch":
        out_devices.extend(setup_switch(device))
    elif device.get_type_name().lower() == "tb74":
        out_devices.extend(setup_tb74(device))
    elif device.get_type_name().lower() == "tb78":
        out_devices.extend(setup_tb78(device))
    elif device.get_type_name().lower() == "crcb":
        out_devices.extend(setup_crcb(device))
    elif device.get_type_name().lower() == "solenoid":
        out_devices.extend(setup_solenoid(device))
    elif device.get_type_name().lower() == "diode":
        out_devices.extend(setup_diode(device))
    elif device.get_type_name().lower() == "pass":
        out_devices.extend(setup_pass(device))
    elif device.get_type_name().lower() == "_alias":
        pass
    else:
        raise Exception("Problem with device " + device.get_type_name())

# Convert the schem2 to schem 
machine.visit_devices(device_internal_setup)

#for c in out_devices:
#    print(c)

# Look for single-pin nodes
for node in machine.get_nodes():
    if node.get_pin_count() == 1:
        print("Single pin node", node.get_name(), " -> ", node.get_pins()[0].get_global_id())

c1 = schem.Circuit(out_devices, [ ])

net_mapper = net.Mapper()
net_devices = []

# Instantiate the final network
def net_setup_visitor(name, type, io_names, params):
    print(type, name, io_names, params)
    if type == "r":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "r" in params:
            raise Exception("Parameter missing for device " + name)
        net_devices.append(net.Resistor(name, io_names[0], io_names[1], float(params["r"])))
    elif type == "co":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        # NOTE: We represent a coil using a low-valued resistor
        net_devices.append(net.Resistor(name, io_names[0], io_names[1], COIL_R))
    elif type == "d":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        net_devices.append(net.Diode(name, io_names[0], io_names[1]))
    elif type == "sw":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "r0" in params or not "r1" in params:
            raise Exception("Parameter missing for device " + name)
        state = False
        if "state" in params:
            state = params["state"]
        # This switch type will not stamp into the matrix if it is open
        net_devices.append(net.Switch2(name, io_names[0], io_names[1], state))
    elif type == "v":
        if len(io_names) != 2:
            raise Exception("Node count error for device " + name)
        if not "v" in params:
            raise Exception("Parameter missing for device " + name)
        net_devices.append(net.VoltageSource(name, io_names[0], io_names[1], float(params["v"])))
    else:
        raise Exception("Unable to create device " + name)

c1.visit_leaves({ }, None, [ ], net_setup_visitor)

# Display net devices
for nd in net_devices:
    print(nd.get_name(), nd)

# Setup nodes and get device names
mapper = net.Mapper()

# Setup name->device mapping
name_to_device = {}
for dev in net_devices:
    name_to_device[dev.get_name()] = dev

# Setup digital logic

fns = [ "../daves-1f/main.logic", "../daves-1f/typewriter-mechanical.logic" ]
lb = logicbox.LogicBox(fns)    

max_iter = 50

start = time.perf_counter()

# Time steps
for i in range(0, 30 * 5):

    print("-----", i, lb.get_int("tw._cycle"), lb.get_int("tw._angle"), "---------")

    # Get the relevant nodes allocated.  This may depend on device 
    # state, which can change at each time step
    mapper.clear()

    for dev in net_devices:
        dev.register_node_names(mapper)
        #for node_name in dev.get_connected_node_names():
        #    if not node_name in node_name_to_devices:
        #        node_name_to_devices[node_name] = []
        #    node_name_to_devices[node_name].append(dev)

    """
    found_ground = False

    def search_2(node_name, name_path):
        global found_ground
        # Stop at 0
        if node_name == "0" or node_name == "GND" or node_name == "VP48" or node_name == "SOLENOID COMMON":
            print(name_path)
            return False
        return True
    
    # Check to see if there are any nodes that lack a path to ground
    for node_name, _ in node_name_to_devices.items():
        found_ground = False
        net.traverse_graph_2(node_name_to_devices, name_to_device, [ node_name ], ground_search)
        if not found_ground:
            print("No ground path found from node ", node_name)
    """

    #net.traverse_graph_2(node_name_to_devices, name_to_device, [ "_NODE47_D30.A" ], search_2, False)
    #net.traverse_graph_2(node_name_to_devices, name_to_device, [ "_NODE76_PS_1U.A" ], search_2, False)

    # Dimension of network can change at each time step as nodes are added/removed
    # by switch actions.
    x = np.zeros((mapper.get_size()))
    previous_x = np.zeros((mapper.get_size()))

    # NR loop
    converged = False
    for j in range(0, max_iter):

        A = np.zeros((mapper.get_size(), mapper.get_size()))
        b = np.zeros((mapper.get_size()))

        # Stamp all devices
        for device in net_devices:
            device.stamp(A, b, None, x)

        previous_x[:] = x
        x = np.linalg.inv(A).dot(b)
        e = np.absolute(x - previous_x)

        # Display values
        #def node_visitor_1(name, ix):
        #    if abs(x[ix]) > 1:
        #        print("Node", name, ix, abs(x[ix]))
        #mapper.visit_all(node_visitor_1)

        if np.all(e < 0.1): 
            converged = True
            #print("Breaking at", j)
            break

    if not converged:
        print("Warning: failed to converge")
        for i in range(0, mapper.get_size()):
            if e[i] > 0.1:
                print(i, mapper.index_to_name(i), e[i])

    # Push coil/solenoid state into logic 
    coil_values = {}
    for dev in net_devices:
        if dev.can_get_current() and ("_coil" in dev.get_name() or "_sol" in dev.get_name()):
            i = dev.get_current(x)
            if abs(i) > 0.1:
                print("Current in device", dev.get_name(), i)
                coil_values["tw." + dev.get_name()] = True
            else:
                coil_values["tw." + dev.get_name()] = False

    # Advance the logic by one step
    lb.tick(coil_values)

    # Transfer all of the switch values
    for logic_name in lb.get_names():
        if logic_name.startswith("tw.") and logic_name.endswith("_sw"):
            # Strip off the leading "tw."
            device_name = logic_name[3:]
            if not device_name in name_to_device:
                #print("Can't find switch", device_name)
                pass
            else:
                changed = name_to_device[device_name].set_state(lb.get_bool(logic_name))
                if changed:
                    print("CHANGED", device_name, "to", lb.get_bool(logic_name))

end = time.perf_counter()
print(end - start)

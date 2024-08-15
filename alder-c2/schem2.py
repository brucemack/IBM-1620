from __future__ import annotations 
"""
IBM-1620 Logic Reproduction 
Copyright (C) 2024 - Bruce MacKinnon
 
This work is covered under the terms of the GNU Public License (V3). Please consult the 
LICENSE file for more information.

This work is being made available for non-commercial use. Redistribution, commercial 
use or sale of any part is prohibited.
"""
import yaml

class PinMeta:

    def __init__(self, name: str, type: str, drivetype: str, tietype: str):
        self.name = name
        if type == None or type == "UNKNOWN":
            self.type = "PASSIVE"
        elif type == "INPUT" or type == "OUTPUT" or type == "PASSIVE" or type == "GND" or \
            type == "VN12" or type == "VP12" or type == "SYSCLOCK":
            self.type = type
        else:
            raise Exception("Invalid pin type " + type)
        
        if drivetype == None or drivetype == "AH" or drivetype == "AL" or \
            drivetype == "AH_PD" or drivetype == "AL_PU":
            self.drivetype = drivetype 
        else:
            raise Exception("Invalid drive type " + drivetype)
        
        if tietype == None or tietype == "NONE":
            self.tietype = "NONE" 
        elif tietype == "VN12" or tietype == "VP12":
            self.tietype = tietype 
        else:
            raise Exception("Invalid tie type " + tietype)

    def is_driver(self) -> bool:
        return self.type == "OUTPUT"

    def is_driven(self) -> bool:
        return self.type == "INPUT"

    def is_passive(self) -> bool:
        return self.type == "PASSIVE"

class DeviceType:

    def __init__(self, type_name, meta_yaml):
        
        self.type_name = type_name
        self.pin_metas = {}
        self.has_meta = False

        if meta_yaml:
            self.has_meta = True
            for pin_name, pin_yaml in meta_yaml["pins"].items():
                type = None
                if "type" in pin_yaml:
                    type = pin_yaml["type"]
                    if type == "NC":
                        continue
                drivetype = None
                if "drivetype" in pin_yaml:
                    drivetype = pin_yaml["drivetype"]
                tie = None
                if "tie" in pin_yaml:
                    tie = pin_yaml["tie"]
                self.pin_metas[pin_name] = PinMeta(pin_name, type, drivetype, tie)


    def get_name(self) -> str: 
        return self.type_name

    def get_pin_meta(self, local_id) -> PinMeta:
        if self.has_meta:
            if not local_id in self.pin_metas:
                raise Exception("Device type " + self.type_name + " does not have pin " + local_id)
            else:
                return self.pin_metas[local_id]
        else:
            return None

class AliasDeviceType():

    def get_name(self) -> str: return "_alias"

    def get_pin_meta(self, local_id) -> PinMeta:
        return PinMeta(local_id, "PASSIVE", None, None)

class Device:

    def __init__(self, type: DeviceType, id: str):
        self.type = type
        self.id = id
        self.pins = {}

    def get_type(self) -> DeviceType: return self.type
    def set_type(self, type: DeviceType): self.type = type
    def get_type_name(self) -> str: return self.type.get_name()
    def get_id(self) -> str: return self.id
    def get_name(self) -> str: return self.id

    def visit_pins(self, visitor): 
        for pin in self.pins.values(): visitor(pin)

    def get_or_create_pin(self, id: str):
        if not id in self.pins:
            self.pins[id] = Pin(self, id.upper(), self.get_pin_meta(id.upper()))
        return self.pins[id.upper()]

    def get_pins(self): return self.pins.values()

    def uses_pin(self, local_pin_id):
        return local_pin_id.upper() in self.pins

    def get_node_name_for_pin(self, local_pin_id) -> str:
        if not local_pin_id in self.pins:
            raise Exception("Pin " + local_pin_id + " not found on " + self.id)
        pin = self.pins[local_pin_id]
        if not pin.get_node():
            raise Exception("No node for pin " + local_pin_id + " on " + self.id)
        return pin.get_node().get_name()

    def get_pin_meta(self, local_pin_id) -> PinMeta:
        # If there is no type defined for this device yet then the pin
        # meta is not available.
        if self.type == None:
            return None
        else:
            return self.type.get_pin_meta(local_pin_id)

    def generate_verilog(self, ostr):
        s = "  SMS_CARD_" + self.get_type_name() + " D_" + make_verilog_id(self.get_name()) + "("
        first = True
        for _, pin in self.pins.items():
            if not first:
                s = s + ", "
            s = s + "." + pin.get_id() + "("
            # For multi-driver nets, the driver nets use their own wires 
            if pin.get_node().is_multidriver() and pin.is_driver():
                s = s + "_W" + make_verilog_id(pin.get_global_id())
            # Otherwise, connect to the wire that represents the node
            else:
                s = s + "_W" + make_verilog_id(pin.get_node().get_name())
            s = s + ")"
            first = False
        s = s + ");\n"
        ostr.write(s)

class SMSCard(Device):

    def __init__(self, type: DeviceType, gate_id: str, loc_id: str):
        super().__init__(type, gate_id + "_" + loc_id)
        self.gate_id = gate_id
        self.loc_id = loc_id

class Pin:

    def __init__(self, device: Device, id: str, meta: PinMeta):
        self.device: Device = device
        self.id: str = id
        self.meta = meta
        self.connections: list[Pin] = []
        self.node = None

    def get_id(self) -> str: return self.id
    def get_device(self) -> Device: return self.device

    def get_global_id(self): return self.device.get_id() + "." + self.id

    def add_connection(self, conn):
        if not conn in self.connections:
            self.connections.append(conn)

    def get_connections(self) -> list:
        return self.connections

    def get_node(self): return self.node 
    def set_node(self, n): self.node = n

    def get_meta(self): return self.meta
    def is_driver(self): return self.meta.is_driver()
    def is_driven(self): return self.meta.is_driven()
    def is_passive(self): return self.meta.is_passive()

def make_verilog_id(i: str) -> str:
    i = i.replace("+S", "PS")
    i = i.replace("-S", "NS")
    i = i.replace(".", "_")
    i = i.replace(" ", "_")
    return i

class Node:

    def __init__(self, name, pins):
        self.name = name
        self.pins = pins

    def get_name(self): return self.name

    def get_pins(self): return self.pins

    def get_pin_count(self): return len(self.pins)

    def is_multidriver(self) -> bool:
        driver_count = 0
        for pin in self.pins:
            if pin.is_driver():
                driver_count = driver_count + 1
        return driver_count > 1

    def generate_verilog(self, ostr):
        """
        The generation of Verilog for a node needs to take into 
        account the possibility of multi-driver "wired logic".

        If a node is only driven by a single pin then nothing 
        special happens - the node is realized using a normal
        Verilog wire.

        If a node has both active pull-up an active pull-down
        drivers then we have may have a conflict and an error is 
        generated.

        If a node is driven by more than one active pull up
        then we consider this to be a wire-or situation. If
        there is a passive pull-down on the node then the 
        default value is 0. If there is no pull-down on the
        node then the default value is undefined/floating.
        """
        # Organize the pins into drivers, driven, and passive
        driver_pins = []
        driven_pins = []
        passive_pins = []
        for pin in self.pins:
            if pin.is_driver():
                driver_pins.append(pin)
            elif pin.is_driven():
                driven_pins.append(pin)
            elif pin.is_passive():
                passive_pins.append(pin)

        net_name = "_W" + make_verilog_id(self.get_name())

        if len(driver_pins) == 1:
            # This is the single-driver case
            # Setup a regular wire for this node
            s = "  wire " + net_name + ";\n"
            ostr.write(s)
        else:
            # Figure out what we've got on the line
            active_pull_up = False
            active_pull_down = False
            passive_pull_up = False
            passive_pull_down = False

            # Look at the driver/active pins
            for driver_pin in driver_pins:
                dt = driver_pin.get_meta().drivetype 
                if dt == "AH" or dt == "AH_PD":
                    active_pull_up = True
                    if dt == "AH_PD":
                        passive_pull_down = True
                elif dt == "AL" or dt == "AL_PU":
                    active_pull_down = True
                    if dt == "AL_PU":
                        passive_pull_up = True
                elif dt == None:
                    pass
                else:
                    raise Exception("Invalid drive type " + dt)

            # Check what the passives are doing
            for passive_pin in passive_pins:
                tt = passive_pin.get_meta().tietype
                if tt == "GND" or tt == "VP12":
                    passive_pull_up = True
                elif tt == "VN12":
                    passive_pull_down = True
                elif tt == "NONE":
                    pass
                else:
                    raise Exception("Invalid tie type: " + tt)

            # Look for problem combinations
            if not active_pull_up and not active_pull_down:
                raise Exception("No driver for node: " + self.get_name())                
            if active_pull_down and active_pull_up:
                raise Exception("Conflicting drive types on wire: " + self.get_name())
            if active_pull_up and passive_pull_up:
                raise Exception("Active and passive pull up on wire: " + self.get_name())
            if active_pull_down and passive_pull_down:
                raise Exception("Active and passive pull down on wire: " + self.get_name())
            # This case is a problem because there is nothing to pull down.
            # In the oppose case (activePullDown) we have the benefit of the input pull up
            if active_pull_up and not passive_pull_down:
                raise Exception("Active pull up with no pull down on wire: " + self.get_name())

            if active_pull_up:
                # Generate a suitable net. Any of the drivers can pull the net high with a 1.
                s = "  wor " + net_name + ";\n"
                ostr.write(s)
                if passive_pull_down:
                    s = "  assign " + net_name + " = 0;\n"
                    ostr.write(s)
            else:                
                # Generate a suitable net. Any of the drivers can pull the net low with a 0.
                s = "  wand _W" + make_verilog_id(self.get_name()) + ";\n"
                ostr.write(s)

def recursive_traverse(visited_pins: set[str], start_pin: Pin, visitor = None):
    if not start_pin.get_global_id() in visited_pins:
        if visitor:
            visitor(start_pin)
        visited_pins.add(start_pin.get_global_id())
        for connection in start_pin.get_connections():
            recursive_traverse(visited_pins, connection, visitor)

class Machine:

    def __init__(self, device_meta_dir = None, util_dir = None):
        self.device_meta_dir = device_meta_dir
        self.util_dir = util_dir
        self.device_types = {}
        self.devices = {}
        # A list of tuples
        self.alias_links = []
        self.nodes = []

        # A special device type
        self.device_types["_alias"] = AliasDeviceType()
        # A special device used for managing named nets
        self.alias_device = Device(self.get_device_type("_alias"), "_ALIASES")
        self.devices["_ALIASES"] = self.alias_device

        # Special devices
        if util_dir:
            with open(util_dir + "/ZERO/ZERO.yaml") as file:
                p = yaml.safe_load(file)
                self.device_types["ZERO"] = DeviceType("ZERO", p)
            with open(util_dir + "/ONE/ONE.yaml") as file:
                p = yaml.safe_load(file)
                self.device_types["ONE"] = DeviceType("ONE", p)
            with open(util_dir + "/RST/RST.yaml") as file:
                p = yaml.safe_load(file)
                self.device_types["RST"] = DeviceType("RST", p)
            with open(util_dir + "/IND/IND.yaml") as file:
                p = yaml.safe_load(file)
                self.device_types["IND"] = DeviceType("IND", p)

    def get_device_type(self, type_name: str) -> DeviceType:
        # If there is no device metadata available then we return a shell type
        if not self.device_meta_dir:
            return DeviceType(type_name, None)
        else:
            if not type_name in self.device_types:
                # Load device meta from a file
                with open(self.device_meta_dir + "/" + type_name + "/" + 
                        type_name + ".yaml") as file:
                    p = yaml.safe_load(file)
                    self.device_types[type_name] = DeviceType(type_name, p)
            return self.device_types[type_name]
    
    def get_device_names(self): 
        return list(self.devices.keys())

    def visit_devices(self, visitor):
        for device in self.devices.values(): visitor(device)

    def visit_nodes(self, visitor):
        for node in self.nodes: visitor(node)

    def get_nodes(self): return self.nodes

    def load_from_ald1(self, ald_fn):

        with open(ald_fn) as file:

            p = yaml.safe_load(file)

            coordinates = {}

            if "devices" in p:

                # First pass registers all known devices/pins
                for yaml_device in p["devices"]:
                    gate_id = yaml_device["gate"].upper()
                    loc_id = str(yaml_device["loc"]).upper()
                    device_name = gate_id + "_" + loc_id
                    type_name = yaml_device["typ"].upper().replace("-", "")

                    if not device_name in self.devices:
                        device = SMSCard(self.get_device_type(type_name), gate_id, loc_id)
                        # First time for this device, add it to the machine
                        self.devices[device_name] = device
                    else:
                        device = self.devices[device_name]
                        # Check for type consistency with existing instance
                        if device.get_type().get_name() != type_name:
                            raise Exception("Device type consistency error " + device_name + " " + type_name)

                    # Keep track of the page-local coordinates
                    coordinates[yaml_device["coo"]] = device

                    # Register the pins (if any)
                    if "inp" in yaml_device:
                        for pin_name, _ in yaml_device["inp"].items():
                            # Multiple pins can be encoded 
                            for local_pin_name in list(pin_name.upper()):
                                device.get_or_create_pin(local_pin_name)
                    if "out" in yaml_device:
                        for pin_name, _ in yaml_device["out"].items():
                            # Multiple pins can be encoded 
                            for local_pin_name in list(pin_name.upper()):
                                device.get_or_create_pin(local_pin_name)

                # Second pass, establish the connections
                for yaml_device in p["devices"]:

                    gate_id = yaml_device["gate"].upper()
                    loc_id = str(yaml_device["loc"]).upper()
                    device_name = gate_id + "_" + loc_id

                    # The device exists already (from first pass)
                    device = self.devices[device_name]

                    pin_list = []

                    if "inp" in yaml_device:
                        for pin_name, pin_connections in yaml_device["inp"].items():
                            pin_list.append((pin_name, pin_connections))
                    if "out" in yaml_device:
                        for pin_name, pin_connections in yaml_device["out"].items():
                            pin_list.append((pin_name, pin_connections))

                    for pin_name, pin_connections in pin_list:
                        # Multiple pins can be encoded
                        for local_pin_name in list(pin_name.upper()):
                            local_pin = device.get_or_create_pin(local_pin_name)
                            if pin_connections:
                                # Get the list of connection targets
                                if pin_connections.__class__ == list:
                                    connections = [x.upper() for x in pin_connections]
                                else:
                                    connections = [ pin_connections.upper() ]
                                for connection in connections:
                                    # Dotted connections are assumed to reference another 
                                    # pin directly
                                    if "." in connection:
                                        tokens = connection.upper().split(".")
                                        if len(tokens) != 2:
                                            raise Exception("Connection syntax error " + connection)
                                        target_coordinate = tokens[0]
                                        # Convert the target location to a target device
                                        if not target_coordinate in coordinates:
                                            raise Exception("Pin on device " + device_name + " references " + \
                                                            "unrecognized coordinate " + target_coordinate)
                                        # In ALD1 mode we can only reference devices that are on the same
                                        # page, so therefore the device will already exist.
                                        target_device = coordinates[target_coordinate]
                                        # Multiple pins can be encoded:
                                        for target_pin_name in list(tokens[1].upper()):
                                            target_pin = target_device.get_or_create_pin(target_pin_name)
                                            # Cross-connect
                                            local_pin.add_connection(target_pin)
                                            target_pin.add_connection(local_pin)
                                    # Otherwise, associate a net alias with the pin
                                    else:
                                        target_device = self.alias_device
                                        target_pin = target_device.get_or_create_pin(connection.upper())
                                        # Cross-connect
                                        local_pin.add_connection(target_pin)
                                        target_pin.add_connection(local_pin)

            # Pick up some additional net aliases
            if "aliases" in p:
                for yaml_alias in p["aliases"]:
                    alias_name = yaml_alias["name"].upper()
                    alias_pin = self.alias_device.get_or_create_pin(alias_name)
                    pin_connections = yaml_alias["inp"]
                    # Get the list of connection targets
                    if pin_connections.__class__ == list:
                        connections = [x.upper() for x in pin_connections]
                    else:
                        connections = [ pin_connections.upper() ]
                    for connection in connections:
                        # Dotted connections are assumed to reference another 
                        # pin directly
                        if "." in connection:
                            tokens = connection.upper().split(".")
                            if len(tokens) != 2:
                                raise Exception("Connection syntax error " + connection)
                            target_coordinate = tokens[0]
                            # Convert the target location to a target device
                            if not target_coordinate in coordinates:
                                raise Exception("Pin on device " + device_name + " references " + \
                                                "unrecognized coordinate " + target_coordinate)
                            target_device = coordinates[target_coordinate]
                            # Multiple pins can be encoded
                            for target_pin_name in list(tokens[1].upper()):
                                target_pin = target_device.get_or_create_pin(target_pin_name)
                                # Cross-connect
                                target_pin.add_connection(alias_pin)
                                alias_pin.add_connection(target_pin)
                        # Everything else (i.e. non-dotted names) are the strange case
                        # where an alias points to a different alias.
                        else:
                            target_device = self.alias_device
                            target_pin = target_device.get_or_create_pin(connection)
                            # Cross-connect
                            target_pin.add_connection(alias_pin)
                            alias_pin.add_connection(target_pin)

    def load_from_ald2s(self, indir, ald_fns):
        for ald_fn in ald_fns:
            try:
                self.load_from_ald2(indir + "/" + ald_fn)
            except Exception as ex:
                print("Failed on page", ald_fn, ex)
                raise ex
                quit()

    def load_from_ald2(self, ald_fn):

        with open(ald_fn) as file:

            p = yaml.safe_load(file)

            if "devices" in p:

                # First pass registers all known devices/pins
                for yaml_device in p["devices"]:
                    device_name = yaml_device["name"].upper()
                    type_name = yaml_device["type"].upper()
                    if not device_name in self.devices:
                        # First time for this device, add it to the machine
                        device = Device(self.get_device_type(type_name), device_name)
                        self.devices[device_name] = device
                    else:
                        # Device exists already
                        device = self.devices[device_name]
                        # Check for type consistency with existing instance
                        if device.get_type():
                            if device.get_type().get_name() != type_name:
                                raise Exception("Device type consistency error " + \
                                                device_name + " " + type_name)
                        # If there is no type yet (i.e. have never seen this device) then 
                        # establish the type
                        else:
                            device.set_type(self.get_device_type(type_name))

                    # Register the pins
                    for pin_name, _ in yaml_device["pins"].items():
                        local_pin_name = pin_name.upper()
                        local_pin = device.get_or_create_pin(local_pin_name)

                # Second pass, cross-connects
                for yaml_device in p["devices"]:
                    device_name = yaml_device["name"].upper()
                    # Device exists already
                    device = self.devices[device_name]
                    for pin_name, pin_connections in yaml_device["pins"].items():
                        local_pin_name = pin_name.upper()
                        local_pin = device.get_or_create_pin(local_pin_name)
                        if pin_connections:
                            # Get the list of connection targets
                            if pin_connections.__class__ == list:
                                connections = [x.upper() for x in pin_connections]
                            else:
                                connections = [ pin_connections.upper() ]

                            for connection in connections:
                                # Dotted connections are assumed to reference another 
                                # pin directly
                                if "." in connection:
                                    tokens = connection.upper().split(".")
                                    if len(tokens) != 2:
                                        raise Exception("Connection syntax error " + connection)
                                    # In ALD2 mode it is possible to reference a device on 
                                    # a different sheet (i.e. one that has never been seen before).
                                    # In that case we create a preliminary version of the device
                                    # and will fill it in later.
                                    if not tokens[0] in self.devices:
                                        self.devices[tokens[0]] = Device(None, tokens[0])
                                    target_device: Device = self.devices[tokens[0]]
                                    target_pin = target_device.get_or_create_pin(tokens[1])
                                # Otherwise, assume a net alias
                                else:
                                    target_device = self.alias_device
                                    target_pin = target_device.get_or_create_pin(connection.upper())
                                # Cross-connect
                                local_pin.add_connection(target_pin)
                                target_pin.add_connection(local_pin)

    def create_nodes(self):
        for device in self.devices.values():
            for pin in device.get_pins():
                # Skip pins that have already been joined to a Node
                if not pin.get_node():
                    # Traverse all electrically connected pins 
                    visited_pins = set()
                    node_pins = []
                    def visitor(pin):
                        node_pins.append(pin)
                    recursive_traverse(visited_pins, pin, visitor)
                    # Figure out if any of the pins on the node are aliases.  If
                    # so, these get priority when naming the net
                    naming_pin = node_pins[0]
                    for pin in node_pins:
                        if pin.device == self.alias_device:
                            naming_pin = pin
                            break
                    # Make a node and connect the pins
                    node = Node(naming_pin.get_global_id(), node_pins)
                    self.nodes.append(node)
                    for pin in node_pins:
                        pin.set_node(node)


"""
IBM-1620 Logic Reproduction 
Copyright (C) 2024 - Bruce MacKinnon
 
This work is covered under the terms of the GNU Public License (V3). Please consult the 
LICENSE file for more information.

This work is being made available for non-commercial use. Redistribution, commercial 
use or sale of any part is prohibited.
"""
import yaml

class DeviceType:

    def __init__(self, type_name):
        self.type_name = type_name

    def get_name(self) -> str: return self.type_name

class Device:

    def __init__(self, type: DeviceType, id: str):
        self.type = type
        self.id = id
        self.pins = {}

    def get_type(self) -> DeviceType: return self.type
    def set_type(self, type: DeviceType): self.type = type
    def get_id(self) -> str: return self.id

    def visit_pins(self, visitor): 
        for pin in self.pins.values(): visitor(pin)

    def get_or_create_pin(self, id: str):
        if not id in self.pins:
            self.pins[id] = Pin(self, id)
        return self.pins[id]

    def get_pins(self): return self.pins.values()

class SMSCard(Device):

    def __init__(self, type: DeviceType, gate_id: str, loc_id: str):
        super().__init__(type, gate_id + "_" + loc_id)
        self.gate_id = gate_id
        self.loc_id = loc_id

class Pin:

    def __init__(self, device: Device, id: str):
        self.device: Device = device
        self.id: str = id
        self.connections: list[Pin] = []
        self.node = None

    def get_id(self): return self.id

    def get_global_id(self): return self.device.get_id() + "." + self.id

    def add_connection(self, conn):
        if not conn in self.connections:
            self.connections.append(conn)

    def get_connections(self) -> list:
        return self.connections

    def get_node(self): return self.node 
    def set_node(self, n): self.node = n

class Node:

    def __init__(self, name, pins):
        self.name = name
        self.pins = pins

def recursive_traverse(visited_pins: set[str], start_pin: Pin, visitor = None):
    if not start_pin.get_global_id() in visited_pins:
        if visitor:
            visitor(start_pin)
        visited_pins.add(start_pin.get_global_id())
        for connection in start_pin.get_connections():
            recursive_traverse(visited_pins, connection, visitor)

class Machine:

    def __init__(self):
        self.devices = {}
        # A list of tuples
        self.alias_links = []
        # A special device used for managing named nets
        self.alias_device = Device(None, "_ALIASES")
        self.devices["_ALIASES"] = self.alias_device
        self.nodes = []

    def get_device_type(self, type_name: str) -> DeviceType:
        return DeviceType(type_name)   
    
    def get_device_names(self): return list(self.devices.keys())

    def visit_devices(self, visitor):
        for device in self.devices.values(): visitor(device)

    def get_or_create_device(self, device_id) -> Device:
        if not device_id in self.devices:
            self.devices[device_id] = Device(None, device_id)
        return self.devices[device_id]

    def load_from_ald1(self, ald_fn):

        with open(ald_fn) as file:

            p = yaml.safe_load(file)

            coordinates = {}

            if "devices" in p:

                # First pass registers all known devices/pins
                for yaml_device in p["devices"]:

                    gate_id = yaml_device["gate"].upper()
                    loc_id = yaml_device["loc"].upper()
                    device_name = gate_id + "_" + loc_id
                    type_name = yaml_device["typ"].upper()

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

                    # Register the pins
                    for pin_name, _ in yaml_device["inp"].items():
                        local_pin_name = pin_name.upper()
                        if local_pin_name in device.pins:
                            raise Exception("Duplicate definition of pin " + local_pin_name + \
                                            " on device " + device_name)
                        local_pin = Pin(device, local_pin_name)
                        device.pins[local_pin_name] = local_pin

                # Second pass, establish the connections
                for yaml_device in p["devices"]:

                    gate_id = yaml_device["gate"].upper()
                    loc_id = yaml_device["loc"].upper()
                    device_name = gate_id + "_" + loc_id
                    # Device exists already
                    device = self.devices[device_name]

                    for pin_name, pin_connections in yaml_device["inp"].items():
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
                                    target_coordinate = tokens[0]
                                    # Convert the target location to a target device
                                    if not target_coordinate in coordinates:
                                        raise Exception("Pin on device " + device_name + " references " + \
                                                        "unrecognized coordinate " + target_coordinate)
                                    target_device = coordinates[target_coordinate]
                                    target_pin = target_device.get_or_create_pin(tokens[1])
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
                            target_pin = target_device.get_or_create_pin(tokens[1])
                        # Everything else (i.e. non-dotted names) are the strange case
                        # where an alias points to a different alias.
                        else:
                            target_device = self.alias_device
                            target_pin = target_device.get_or_create_pin(connection)
                        # Cross-connect
                        target_pin.add_connection(alias_pin)
                        alias_pin.add_connection(target_pin)

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
                        else:
                            device.set_type(self.get_device_type(type_name))

                    # Register the pins
                    for pin_name, _ in yaml_device["pins"].items():
                        local_pin_name = pin_name.upper()
                        if local_pin_name in device.pins:
                            raise Exception("Duplicate definition of pin " + local_pin_name + \
                                            " on device " + device_name)
                        local_pin = Pin(device, local_pin_name)
                        device.pins[local_pin_name] = local_pin

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
                                    target_device = self.get_or_create_device(tokens[0])
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
                    # Figure out if any of the pins on the node are aliases
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

                    

  




    

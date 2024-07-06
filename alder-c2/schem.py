component_types = [ "r", "r2", "sw", "c", "l", "v", "i" ]

class Component:
    def __init__(self, name: str, type: str, use_io_names: list[str], params: map = None):
        self.name = name
        self.type = type 
        self.use_io_names = use_io_names
        self.params = params

    def visit_leaves(self, parent_name: str, instance_name: str, local_names: list[str], visitor):
        # Perform the translation on any properties that need
        expanded_params = {}
        for l, v in self.params.items():
            if parent_name:
                expanded_params[l] = str(v).replace("@parent", parent_name)
            else:
                expanded_params[l] = v
        visitor(instance_name, self.type, local_names, expanded_params)

def translate_node_names(parent_instance_name: str, use_io_names: list[str], 
    parent_def_io_names: list[str], parent_use_io_names: list[str]):
    if len(parent_def_io_names) != len(parent_use_io_names):
        raise Exception("Wrong number of IOs")
    result = []
    for use_io_name in use_io_names:
        # Global names are unchanged
        if use_io_name[0] == "!":
            result.append(use_io_name)
        # See if the components io is connected to one of the parent's defined 
        # IOs.  If so, then pull in the name used when instantiating the parent. 
        # (i.e passing a node down one level)
        elif use_io_name in parent_def_io_names:
            i = parent_def_io_names.index(use_io_name)
            result.append(parent_use_io_names[i])
        # Otherwise, this is a new local node name
        else:
            if parent_instance_name:
                result.append(parent_instance_name + "." + use_io_name)
            else:
                result.append(use_io_name)
    return result

class Circuit:
    
    def __init__(self, components: list[Component], def_io_names: list[str]):
        self.components = components
        self.def_io_names = def_io_names

    def visit_leaves(self, circuits, parent_name: str, use_io_names: list[str], visitor):
        """
        Visits each lowest-level component, instantiating sub-circuits as needed.

        Visitor parameters:

            visitor(instance_name: str, type: str, io_names: list, param_map: map)
        """
        for comp in self.components:
            if parent_name:
                comp_name = parent_name + "." + comp.name
            else:
                comp_name = comp.name
            # Make the node names for the hook-up
            local_names = translate_node_names(parent_name, comp.use_io_names, self.def_io_names, use_io_names)
            if comp.type in component_types:
                comp.visit_leaves(parent_name, comp_name, local_names, visitor)
            else:
                circuit = circuits[comp.type]
                circuit.visit_leaves(circuits, comp_name, local_names, visitor)

def test_1():

    circuits = {}

    c0_parts = []
    c0_parts.append(Component("r1", "r", [ "a", "x" ], { "r": 1.5 } ))
    c0_parts.append(Component("r2", "r", [ "x", "b" ], { "r": 2.5, "n": "@parent.r1" } ))
    c0_parts.append(Component("c1", "c", [ "a", "b" ], { "c": 200 } ))
    c0_parts.append(Component("c2", "c", [ "!vp48", "b" ], { "c": 200 } ))
    # This circuit has two inputs:
    c0 = Circuit(c0_parts, [ "a", "b" ])
    circuits["c0"] = c0

    c1_parts = []
    c1_parts.append(Component("r1", "r", [ "w", "y" ], { "r": 5 }))
    # Here we are calling out a sub-circuit
    c1_parts.append(Component("x0", "c0", [ "y", "x" ]))
    c1_parts.append(Component("v1", "v", [ "0", "!vp48" ], { "v": 48 }))
    # This circuit has two inputs:
    c1 = Circuit(c1_parts, [ "w", "x" ])

    # Instantiate an instance of the the c1 circuit
    def v(name, type, io_names, params):
        print(type, name, io_names, params)
    c1.visit_leaves(circuits, None, [ "g", "h" ], v)

def test_2(v):

    circuits = {}

    c0_parts = []
    c0_parts.append(Component("p_sense", "v", [ "p0", "px" ], { "v": 0 } ))
    c0_parts.append(Component("p_coil", "r", [ "px", "p1" ], { "r": 10 } ))
    c0_parts.append(Component("h_sense", "v", [ "h0", "hx" ], { "v": 0 } ))
    c0_parts.append(Component("h_coil", "r", [ "hx", "h1" ], { "r": 10 } ))
    # Normally open path: high resistance by default
    c0_parts.append(Component("rno", "r2", [ "no", "op" ], 
            { "r0": 10000000, "r1": 1, "s0": "@parent.p_sense", "s1": "@parent.h_sense", } ))
    # Normally closed path: low resistance by default
    c0_parts.append(Component("rnc", "r2", [ "nc", "op" ], 
            { "r0": 1, "r1": 10000000, "s0": "@parent.p_sense", "s1": "@parent.h_sense", } ))
    c0 = Circuit(c0_parts, [ "p0", "p1", "h0", "h1", "nc", "op", "no" ])
    circuits["relay"] = c0

    l0_parts = []
    l0_parts.append(Component("sense", "v", [ "a", "x" ], { "v": 0 } ))
    l0_parts.append(Component("filament", "r", [ "x", "b" ], { "r": 10 } ))
    l0 = Circuit(l0_parts, [ "a", "b" ])
    circuits["bulb"] = l0

    c1_parts = []
    # Battery that powers the relay
    c1_parts.append(Component("v0", "v", [ "a", "b"], { "v": 48 }))
    # Switch that controls the relay
    c1_parts.append(Component("sw0", "sw", [ "b", "0"], { "r0": 10000000, "r1": 1 }))
    # Light for NO
    c1_parts.append(Component("l_nc", "bulb", [ "nc_l", "0"] ))
    # Light for NC
    c1_parts.append(Component("l_no", "bulb", [ "no_l", "0"] ))
    # Power for light
    c1_parts.append(Component("v1", "v", [ "f", "0"], { "v": 48 }))
    # Relay
    c1_parts.append(Component("x0", "relay", [ "a", "0", "a", "0", "nc_l", "f", "no_l" ]))
    c1 = Circuit(c1_parts, [ "w", "x" ])

    c1.visit_leaves(circuits, None, [ "a", "b" ], v)

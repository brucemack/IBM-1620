import network as net 

class Component:
    def __init__(self, name: str, type: str, use_io_names: list[str], params: map = None):
        self.name = name
        self.type = type 
        self.use_io_names = use_io_names
        self.params = params

    def visit_leaves(self, instance_name: str, local_names: list[str], visitor):
        visitor(instance_name, self.type, local_names, self.params)

def translate_node_names(parent_instance_name: str, use_io_names: list[str], 
    parent_def_io_names: list[str], parent_use_io_names: list[str]):
    if len(parent_def_io_names) != len(parent_use_io_names):
        raise Exception("Wrong number of IOs")
    result = []
    for use_io_name in use_io_names:
        # See if the components io is connected to one of the parent's defined 
        # IOs.  If so, then pull in the name used when instantiating the parent. 
        # (i.e passing a node down one level)
        if use_io_name in parent_def_io_names:
            i = parent_def_io_names.index(use_io_name)
            result.append(parent_use_io_names[i])
        # Otherwise, this is a local node name
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
            if comp.type == "r" or comp.type == "c" or comp.type == "v" or comp.type == "l" or comp.type == "i":
                comp.visit_leaves(comp_name, local_names, visitor)
            else:
                circuit = circuits[comp.type]
                circuit.visit_leaves(circuits, comp_name, local_names, visitor)

def test_1():

    circuits = {}

    c0_parts = []
    c0_parts.append(Component("r1", "r", [ "a", "x" ], { "r": 1.5 } ))
    c0_parts.append(Component("r2", "r", [ "x", "b" ], { "r": 2.5 } ))
    c0_parts.append(Component("c1", "c", [ "a", "b" ], { "c": 200 } ))
    # This circuit has two inputs:
    c0 = Circuit(c0_parts, [ "a", "b" ])
    circuits["c0"] = c0

    c1_parts = []
    c1_parts.append(Component("r1", "r", [ "w", "y" ], { "r": 5 }))
    # Here we are calling out a sub-circuit
    c1_parts.append(Component("x0", "c0", [ "y", "x" ]))
    # This circuit has two inputs:
    c1 = Circuit(c1_parts, [ "w", "x" ])

    # Instantiate an instance of the the c1 circuit
    def v(name, type, io_names, params):
        print(type, name, io_names, params)
    c1.visit_leaves(circuits, None, [ "g", "h" ], v)

test_1()

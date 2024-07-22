component_types = [ "r", "r2", "sw", "c", "l", "v", "i", "d", "co" ]

class Component:
    def __init__(self, name: str, type: str, use_io_names: list[str], params: map = None):
        self.name = name
        self.type = type 
        self.use_io_names = use_io_names
        self.params = params

    def __str__(self):
        return self.name + " " + self.type + " " + str(self.use_io_names) + " " + str(self.params)

    def visit_leaves(self, parent_name: str, instance_name: str, local_names: list[str], visitor):
        # Perform the translation on any properties that need
        expanded_params = {}
        if self.params:
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


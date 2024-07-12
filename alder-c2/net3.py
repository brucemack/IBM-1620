import math

def traverse_graph_recursive_2(node_name_to_devices, name_to_device, 
                               start_node_name, visited_nodes, path, visitor, prevent_duplicates = True):
    # Prevent duplicate visits
    if prevent_duplicates and start_node_name in visited_nodes:
        return
    visited_nodes.add(start_node_name)
    # The return decides whether we continue to traverse
    cont = visitor(start_node_name, path)
    if cont:
        for neighbor_device in node_name_to_devices[start_node_name]:
            for neighbor_name in neighbor_device.get_connected_node_names():
                # Avoid loops
                if not neighbor_name in path:
                    # Recurse.  The path is copied and extended before continuing
                    # the traversal.
                    new_path = path.copy()
                    new_path.append(neighbor_name)
                    traverse_graph_recursive_2(node_name_to_devices, name_to_device, 
                                                neighbor_name, visited_nodes, new_path, 
                                                visitor, prevent_duplicates)

def traverse_graph_2(node_name_to_devices, name_to_device, start_node_name_list, visitor, 
                     prevent_duplicates = True):
    # This set keeps track of what we have seen already
    visited_nodes = set()
    # Visit every node in the graph, but keep in mind that some
    # will be visited indirectly.
    for start_node_name in start_node_name_list:
        traverse_graph_recursive_2(node_name_to_devices, name_to_device, 
                                   start_node_name, visited_nodes, 
                                   [ start_node_name ], visitor, prevent_duplicates)
        
class Mapper:

    def __init__(self):
        self.map = {}

    def clear(self):
        self.map.clear()

    def get_size(self): return len(self.map)

    def register(self, n):
        if n == "0":
            return -1
        if not n in self.map:
            self.map[n] = len(self.map)
        return self.map[n]

    def get(self, n: str):
        if n == "0":
            return -1
        if not n in self.map:
            raise Exception("Invalid node: " + n)
        return self.map[n]
    
    def diff(self, x, plus_name, minus_name):
        return x[self.get(plus_name)] - x[self.get(minus_name)]
    
    def visit_all(self, visitor):
        for n, i in self.map.items():
            visitor(n, i)

class Device2:

    def __init__(self, name: str, node_name_0: str, node_name_1: str):
        self.name = name
        self.node_name_0 = node_name_0
        self.node_name_1 = node_name_1
        self.i0 = -1
        self.i1 = -1

    def get_name(self): return self.name

    def register_node_names(self, name_to_index):
        self.i0 = name_to_index.register(self.node_name_0)
        self.i1 = name_to_index.register(self.node_name_1)

    def get_connected_node_names(self):
        return [ self.node_name_0, self.node_name_1 ]

class Resistor(Device2):

    def __init__(self, name: str, node_name_0: str, node_name_1: str, r: float):
        super().__init__(name, node_name_0, node_name_1)
        self.r = r

    def stamp(self, A, b, x_t, x_n):
        g = 1 / self.r
        if self.i0 == -1:
            A[self.i1][self.i1] = A[self.i1][self.i1] + g
        elif self.i1 == -1:
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
        else:
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
            A[self.i0][self.i1] = A[self.i0][self.i1] + -g
            A[self.i1][self.i0] = A[self.i1][self.i0] + -g
            A[self.i1][self.i1] = A[self.i1][self.i1] + g

class Switch(Device2):
    """
    This switch uses two different resistances.
    """

    def __init__(self, name: str, node_name_0: str, node_name_1: str, state: bool = False):
        super().__init__(name, node_name_0, node_name_1)
        self.r0 = 100000000
        self.r1 = 0.001
        self.state = state

    def set_state(self, s: bool) -> bool:
        old_state = self.state
        self.state = s
        return old_state != self.state

    def stamp(self, A, b, x_t, x_n):
        r = self.r1 if self.state else self.r0
        g = 1 / r
        if self.i0 == -1:
            A[self.i1][self.i1] = A[self.i1][self.i1] + g
        elif self.i1 == -1:
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
        else:
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
            A[self.i0][self.i1] = A[self.i0][self.i1] + -g
            A[self.i1][self.i0] = A[self.i1][self.i0] + -g
            A[self.i1][self.i1] = A[self.i1][self.i1] + g

class Switch2(Device2):
    """ 
    This switch will not stamp into the matrix if it is open
    """
    def __init__(self, name: str, node_name_0: str, node_name_1: str, state: bool = False):
        super().__init__(name, node_name_0, node_name_1)
        self.r1 = 0.00001
        self.state = state

    def set_state(self, s: bool) -> bool:
        old_state = self.state
        self.state = s
        return old_state != self.state

    def get_connected_node_names(self):
        if self.state:
            return [ self.node_name_0, self.node_name_1 ]
        else:
            return [ ]

    def register_node_names(self, name_to_index):
        # Note that we don't register any nodes if the switch is off
        if self.state:        
            self.i0 = name_to_index.register(self.node_name_0)
            self.i1 = name_to_index.register(self.node_name_1)

    def stamp(self, A, b, x_t, x_n):
        # Note that we don't stamp the matrix if the switch is off
        if self.state:
            r = self.r1 
            g = 1 / r
            if self.i0 == -1:
                A[self.i1][self.i1] = A[self.i1][self.i1] + g
            elif self.i1 == -1:
                A[self.i0][self.i0] = A[self.i0][self.i0] + g
            else:
                A[self.i0][self.i0] = A[self.i0][self.i0] + g
                A[self.i0][self.i1] = A[self.i0][self.i1] + -g
                A[self.i1][self.i0] = A[self.i1][self.i0] + -g
                A[self.i1][self.i1] = A[self.i1][self.i1] + g

class CurrentSource(Device2):

    def __init__(self, name: str, node_name_0: str, node_name_1: str, i: float):
        super().__init__(name, node_name_0, node_name_1)
        self.i = i

    def stamp(self, A, b, x_t, x_n):
        if self.i1 == -1:
            b[self.i0] = b[self.i0] + -self.i
        elif self.i0 == -1:
            b[self.i1] = b[self.i1] + -self.i
        else:
            b[self.i0] = b[self.i0] + -self.i
            b[self.i1] = b[self.i1] + self.i

class VoltageSource(Device2):

    def __init__(self, name: str, node_name_0: str, node_name_1: str, v: float):
        super().__init__(name, node_name_0, node_name_1)
        self.v = v

    def register_node_names(self, name_to_index):
        super().register_node_names(name_to_index)
        self.iaux = name_to_index.register("#" + self.name)

    def stamp(self, A, b, x_t, x_n):
        # This is the case where the negative terminal is grounded
        if self.i1 == -1:
            A[self.i0][self.iaux] = A[self.i0][self.iaux] + 1
            A[self.iaux][self.i0] = A[self.iaux][self.i0] + 1
        elif self.i0 == -1:
            A[self.iaux][self.i1] = A[self.iaux][self.i1] + 1
            A[self.i1][self.iaux] = A[self.i1][self.iaux] + 1
        else:
            A[self.i0][self.iaux] = A[self.i0][self.iaux] + 1
            A[self.i1][self.iaux] = A[self.i1][self.iaux] + -1
            A[self.iaux][self.i0] = A[self.iaux][self.i0] + 1
            A[self.iaux][self.i1] = A[self.iaux][self.i1] + -1
        b[self.iaux] = b[self.iaux] + self.v

class Diode(Device2):
    """
    See this reference https://ltwiki.org/files/SPICEdiodeModel.pdf for information
    on how the negative voltages are handled.
    """
    def __init__(self, name: str, node_name_0: str, node_name_1: str):
        super().__init__(name, node_name_0, node_name_1)
        self.isat = 10e-15
        self.vt = 0.025
        self.max_vd = 0.8
        self.gmin = 1e-12
        self.N = 1

    # We are assuming that the 0 node is the positive node and the 1
    # node is the negative (i.e. current flows from 0->1)
    def stamp(self, A, b, x_t, x_n):
        a = 1 / self.vt
        # This is the case when the positive terminal (0) is grounded
        if self.i0 == -1:
            # The Vd is capped to avoid overflow
            vd = min(-x_n[self.i1], self.max_vd)
            if vd < -5 * self.vt:
                g = self.gmin
                # TODO: Check this sign
                i = -self.isat
            else:
                #g = a * math.exp(a * vd)
                #i = -((math.exp(a * vd) - 1) - a * math.exp(a * vd) * vd)
                deriv = (self.isat * a * math.exp( a * vd)) + self.gmin
                g = deriv
                i = (self.isat * (math.exp(a * vd) - 1)) + \
                    (self.gmin * vd) - \
                    (deriv * vd)
            # This current flows from gnd->1 (i.e. opposite to convention that
            # states that positive current leaves the node.
            i = -i
            A[self.i1][self.i1] = A[self.i1][self.i1] + g
            # IMPORTANT: Current flips sign on RHS
            b[self.i1] = b[self.i1] - i
        # This is the case when the negative terminal (1) is grounded.
        elif self.i1 == -1:
            # The Vd is capped to avoid overflow
            vd = min(x_n[self.i0], self.max_vd)
            if vd < -5 * self.vt:
                g = self.gmin
                i = -self.isat
            else:
                #g = a * math.exp(a * vd)
                # Positive current flows from 0->gnd
                #i = (math.exp(a * vd) - 1) - a * math.exp(a * vd) * vd
                deriv = (self.isat * a * math.exp( a * vd)) + self.gmin
                g = deriv
                i = (self.isat * (math.exp(a * vd) - 1)) + \
                    (self.gmin * vd) - \
                    (deriv * vd)
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
            # IMPORTANT: Sign flips when moved to RHS
            b[self.i0] = b[self.i0] - i
        # Positive voltage when i0 is higher than i1
        else:
            # The Vd is capped to avoid overflow
            vd = min(x_n[self.i0] - x_n[self.i1], self.max_vd)
            if vd < -5 * self.vt:
                #if self.get_name() == "d30":
                #    print(self.get_name(),"neg", vd)
                g = self.gmin
                i = -self.isat
            else:
                #g = a * math.exp(a * vd)
                # This is the positive flow of current from 0->1
                #i = (math.exp(a * vd) - 1) - a * math.exp(a * vd) * vd
                deriv = (self.isat * a * math.exp( a * vd)) + self.gmin
                g = deriv
                i = (self.isat * (math.exp(a * vd) - 1)) + \
                    (self.gmin * vd) - \
                    (deriv * vd)
                #if self.get_name() == "d30":
                #    print(self.get_name(), "pos", vd, 1 / g, i)
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
            A[self.i0][self.i1] = A[self.i0][self.i1] + -g
            A[self.i1][self.i0] = A[self.i1][self.i0] + -g
            A[self.i1][self.i1] = A[self.i1][self.i1] + g
            # IMPORTANT! Sign is flipped when the positive current flow moves 
            # to the RHS
            b[self.i0] = b[self.i0] - i
            b[self.i1] = b[self.i1] + i

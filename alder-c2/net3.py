import math

class Mapper:

    def __init__(self):
        self.map = {}

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
        return self.map[n]

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
        self.max_vd = 2
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
            A[self.i0][self.i0] = A[self.i0][self.i0] + g
            A[self.i0][self.i1] = A[self.i0][self.i1] + -g
            A[self.i1][self.i0] = A[self.i1][self.i0] + -g
            A[self.i1][self.i1] = A[self.i1][self.i1] + g
            # IMPORTANT! Sign is flipped when the positive current flow moves 
            # to the RHS
            b[self.i0] = b[self.i0] - i
            b[self.i1] = b[self.i1] + i

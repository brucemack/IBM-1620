
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

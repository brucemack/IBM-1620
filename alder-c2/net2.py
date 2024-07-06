import numpy as np

class Node:

    def __init__(self, name: str):
        self.name = name
        self.index = -1

    def set_index(self, i: int): self.index = i
    def get_index(self) -> int: return self.index
    def set_name(self, name: str): self.name = name
    def get_name(self) -> str: return self.name

class Edge:
    def __init__(self, name: str, a: Node, b: Node):
        self.name = name
        self.node_a = a
        self.node_b = b

    def get_name(self): return self.name

class Matrix:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.data = np.zeros((rows, cols))

    def add_term(self, r: int, c: int, v: float):
        self.data[r, c] = self.data[r, c] + v

    def clear(self):
        self.data = np.zeros((self.rows, self.cols))


class Vector:
    def __init__(self, size: int):
        self.size = size
        self.data = np.zeros((size))

    def add_term(self, r: int, v: float):
        self.data[r] = self.data[r] + v

    def clear(self):
        self.data = np.zeros((self.size))

class ResistorEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node, r: float):
        super().__init__(name, a, b)
        self.r = r

    def stamp(self, a_matrix, b_matrix, previous_x_matrix):

        g = 1 / self.r

        if self.node_a.get_index() == 0:
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1,  g)    
        elif self.node_b.get_index() == 0:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1,  g)    
        else:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1,  g)
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_b.get_index() - 1, -g)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_a.get_index() - 1, -g)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1,  g)

class CurrentControlledResistorEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node, n0: Node, n1: Node, r0: float, r1: float):
        super().__init__(name, a, b)
        self.n0 = n0
        self.n1 = n1
        self.r0 = r0
        self.r1 = r1
        self.thresh = 0.001

    def stamp(self, a_matrix, b_matrix, previous_x_matrix):

        # Figure out if either of the control nodes are above the threshold
        r = self.r0
        if self.n0 and previous_x_matrix[self.n0.get_index() - 1] > self.thresh:
            r = self.r1 
        elif self.n1 and previous_x_matrix[self.n1.get_index() - 1] > self.thresh:
            r = self.r1

        g = 1 / r

        if self.node_a.get_index() == 0:
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1, g)    
        elif self.node_b.get_index() == 0:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1, g)    
        else:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1, g)
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_b.get_index() - 1, -g)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_a.get_index() - 1, -g)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1, g)

# Positive current goes into the A node and out of the B node
class CurrentSourceEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node, i: float):
        super().__init__(name, a, b)
        self.i = i

    def stamp(self, a_matrix, b_vector, previous_x_matrix):
        if self.node_a.get_index() != 0:
            b_vector.add_term(self.node_a.get_index() - 1, -self.i)    
        if self.node_b.get_index() != 0:
            b_vector.add_term(self.node_b.get_index() - 1, self.i)    

class VoltageSourceEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node, aux_node: Node, v: float):
        super().__init__(name, a, b)
        self.aux_node = aux_node
        self.v = v

    def stamp(self, a_matrix, b_vector, previous_x_matrix):
        if self.node_a.get_index() != 0:
            a_matrix.add_term(self.node_a.get_index() - 1, self.aux_node.get_index() - 1, 1)    
            a_matrix.add_term(self.aux_node.get_index() - 1, self.node_a.get_index() - 1, 1)    
        if self.node_b.get_index() != 0:
            a_matrix.add_term(self.node_b.get_index() - 1, self.aux_node.get_index() - 1, -1)    
            a_matrix.add_term(self.aux_node.get_index() - 1, self.node_b.get_index() - 1, -1)    
        b_vector.add_term(self.aux_node.get_index() - 1, self.v)


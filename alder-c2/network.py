import numpy as np

class Node:

    def __init__(self, name: str):
        self.edges = []   
        self.name = name
        self.index = -1

    def set_index(self, i: int): self.index = i
    def get_index(self) -> int: return self.index
    def set_name(self, name: str): self.name = name
    def get_name(self) -> str: return self.name

class EdgeType:
    def __init__(self):
        pass

    def create(self):
        raise Exception("Create failed")

class Edge:
    def __init__(self, name: str, a: Node, b: Node):
        self.name = name
        self.node_a = a
        self.node_b = b

    def get_name(self): return self.name
    def get_aux_variable_count(self): return 0
    def assign_aux_variable(self, aux_index: int, mat_index: int): 
       raise Exception("Unexpected aux_index")
    def get_aux_variable(self, aux_index: int) -> int:
       raise Exception("Unexpected aux_index")

class Matrix:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.data = np.zeros((rows, cols))

    def add_term(self, r: int, c: int, v: float):
        self.data[r, c] = self.data[r, c] + v

class Vector:
    def __init__(self, size: int):
        self.size = size
        self.data = np.zeros((size))

    def add_term(self, r: int, v: float):
        self.data[r] = self.data[r] + v

class ResistorEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node):
        super().__init__(name, a, b)
        self.r = 0

    def set_r(self, r): self.r = r

    def stamp(self, a_matrix, b_matrix):
        if self.node_a.get_index() == 0:
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1, 1 / self.r)    
        elif self.node_b.get_index() == 0:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1, 1 / self.r)    
        else:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1, 1 / self.r)
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_b.get_index() - 1, -1 / self.r)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_a.get_index() - 1, -1 / self.r)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1, 1 / self.r)

# Positive current goes into the A node and out of the B node
class CurrentSourceEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node):
        super().__init__(name, a, b)
        self.i = 0

    def set_i(self, i): self.i = i

    def stamp(self, a_matrix, b_vector):
        if self.node_a.get_index() != 0:
            b_vector.add_term(self.node_a.get_index() - 1, -self.i)    
        if self.node_b.get_index() != 0:
            b_vector.add_term(self.node_b.get_index() - 1, self.i)    


class VoltageSourceEdge(Edge):

    def __init__(self, name: str, a: Node, b: Node):
        super().__init__(name, a, b)
        self.v = 0
        self.aux_index = 0

    def set_v(self, v): self.v = v

    def get_aux_variable_count(self): return 1
    
    def assign_aux_variable(self, aux_index: int, mat_index: int): 
        if aux_index == 0:
            self.aux_index = mat_index
        else:
            raise Exception("Unexpected aux_index")
        
    def get_aux_variable(self, aux_index: int) -> int:
        if aux_index == 0:
            return self.aux_index
        else:
            raise Exception("Unexpected aux_index")

    def stamp(self, a_matrix, b_vector):
        if self.node_a.get_index() != 0:
            a_matrix.add_term(self.node_a.get_index() - 1, self.aux_index - 1, 1)    
            a_matrix.add_term(self.aux_index - 1, self.node_a.get_index() - 1, 1)    
        if self.node_b.get_index() != 0:
            a_matrix.add_term(self.node_b.get_index() - 1, self.aux_index - 1, -1)    
            a_matrix.add_term(self.aux_index - 1, self.node_b.get_index() - 1, -1)    
        b_vector.add_term(self.aux_index - 1, self.v)

class ResistorEdgeType(EdgeType):

    def __init__(self):
        super().__init__()

    def create(self, name: str, a: Node, b: Node):
        return ResistorEdge(name, a, b)

class CurrentSourceEdgeType(EdgeType):

    def __init__(self):
        super().__init__()

    def create(self, name: str, a: Node, b: Node):
        return CurrentSourceEdge(name, a, b)

class VoltageSourceEdgeType(EdgeType):

    def __init__(self):
        super().__init__()

    def create(self, name: str, a: Node, b: Node):
        return VoltageSourceEdge(name, a, b)

def connect_nodes(name: str, a: Node, b: Node, edge_type: EdgeType):
    edge = edge_type.create(name, a, b, edge_type)
    a.add_edge(edge)
    b.add_edge(edge)


# Demonstrate stamping of some voltage sources and resistors
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
    def __init__(self, a: Node, b: Node):
        self.node_a = a
        self.node_b = b

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
        print("v add_term", r, v)
        self.data[r] = self.data[r] + v

class ResistorEdge(Edge):

    def __init__(self, a: Node, b: Node):
        super().__init__(a, b)
        self.r = 0

    def set_r(self, r): self.r = r

    def stamp(self, a_matrix, b_matrix):
        if self.node_a.get_index() == 0:
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1, 1 / self.r)    
        if self.node_b.get_index() == 0:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1, 1 / self.r)    
        else:
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_a.get_index() - 1, 1 / self.r)
            a_matrix.add_term(self.node_a.get_index() - 1, self.node_b.get_index() - 1, -1 / self.r)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_a.get_index() - 1, -1 / self.r)
            a_matrix.add_term(self.node_b.get_index() - 1, self.node_b.get_index() - 1, 1 / self.r)

# Positive current comes out of the A node and into the B node
class CurrentSourceEdge(Edge):

    def __init__(self, a: Node, b: Node):
        super().__init__(a, b)
        self.i = 0

    def set_i(self, i): self.i = i

    def stamp(self, a_matrix, b_vector):
        if self.node_a.get_index() != 0:
            b_vector.add_term(self.node_a.get_index() - 1, -self.i)    
        if self.node_b.get_index() != 0:
            b_vector.add_term(self.node_b.get_index() - 1, self.i)    

class ResistorEdgeType(EdgeType):

    def __init__(self):
        super().__init__()

    def create(self, a: Node, b: Node):
        return ResistorEdge(a, b)

class CurrentSourceEdgeType(EdgeType):

    def __init__(self):
        super().__init__()

    def create(self, a: Node, b: Node):
        return CurrentSourceEdge(a, b)

def connect_nodes(a: Node, b: Node, edge_type: EdgeType):
    edge = edge_type.create(a, b, edge_type)
    a.add_edge(edge)
    b.add_edge(edge)


rt = ResistorEdgeType()
cst = CurrentSourceEdgeType()

nodes = []
edges = []

node_0 = Node("0")
node_1 = Node("1")
node_2 = Node("2")
node_3 = Node("3")

nodes.append(node_0)
nodes.append(node_1)
nodes.append(node_2)
nodes.append(node_3)

i = 0
for node in nodes:
    node.set_index(i)
    i = i + 1

ia = cst.create(node_1, node_0)
ia.set_i(-5)
edges.append(ia)

ra = rt.create(node_1, node_2)
ra.set_r(1)
edges.append(ra)

rb = rt.create(node_2, node_0)
rb.set_r(2)
edges.append(rb)

rc = rt.create(node_2, node_3)
rc.set_r(3)
edges.append(rc)

rd = rt.create(node_3, node_0)
rd.set_r(4)
edges.append(rd)

a = Matrix(3, 3)
b = Vector(3)

# Stamp all devices
for edge in edges:
    edge.stamp(a, b)

print(a.data)    
print(b.data)

ainv = np.linalg.inv(a.data)
print("Result", ainv.dot(b.data))



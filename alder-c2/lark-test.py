import lark

parser = lark.Lark.open("./logic.lark")

#tree = parser.parse("c = a | b; d = 1;")
tree = parser.parse(open("./mechanical.logic").read())
#print(tree.pretty())

class DeclarationProcessor(lark.visitors.Transformer):

    def __init__(self, input_names, reg_names):
        self.input_names = input_names
        self.reg_names = reg_names

    def identifierlist_start(self, tree):
        return [ tree[0] ]

    def identifierlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, tree[0])
        return l

    def declaration_input(self, tree):
        self.input_names.extend(tree[1])

    def declaration_reg(self, tree):
        self.reg_names.extend(tree[1])

    def IDENTIFIER(self, tree):
        return str(tree)

class Evaluator(lark.visitors.Transformer):

    def __init__(self, value_map, next_value_map):
        self.value_map = value_map
        self.next_value_map = next_value_map

    def assignment_eq(self, tree):
        self.value_map[tree[0]] = tree[1]

    def assignment_eq2(self, tree):
        self.next_value_map[tree[0]] = tree[1]

    def logicalexp_or(self, tree):
        return tree[0] == True or tree[1] == True

    def logicalexp_and(self, tree):
        return tree[0] == True and tree[1] == True

    def logicalexp_xor(self, tree):
        return (tree[0] == True and tree[1] == False) or \
               (tree[0] == False and tree[1] == True)

    def logicalexp_not(self, tree):
        return (tree[0] != True)

    def logicalexp_paren(self, tree):
        return tree[0]

    def logicalexp_id(self, tree):
        return self.value_map[tree[0]]

    def IDENTIFIER(self, tree):
        return str(tree)

# Process declarations (one time)
input_names = []
reg_names = []
d = DeclarationProcessor(input_names, reg_names)
d.transform(tree)
print("Inputs:", input_names)
print("Regs:", reg_names)

value_map = {}

# Setup variable
for n in input_names:
    value_map[n] = False
for n in reg_names:
    value_map[n] = False

# Time Loop
    
for t in range(0, 8):

    print(t, "-----------------------------")

    if t == 1:
        value_map["r30_pick_current"] = True
        value_map["r10_pick_current"] = True
    elif t == 2:
        value_map["r30_pick_current"] = False
        value_map["r10_pick_current"] = False
    elif t == 4:
        value_map["r10_trip_current"] = True
    elif t == 5:
        value_map["r10_trip_current"] = False


    next_value_map = {}
    ev = Evaluator(value_map, next_value_map)
    ev.transform(tree)
    #print("Values", value_map)
    #print("Next Values", next_value_map)
    print(value_map["r30_1_no"], value_map["r10_1_no"])

    # Copy values down
    for n, v in next_value_map.items():
        value_map[n] = v





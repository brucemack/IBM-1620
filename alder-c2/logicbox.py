import lark

def make_global_name(namespace: str, local_name: str):
    return namespace + "." + local_name

# ----- Expression Related ---------------------------------------------------

class Value: 

    def __init__(self, v):
        self.value = v

    def get_bool(self):
        return bool(self.value)

class Expression:
    def evaluate(self, namespace: str, variable_declarations, \
                 value_state: dict[str, Value]) -> Value:
        raise Exception("Not implemented")
    
class Variable(Expression):

    def __init__(self, local_name):
        self.local_name = local_name 

    def evaluate(self, namespace: str, variable_declarations: dict[str, Expression], \
                 value_state: dict[str, Value]) -> Value:
        global_name = make_global_name(namespace, self.local_name)
        # If the variable has not been computed in this cycle then perform the 
        # computation and hold the result for next time.
        if not global_name in value_state:
            exp = variable_declarations[global_name]
            value_state[global_name] = exp.evaluate(namespace, variable_declarations, value_state)
        return value_state[global_name]

class Constant(Expression):

    def __init__(self, value):
        self.value = value

    def evaluate(self, namespace: str, variable_declarations, \
                 value_state: dict[str, Value]) -> Value:
        return self.value

class BinaryExpresion(Expression):

    def __init__(self, type, lhs, rhs):
        self.type = type 
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, namespace: str, variable_declarations, \
                 value_state: dict[str, Value]) -> Value:
        lhs_value = self.lhs.evaluate(namespace, variable_declarations, value_state)
        rhs_value = self.rhs.evaluate(namespace, variable_declarations, value_state)
        return self.eval(lhs_value, rhs_value)
    
    def eval(self, lhs: Value, rhs: Value) -> Value:
        if self.type == "or":
            return Value(lhs.get_bool() or rhs.get_bool())
        elif self.type == "and":
            return Value(lhs.get_bool() and rhs.get_bool())
        else:
            raise Exception("Invalid operation type")

class UnaryExpresion(Expression):

    def __init__(self, type, lhs):
        self.type = type 
        self.lhs = lhs

    def evaluate(self, namespace: str, variable_declarations, \
                 value_state: dict[str, Value]) -> Value:
        lhs_value = self.lhs.evaluate(namespace, variable_declarations, value_state)
        return self.eval(lhs_value)
    
    def eval(self, lhs: Value)-> Value:
        if self.type == "not":
            return Value(not lhs.get_bool())
        else:
            raise Exception("Invalid operation type")
        




class Module:
    def __init__(self, name, ports, body):
        self.name = name
        self.ports = ports
        self.body = body

    def __repr__(self):
        return "Module: " + self.name + " " + str(self.ports) + " " + str(self.body)


class AssignmentStatement:

    def __init__(self, lhs_name, type, rhs_exp):
        self.lhs_name = lhs_name
        self.type = type 
        self.rhs_exp

    def execute(self, namespace: str, value_state):
        pass 

class PortDeclaration:

    def __init__(self, io, wr, name):
        self.io = io
        self.wr = wr 
        self.name = name

    def fill_in(self, other):
        if self.io is None: self.io = other.io
        if self.wr is None: self.wr = other.wr

    def __repr__(self) -> str:
        io = self.io 
        if io is None:
            io = "?"
        wr = self.wr 
        if wr is None:
            wr = "?"
        return io + "/" + wr + "/" + self.name

class Declaration:

    def __init__(self, wr, name):
        self.wr = wr 
        self.name = name

    def __repr__(self) -> str:
        wr = self.wr 
        if wr is None:
            wr = "?"
        return wr + "/" + self.name

# ----- Parse Tree Transformers ---------------------------------------------------------

class ModuleDeclarationProcessor(lark.visitors.Transformer):

    def __init__(self):
        pass

    def moduledeclaration(self, tree):
        # Carry forward declaration information as needed
        previous_pd = PortDeclaration("INPUT", "WIRE", None)
        for pd in tree[2]:
            pd.fill_in(previous_pd)
            previous_pd = pd
        return Module(str(tree[1]), tree[2], tree[3])

    def portdeclaration_full(self, tree):
        return PortDeclaration( tree[0].type, tree[1].type, str(tree[2]) )

    def portdeclaration_default(self, tree):
        return PortDeclaration( None, None, str(tree[0]) )

    # This will be a list of port declarations
    def portdeclarationlist_start(self, tree):
        r =  [ tree[0] ]
        return r

    def portdeclarationlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, tree[0])
        return l

# This processor goes through and extracts all of the declarations
class DeclarationProcessor(lark.visitors.Transformer):

    def __init__(self):
        pass

    def declaration_wire(self, tree):
        return [ Declaration("WIRE", x) for x in tree[1] ]

    def declaration_reg(self, tree):
        return [ Declaration("REG", x) for x in tree[1] ]

    def identifierlist_start(self, tree):
        return [ str(tree[0]) ]

    def identifierlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, str(tree[0]))
        return l

    def statement_declaration(self, tree):
        return tree[0]

    def statement_assignment(self, tree):
        return [ ]

    def statement_moduleinstantiation(self, tree):
        return [ ]

    def statementlist_start(self, tree):
        return tree[0]

    def statementlist_add(self, tree):
        l = tree[1].copy()
        l.extend(tree[0])
        return l

class Evaluator(lark.visitors.Transformer):

    def __init__(self, value_map, next_value_map):
        self.value_map = value_map
        self.next_value_map = next_value_map

    def assignment_eq(self, tree):
        self.value_map[tree[0]] = tree[1]

    def assignment_eq2(self, tree):
        self.next_value_map[tree[0]] = tree[1]

    def exp_or(self, tree):
        return tree[0] == True or tree[1] == True

    def exp_and(self, tree):
        return tree[0] == True and tree[1] == True

    def exp_xor(self, tree):
        return (tree[0] == True and tree[1] == False) or \
               (tree[0] == False and tree[1] == True)

    def exp_lt(self, tree):
        return tree[0] < tree[1]

    def exp_lte(self, tree):
        return tree[0] <= tree[1]

    def exp_gt(self, tree):
        return tree[0] > tree[1]

    def exp_gte(self, tree):
        return tree[0] >= tree[1]

    def exp_not(self, tree):
        return (tree[0] != True)

    def exp_paren(self, tree):
        return tree[0]

    def exp_id(self, tree):
        return self.value_map[tree[0]]

    def exp_number(self, tree):
        return int(tree[0])

    def IDENTIFIER(self, tree):
        return str(tree)

    def SIGNED_NUMBER(self, tree):
        return str(tree)

# We only process the angles that really matter    
significant_angles = [ 0, 1, 2, 3,
                    49, 50, 51, 52,
                    98, 99, 100, 101, 
                    170, 171, 172, 173,
                    219, 220, 221, 222, 223,
                    299, 300, 301, 302,
                    309, 310, 311, 312,
                    359 ]
"""
class LogicBox:

    def __init__(self, logic_file_name, value_source):
        self.value_source = value_source
        parser = lark.Lark.open("./logic.lark")
        with open(logic_file_name) as lf:
            self.tree = parser.parse(lf.read())
        self.tick_count = 0
        #print(self.tree.pretty())

        # Process declarations (one time)
        self.input_names = []
        self.reg_names = []
        d = ModuleDeclarationProcessor(self.input_names, self.reg_names)
        d.transform(self.tree)
        #print("Inputs:", self.input_names)
        #print("Regs:", self.reg_names)

        self.value_map = {}

        # Initialize varaibles
        for n in self.input_names:
            self.value_map[n] = False
        for n in self.reg_names:
            self.value_map[n] = False

        self.value_map["_angle"] = 0
        self.value_map["_cycle"] = 0

    def get_input_names(self) -> list[str]:
        return self.input_names.copy()

    def get_names(self) -> list[str]:
        result = []
        for name, _ in self.value_map.items():
            result.append(name)
        return result

    def get(self, name: str):
        return self.value_map[name]

    def tick(self):

        global significant_angles

        # Setup input
        for n in self.input_names:
            self.value_map[n] = self.value_source.get(n)

        sa_ptr = self.tick_count % (len(significant_angles))
        sa_cycle = int(self.tick_count / (len(significant_angles)))
        self.value_map["_angle"] = significant_angles[sa_ptr]
        self.value_map["_cycle"] = sa_cycle

        next_value_map = {}
        ev = Evaluator(self.value_map, next_value_map)
        ev.transform(self.tree)

        # Copy values down
        for n, v in next_value_map.items():
            self.value_map[n] = v

        self.tick_count = self.tick_count + 1
"""
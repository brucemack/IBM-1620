import lark

def make_global_name(namespace: str, local_name: str):
    if namespace:
        return namespace + "." + local_name
    else:
        return local_name

# ----- Expression Related ---------------------------------------------------

class Value: 

    def __init__(self, v):
        self.value = v

    def get_bool(self):
        return bool(self.value)
    
    def __repr__(self) -> str:
        return str(self.value)

class Expression:
    def evaluate(self, assignment_0_map, value_state: dict[str, Value]) -> Value:
        raise Exception("Not implemented")
    
class VariableExpression(Expression):

    def __init__(self, name):
        self.name = name 

    def evaluate(self, assignment_0_map: dict[str, Expression], \
                 value_state: dict[str, Value]) -> Value:
        # If the variable has not been computed in this cycle then perform the 
        # computation and hold the result for next time.
        if not self.name in value_state:
            # Get the RHS expression that defines the variable
            exp = assignment_0_map[self.name]
            # Evaluate the expression and hold for future use
            value_state[self.name] = exp.evaluate(assignment_0_map, value_state)
        return value_state[self.name]

    def __repr__(self) -> str:
        return self.name

class ConstantExpression(Expression):

    def __init__(self, value: Value):
        self.value = value

    def evaluate(self, assignment_0_map: dict[str, Expression], \
                 value_state: dict[str, Value]) -> Value:
        return self.value

    def __repr__(self):
        return str(self.value)

class BinaryExpression(Expression):

    def __init__(self, type, lhs, rhs):
        self.type = type 
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, assignment_0_map: dict[str, Expression], value_state: dict[str, Value]) -> Value:
        lhs_value = self.lhs.evaluate(assignment_0_map, value_state)
        rhs_value = self.rhs.evaluate(assignment_0_map, value_state)
        return self.eval(lhs_value, rhs_value)
    
    def eval(self, lhs: Value, rhs: Value) -> Value:
        if self.type == "or":
            return Value(lhs.get_bool() or rhs.get_bool())
        elif self.type == "and":
            return Value(lhs.get_bool() and rhs.get_bool())
        else:
            raise Exception("Invalid operation type")
        
    def __repr__(self):
        return "(" + str(self.lhs) + " " + self.type + " " + str(self.rhs) + ")"

class UnaryExpression(Expression):

    def __init__(self, type, lhs):
        self.type = type 
        self.lhs = lhs

    def evaluate(self, assignment_0_map: dict[str, Expression], value_state: dict[str, Value]) -> Value:
        lhs_value = self.lhs.evaluate(assignment_0_map, value_state)
        return self.eval(lhs_value)
    
    def eval(self, lhs: Value)-> Value:
        if self.type == "not":
            return Value(not lhs.get_bool())
        else:
            raise Exception("Invalid operation type")
    
# ----- Statement Related -------------------------------------------------------

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
        if len(tree) == 5:
            # Carry forward declaration information as needed
            previous_pd = PortDeclaration("INPUT", "WIRE", None)    
            for pd in tree[2]:
                pd.fill_in(previous_pd)
                previous_pd = pd
            return Module(str(tree[1]), tree[2], tree[3])
        elif len(tree) == 4:
            return Module(str(tree[1]), [], tree[2])

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

class ExpressionTransformer(lark.visitors.Transformer):

    def __init__(self, base_name):
        self.base_name = base_name

    def exp_or(self, tree):
        return BinaryExpression("or", tree[0], tree[1])

    def exp_and(self, tree):
        return BinaryExpression("or", tree[0], tree[1])

    def exp_xor(self, tree):
        return BinaryExpression("xor", tree[0], tree[1])

    def exp_lt(self, tree):
        return BinaryExpression("lt", tree[0], tree[1])

    def exp_lte(self, tree):
        return BinaryExpression("lte", tree[0], tree[1])

    def exp_gt(self, tree):
        return BinaryExpression("gt", tree[0], tree[1])

    def exp_gte(self, tree):
        return BinaryExpression("gte", tree[0], tree[1])

    def exp_not(self, tree):
        return UnaryExpression("not", tree[0])

    def exp_paren(self, tree):
        return tree[0]

    def exp_id(self, tree):
        return VariableExpression(make_global_name(self.base_name, str(tree[0])))

    def exp_number(self, tree):
        return ConstantExpression(Value(int(str(tree[0]))))

# Creates a list of tuples
class ParameterListTransformer(lark.visitors.Transformer):

    def parameterlist_start(self, tree):
        return [ tree[0] ]

    def parameterlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, tree[0])
        return l
    
    def parameter(self, tree):
        return (str(tree[0]), str(tree[1]))

class IdentifierListTransformer(lark.visitors.Transformer):

    def __init__(self, base_name):
        self.base_name = base_name

    def identifierlist_start(self, tree):
        return [ make_global_name(self.base_name, str(tree[0])) ]

    def identifierlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, make_global_name(self.base_name, str(tree[0])))
        return l

class StatementVisitor(lark.visitors.Visitor):

    def __init__(self, modules, assignment_0_map, assignment_1_map, register_list, base_name):
        self.modules = modules
        self.assignment_0_map = assignment_0_map
        self.assignment_1_map = assignment_1_map
        self.register_list = register_list
        self.base_name = base_name 

    def statement_declaration(self, tree):
        if str(tree.children[0]).upper() == "REG":
            self.register_list.extend(
                IdentifierListTransformer(self.base_name).transform(tree.children[1]))

    def statement_assignment(self, tree):
        lhs_name = str(tree.children[0])
        # Transform the expression 
        exp = ExpressionTransformer(self.base_name).transform(tree.children[2])
        if str(tree.children[1]) == "=":
            self.assignment_0_map[make_global_name(self.base_name, lhs_name)] = exp
        elif str(tree.children[1]) == "<=":
            self.assignment_1_map[make_global_name(self.base_name, lhs_name)] = exp
        else:
            raise Exception("Invalid operation")

    def statement_moduleinstantiation(self, tree):
        module_name = str(tree.children[0])
        module = self.modules[module_name]
        instance_name = str(tree.children[1])
        parameter_map = {}
        for parameter in ParameterListTransformer().transform(tree.children[2]):
            parameter_map[parameter[0]] = parameter[1]
        # Create the assignment statements for the ports
        for port in module.ports:
            if not port.name in parameter_map:
                raise Exception("Parameter for " + module_name + " not found: " + port.name)
            if port.io == "INPUT":
                # We are assuming that the parameter assignments happen immediately
                self.assignment_0_map[make_global_name(self.base_name, instance_name + "." + port.name)] = \
                    VariableExpression(make_global_name(self.base_name, parameter_map[port.name]))
            elif port.io == "OUTPUT":
                # We are assuming that the parameter assignments happen immediately
                self.assignment_0_map[make_global_name(self.base_name, parameter_map[port.name])] = \
                    VariableExpression(make_global_name(self.base_name, instance_name + "." + port.name))
                if port.wr == "REG":
                    self.register_list.append(
                        make_global_name(self.base_name, instance_name + "." + port.name))
        # Recurse
        instantiate_recursive(self.modules, \
                              self.assignment_0_map, self.assignment_1_map, self.register_list, \
                              module_name, make_global_name(self.base_name, instance_name))

    


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

def instantiate_recursive(modules, assignment_0_map, assignment_1_map, register_list: list[str],
                          module_name, base_name):
    
    module = modules[module_name]

    # No input/output wires for the root level
    if not base_name is None:
        pass
    # Visit the statements in the module
    v = StatementVisitor(modules, assignment_0_map, assignment_1_map, register_list, base_name)
    v.visit(module.body)

def instantiate(modules, assignment_0_map, assignment_1_map, register_list: list[str]):
    declaration_map = {}
    instantiate_recursive(modules, assignment_0_map, assignment_1_map, register_list, "main", None)

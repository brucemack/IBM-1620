import lark

class Module:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

class ExecutableStatement:
    def __init__(self):
        pass
    def execute(self, value_map, next_value_map):
        pass

class ExecutableAssignmentStatement(ExecutableStatement):
    def __init__(self, target_name, exp_node):
        pass
    def execute(self, value_map, next_value_map):
        pass

class ExecuableExpressionNode:
    def __init__(self, target_name, exp_node):
        pass
    def evaluate(self, value_map):
        pass

class Declaration:

    def __init__(self, io, wr, name):
        self.io = io
        self.wr = wr 
        self.name = name

    def fill_in(self, d):
        if self.io is None:
            self.io = d.io
        if self.wr is None:
            self.wr = d.wr
 
    def override(self, d):
        if not d.io is None:
            self.io = d.io
        if not d.wr is None:
            self.wr = d.wr

    def __repr__(self) -> str:
        io = self.io 
        if io is None:
            io = "?"
        wr = self.wr 
        if wr is None:
            wr = "?"
        return io + "/" + wr + "/" + self.name

# ----- Parse Tree Transformers ---------------------------------------------------------

class ModuleDeclarationProcessor(lark.visitors.Transformer):

    def __init__(self, modules):
        self.modules = modules

    # moduledeclaration: MODULE IDENTIFIER "(" identifierlist ")" ";" statementlist ENDMODULE
        #                          [1]              [2]                   [3]
    def moduledeclaration(self, tree):
        module_name = str(tree[1])
        declaration_list = []
        # Process the identifiers
        last_declaration = Declaration( "INPUT", "WIRE", None)
        for decl in tree[2]:
            # Handle defaults by carrying over the previous characteristic
            decl.fill_in(last_declaration)
            declaration_list.append(decl)
            last_declaration = decl
        # Process the statements looking for declarations
        for statement in tree[3]:
            if statement.data == "statement_declaration":
                for d in statement.children:
                    for decl in d:
                        # Scan to look for name matches
                        found = False
                        for possible in declaration_list:
                            if decl.name ==  possible.name:
                                possible.override(decl)
                                found = True
                        if not found:
                            declaration_list.append(decl)
            elif statement.data == "statement_assignment":
                pass
            elif statement.data == "statement_moduleinstantiation":
                pass

        # Deal with declaration defaults
        print("BEFORE",declaration_list)
        for decl in declaration_list:
            decl.fill_in(Declaration("LOCAL", "WIRE", None))
        print("AFTER",declaration_list)
            
        self.modules[module_name] = Module(module_name, None)

    def statementlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, tree[0])
        return l

    def statementlist_start(self, tree):
        return [ tree[0] ]
    
    def declarationidentifier_a(self, tree):
        return Declaration( tree[0].type, tree[1].type, str(tree[2]) )

    def declarationidentifier_b(self, tree):
        return Declaration( tree[0].type, None, str(tree[1]) )

    def declarationidentifier_c(self, tree):
        return Declaration( None, tree[0].type, str(tree[1]) )
    
    def declarationidentifier_d(self, tree):
        return Declaration( None, None, str(tree[0]) )

    # This will be a list of Declarations
    def declarationidentifierlist_start(self, tree):
        return [ tree[0] ]

    def declarationidentifierlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, tree[0])
        return l

    def declaration_input(self, tree):
        result = []
        for id in tree[1]:
            result.append(Declaration( "INPUT", None, id) )
        return result
    
    def declaration_input_wire(self, tree):
        result = []
        for id in tree[2]:
            result.append(Declaration( "INPUT", "WIRE", id) )
        return result

    def declaration_output(self, tree):
        result = []
        for id in tree[1]:
            result.append(Declaration( "OUTPUT", None, id))
        return result
    
    def declaration_output_wire(self, tree):
        result = []
        for id in tree[2]:
            result.append(Declaration( "OUTPUT", "WIRE", id))
        return result
    
    def declaration_output_reg(self, tree):
        result = []
        for id in tree[2]:
            result.append(Declaration( "OUTPUT", "REG", id))
        return result

    def declaration_reg(self, tree):
        result = []
        for id in tree[1]:
            result.append(Declaration( None, "REG", id))
        return result
    
    def declaration_wire(self, tree):
        result = []
        for id in tree[1]:
            result.append(Declaration( None, "WIRE", id))
        return result

    # Start a list of strings
    def identifierlist_start(self, tree):
        return [ str(tree[0]) ]

    # Continue a list of strings
    def identifierlist_add(self, tree):
        l = tree[1].copy()
        l.insert(0, str(tree[0]))
        return l  

"""
class DeclarationProcessor(lark.visitors.Transformer):

    def __init__(self, input_names, reg_names):
        self.input_names = input_names
        self.reg_names = reg_names
        self.stack = []

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
"""

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
        d = DeclarationProcessor(self.input_names, self.reg_names)
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

import lark

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

class LogicBox:

    def __init__(self, logic_file_name, value_source):
        self.value_source = value_source
        parser = lark.Lark.open("./logic.lark")
        with open(logic_file_name) as lf:
            self.tree = parser.parse(lf.read())
        self.tick_count = 0
        print(self.tree.pretty())

        # Process declarations (one time)
        self.input_names = []
        self.reg_names = []
        d = DeclarationProcessor(self.input_names, self.reg_names)
        d.transform(self.tree)
        print("Inputs:", self.input_names)
        print("Regs:", self.reg_names)

        self.value_map = {}

        # Initialize varaibles
        for n in self.input_names:
            self.value_map[n] = False
        for n in self.reg_names:
            self.value_map[n] = False

    def get_input_names(self) -> list[str]:
        return self.input_names.copy()

    def get(self, name: str):
        return self.value_map[name]
    
    def tick(self):

        # Setup input
        for n in self.input_names:
            self.value_map[n] = self.value_source.get(n)

        self.value_map["_angle"] = (self.tick_count % 360)

        next_value_map = {}
        ev = Evaluator(self.value_map, next_value_map)
        ev.transform(self.tree)

        # Copy values down
        for n, v in next_value_map.items():
            self.value_map[n] = v

        self.tick_count = self.tick_count + 1

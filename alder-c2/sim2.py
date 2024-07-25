
from enum import Enum

class ValueMode(Enum):
    NORMAL = 0
    X = 1
    Z = 2

class Value:    

    def __init__(self, v):
        self.value_mode = ValueMode.NORMAL
        self.value = v

    def __init__(self, vm: ValueMode):
        self.value_mode = vm
        self.value = 0

    def __eq__(self, other):
        return self.value_mode == other.value_mode and self.value == other.value     

    def is_x(self):
        return self.value_mode == ValueMode.X
    
    def is_z(self):
        return self.value_mode == ValueMode.Z

    def get_bool(self):
        return bool(self.value)
    
    def get_float(self):
        return float(self.value)

    def get_int(self):
        return int(self.value)
    
    def get_value(self):
        return self.value

    def __repr__(self) -> str:
        return str(self.value)

# ----- Expression Related ----------------------------------------------

class Expression:

    def __init__(self):
        pass

    def evaluate(self, context) -> Value:
        raise Exception()

    def get_references(self) -> list[str]:
        raise Exception()

class VariableExpression(Expression):

    def __init__(self, name):
        self.name = name 

    def evaluate(self, context) -> Value:
        return context.get_value(self.name)

    def __repr__(self) -> str:
        return self.name

    def get_references(self) -> list[str]:
        return [ self.name ]

class ConstantExpression(Expression):

    def __init__(self, value: Value):
        self.value = value

    def evaluate(self, context) -> Value:
        return self.value

    def __repr__(self):
        return str(self.value)

    def get_references(self) -> list[str]:
        return [ ]

class BinaryExpression(Expression):

    def __init__(self, type, lhs, rhs):
        self.type = type 
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, context) -> Value:
        lhs_value = self.lhs.evaluate(context)
        rhs_value = self.rhs.evaluate(context)
        return self.eval(lhs_value, rhs_value)
    
    def eval(self, lhs: Value, rhs: Value) -> Value:
        if self.type == "|":
            return Value(lhs.get_bool() or rhs.get_bool())
        elif self.type == "&":
            return Value(lhs.get_bool() and rhs.get_bool())
        elif self.type == "<":
            return Value(lhs.get_float() < rhs.get_float())
        elif self.type == "<=":
            return Value(lhs.get_float() <= rhs.get_float())
        elif self.type == ">":
            return Value(lhs.get_float() > rhs.get_float())
        elif self.type == ">=":
            return Value(lhs.get_float() >= rhs.get_float())
        else:
            raise Exception("Invalid operation type")
        
    def __repr__(self):
        return "(" + str(self.lhs) + " " + self.type + " " + str(self.rhs) + ")"

    def get_references(self) -> list[str]:
        result = self.lhs.get_references()
        result.extend(self.rhs.get_references())
        return result 
    
class UnaryExpression(Expression):

    def __init__(self, type, lhs):
        self.type = type 
        self.lhs = lhs

    def evaluate(self, context) -> Value:
        lhs_value = self.lhs.evaluate(context)
        return self.eval(lhs_value)
    
    def eval(self, lhs: Value)-> Value:
        if self.type == "!":
            return Value(not lhs.get_bool())
        else:
            raise Exception("Invalid operation type")

    def __repr__(self):
        return "(" + self.type + str(self.lhs) + ")"

    def get_references(self) -> list[str]:
        return self.lhs.get_references()

# --------------------------------------------------------------------------

class DataType(Enum):
    NET = 1
    VARIABLE = 2

class PortType(Enum):
    INPUT = 1
    OUTPUT = 2

class NetType(Enum):
    SUPPLY0 = 0
    SUPPLY1 = 1
    WIRE = 2
    WOR = 3
    WAND = 4

LOGIC_0 = Value(0)
LOGIC_1 = Value(1)
LOGIC_X = Value(ValueMode.X)
LOGIC_Z = Value(ValueMode.Z)

# See IEEE Standard Section 5.1.10
def logic_eval_or(a, b):
    if a == LOGIC_0:
        if   (b == LOGIC_0): return LOGIC_0
        elif (b == LOGIC_1): return LOGIC_1
        elif (b == LOGIC_X): return LOGIC_X
        elif (b == LOGIC_Z): return LOGIC_X
    elif a == LOGIC_1:
        if   (b == LOGIC_0): return LOGIC_1
        elif (b == LOGIC_1): return LOGIC_1
        elif (b == LOGIC_X): return LOGIC_1
        elif (b == LOGIC_Z): return LOGIC_1
    elif a == LOGIC_X or a == LOGIC_Z:
        if   (b == LOGIC_0): return LOGIC_X
        elif (b == LOGIC_1): return LOGIC_1
        elif (b == LOGIC_X): return LOGIC_X
        elif (b == LOGIC_Z): return LOGIC_X

# See IEEE Standard Section 5.1.10
def logic_eval_and(a, b):
    if a == LOGIC_0:
        if   (b == LOGIC_0): return LOGIC_0
        elif (b == LOGIC_1): return LOGIC_0
        elif (b == LOGIC_X): return LOGIC_0
        elif (b == LOGIC_Z): return LOGIC_0
    elif a == LOGIC_1:
        if   (b == LOGIC_0): return LOGIC_0
        elif (b == LOGIC_1): return LOGIC_1
        elif (b == LOGIC_X): return LOGIC_X
        elif (b == LOGIC_Z): return LOGIC_X
    elif a == LOGIC_X or a == LOGIC_Z:
        if   (b == LOGIC_0): return LOGIC_0
        elif (b == LOGIC_1): return LOGIC_X
        elif (b == LOGIC_X): return LOGIC_X
        elif (b == LOGIC_Z): return LOGIC_X

def wire_logic_eval(drivers: list[Value], net_type: NetType):
    if net_type == NetType.SUPPLY0:
        if len(drivers) > 0:
            raise Exception("Not allowed to drive a supply net")
        return Value(0)
    elif net_type == NetType.SUPPLY1:
        if len(drivers) > 0:
            raise Exception("Not allowed to drive a supply net")
        return Value(1)
    elif net_type == NetType.WIRE:
        if len(drivers) > 1:
            return Value(ValueMode.X)
        return drivers[0]
    elif net_type == NetType.WOR:
        l = drivers[0]
        for i in range(1, len(drivers)):
            l = logic_eval_or(l, drivers[i])
        return l
    elif net_type == NetType.WAND:
        l = drivers[0]
        for i in range(1, len(drivers)):
            l = logic_eval_and(l, drivers[i])
        return l

class SymbolDeclaration:

    def __init__(self, name: str, type: DataType):
        self.name = name 
        self.data_type = type

    def get_name(self): return self.name 
    def get_data_type(self): return self.data_type

class NetDeclaration(SymbolDeclaration):

    def __init__(self, name: str, net_type: NetType):
        super().__init__(name, DataType.NET)
        self.net_type = net_type

    def get_net_type(self): return self.net_type

class PortDeclaration(NetDeclaration):

    def __init__(self, name: str, port_type: PortType):
        super().__init__(name, NetType.WIRE)
        self.port_type = port_type

class FunctionParameter:

    def __init__(self, name: str):
        self.name = name

    def get_name(self): return self.name

class Statement:
    def __init__(self):
        pass
    def execute(self, context):
        raise Exception("Not implemented")

class ProcedureAssignment(Statement):
    def __init__(self, lhs: str, rhs: Expression):
        self.lhs = lhs
        self.rhs = rhs

    def execute(self, context):
        
        # Make sure the LHS is a variable (i.e. it's illegal to assign
        # to nets).

        # Evaluate the RHS
        rhs_value = self.rhs.evaluate(context)
        # Assign the result to the LHS
        context.assign(self.lhs, rhs_value)

    def get_references(self):
        return self.rhs.get_references()

class ProcedureBlock:

    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def execute(self, context):
        for statement in self.statements:
            statement.execute(context)

    def get_references(self):
        result = []
        for statement in self.statements:
            result.extend(statement.get_references())
        return result

class Function(Expression):
    
    def __init__(self, name: str, 
                 params: list[FunctionParameter], 
                 local_variables: list, 
                 procedure_block: ProcedureBlock):

        self.name = name

        self.params: dict = {}
        for param in params:
            self.params[param.get_name()] = param

        self.local_variables: dict = {}
        for local_variable in local_variables:
            self.local_variables[local_variable.get_name()] = local_variable

        self.procedure_block: ProcedureBlock = procedure_block

    def get_name(self) -> str: return self.name

    def evaluate(self, context) -> Value:
        # Setup the context:
        # 1. Connect to local variables
        # 2. Any reference to a variable that isn't local gets forwarded out 
        #    to the calling context.
        # 3. Any reference to a variable with the same name of the function 
        #    is assumed to be the return value 

        # Run the procedure block
        self.procedure_block.execute(context)
        # Extract the return value
        result = None
        return result

    def get_references(self) -> list[str]:
        # Get the references made by the procedure block
        refs = self.procedure_block.get_references()
        # Remove any ports since they aren't external
        for param in self.params.values():
            refs.remove(param.get_name())
        # Remove any local variables since they aren't external
        for lv in self.local_variables.values():
            refs.remove(lv.get_name())
        return refs

class NetAssignment:

    def __init__(self, name: str, exp: Expression):
        self.name = name 
        self.exp = exp

    def get_name(self): return self.name 
    def get_exp(self): return self.exp

class ModuleDefinition:

    def __init__(self, name, net_declarations, net_assignments):

        self.name = name

        # Move the list of net declarations into a map
        self.net_declarations: dict[str, SymbolDeclaration] = {}
        for declaration in net_declarations:
            if declaration.get_name() in self.net_declarations:
                raise Exception("Redundant declaration " + declaration.get_name())
            self.net_declarations[declaration.get_name()] = declaration

        # Move the list of net assignments into a map 
        self.net_assignments: dict[str, list[NetAssignment]] = {}
        for assignment in net_assignments:
            if not assignment.get_name() in self.net_assignments:
                self.net_assignments[assignment.get_name()] = []
            self.net_assignments[assignment.get_name()].append(assignment)
      
class ValueState:

    def __init__(self):
        self.state: dict[str, Value] = {}

    def set_value(self, name, value: Value): self.state[name] = value
    def get_value(self, name) -> Value: return self.state[name]
    def is_value_available(self, name) -> bool: return name in self.state
    def is_value_changed(self, name, value: Value) -> bool:
        return (not name in self.state) or (not self.state[name] == value)

class ModuleEvalContext:

    def __init__(self, value_state: ValueState):
        self.value_state = value_state
    
    def get_value(self, name):
        if not self.value_state.is_value_available(name):
            raise Exception("No value available for " + name)
        return self.value_state.get_value(name)

class UpdateEvent:

    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return "UpdateEvent: " + self.name + " = " + str(self.value)

class ModuleInstance:

    def __init__(self, name: str, mod_def: ModuleDefinition, value_state: ValueState):
        self.name = name 
        self.mod_def = mod_def
        self.values = {}
        self.value_state: ValueState = value_state

    def init(self):
        for nd in self.mod_def.net_declarations.values():
            self.value_state.set_value(nd.get_name(), Value(ValueMode.X))

    def set_value(self, name: str, value: Value, active_queue: list[UpdateEvent]):
        print("Setting value of symbol:", name)
        if not name in self.mod_def.net_declarations:
            raise Exception("Undefined symbol " + name + " in module " +
                            self.name)
        # Check to see if this value has changed since the last time
        changed = self.value_state.is_value_changed(name, value)
        if changed:
            print("Value has changed")
            # Save value
            self.value_state.set_value(name, value)

            # Figure out which nets need to be recomputed now
            dirty_nets = set()
            for net_name, assignment_list in self.mod_def.net_assignments.items():
                for assignment in assignment_list:
                    if name in assignment.get_exp().get_references():
                        dirty_nets.add(net_name)

            # Setup the evaluation context
            eval_context = ModuleEvalContext(self.value_state)

            # Do the recomputation for each dirty symbol
            for dirty_net in dirty_nets:
                print("Dirty Net", dirty_net)

                # The net may have more than one driver, so evaluate them all
                driving_values = []
                for assignment in self.mod_def.net_assignments[dirty_net]:
                    print("   Driving Expression:", str(assignment.get_exp()))
                    driving_value = assignment.get_exp().evaluate(eval_context)
                    driving_values.append(driving_value)

                new_value = wire_logic_eval(driving_values, 
                                            self.mod_def.net_declarations[dirty_net].get_net_type())

                # Create an event to store back the new value
                active_queue.append(UpdateEvent(dirty_net, new_value))
        else:
            print("Value has not changed, ignoring")



from enum import Enum

class Value:    

    def __init__(self, v):
        self.value = v

    def __eq__(self, other):
        return self.value == other.value     

    def is_x(self):
        return self.value == "X"
    
    def is_z(self):
        return self.value == "Z"

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

LOGIC_0 = Value(0)
LOGIC_1 = Value(1)
LOGIC_X = Value("X")
LOGIC_Z = Value("Z")

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
def logic_eval_and(a: Value, b: Value) -> Value:
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

# See Table 5-16
def logic_eval_not(a: Value) -> Value:
    if a == LOGIC_0:
        return LOGIC_1
    elif a == LOGIC_1:
        return LOGIC_0
    else:
        return LOGIC_X

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
            return logic_eval_or(lhs, rhs)
        elif self.type == "&":
            return logic_eval_and(lhs, rhs)
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
            return logic_eval_not(lhs)
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

class ValueState:

    def __init__(self):
        self.state: dict[str, Value] = {}

    def set_value(self, name, value: Value): self.state[name] = value
    def get_value(self, name) -> Value: 
        if not name in self.state:
            return LOGIC_X
        else:
            return self.state[name]
    def is_value_available(self, name) -> bool: return name in self.state
    def is_value_changed(self, name, value: Value) -> bool:
        return (not name in self.state) or (not self.state[name] == value)

class SignalDeclaration:

    def __init__(self, name: str, type: DataType):
        self.name = name 
        self.data_type = type

    def get_name(self): return self.name 
    def get_data_type(self): return self.data_type

class NetDeclaration(SignalDeclaration):

    def __init__(self, name: str, net_type: NetType):
        super().__init__(name, DataType.NET)
        self.net_type = net_type

    def get_net_type(self): return self.net_type

class VariableDeclaration(SignalDeclaration):

    def __init__(self, name: str):
        super().__init__(name, DataType.VARIABLE)

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

        # TODO: Make sure the LHS is a variable (i.e. it's illegal to assign
        # to nets).
        
        # Evaluate the RHS
        rhs_value = self.rhs.evaluate(context)
        # Assign the result to the LHS
        context.set_value(self.lhs, rhs_value)

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

class FunctionDefinition:
    
    def __init__(self, name: str, 
                 params: list[FunctionParameter], 
                 local_variables: list[VariableDeclaration], 
                 procedure_block: ProcedureBlock):

        self.name = name
        self.params = params

        # Convert the list of local variable definitions to a map
        self.local_variables: dict[str, VariableDeclaration] = {}
        for local_variable in local_variables:
            self.local_variables[local_variable.get_name()] = local_variable

        self.procedure_block: ProcedureBlock = procedure_block

    def get_name(self) -> str: return self.name

    def is_local_variable(self, name: str): return name in self.local_variables

    def is_param_name(self, name: str):
        # TODO: FASTER
        for param in self.params:
            if name == param.get_name(): return True
        return False

    def get_references(self) -> list[str]:
        # Get the references made by the procedure block
        refs = self.procedure_block.get_references()
        # Remove any parameter names since they aren't external
        for param in self.params:
            refs.remove(param.get_name())
        # Remove any local variables since they aren't external
        for lv in self.local_variables.values():
            refs.remove(lv.get_name())
        return refs

class FunctionEvalContext:

    def __init__(self, function_def: FunctionDefinition, value_state, param_values: list[Value]):

        self.value_state = value_state
        self.function_def = function_def

        # Here is where the local variables are stored
        self.local_value_state: dict[str, Value] = {}

        # Move the parameter values into the local variable store
        if len(param_values) != len(self.function_def.params):
            raise Exception("Wrong number of parameters passed to " + self.function_def.get_name())
        i = 0
        for param in self.function_def.params:
            self.local_value_state[param.get_name()] = param_values[i]
            i = i + 1
    
    def is_local_name(self, name:str) -> bool:
        return name == self.function_def.get_name() or \
           self.function_def.is_local_variable(name) or \
           self.function_def.is_param_name(name)

    def get_value(self, name: str) -> Value:
        # Figure out if this is a reference to a parameter, a local variable, or to the 
        # function name itself (which is treated like a local)
        if self.is_local_name(name):
            # Default unset variables to X
            if not name in self.local_value_state:
                return LOGIC_X
            else:
                return self.local_value_state[name]
        # Otherwise, forward out to the wider context
        else:
            return self.value_state.get_value(name)

    def set_value(self, name: str, value: Value):
        # Figure out if this is a reference to a local variable or to the function 
        # name itself, which is treated like a local
        if self.is_local_name(name):
            self.local_value_state[name] = value
        # Otherwise, forward out to the wider context
        else:
            self.value_state.set_value(name, value)

class FunctionExpression(Expression):

    def __init__(self, function_def: FunctionDefinition, params: list[Expression]):

        self.function_def = function_def
        self.params = params

    def evaluate(self, global_context) -> Value:

        # Evaluate the parameters to the function
        param_values = [arg.evaluate(global_context) for arg in self.params]
        # Setup the context for use INSIDE of the function execution
        function_context = FunctionEvalContext(self.function_def, global_context, param_values)
        # Run the procedure block
        self.function_def.procedure_block.execute(function_context)
        # Extract the return value based on the name of the function
        return function_context.get_value(self.function_def.get_name())

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
        self.net_declarations: dict[str, NetDeclaration] = {}
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
            self.value_state.set_value(nd.get_name(), LOGIC_X)

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


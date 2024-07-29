from __future__ import annotations 

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

def globalize_name_if_necessary(prefix, local_variables: list[str], name: str) -> str:
    if "." in name: 
        return name 
    elif name in local_variables: 
        return name
    else:
        return prefix + "." + name

class Expression:

    def evaluate(self, contex: EvalContext) -> Value:
        raise Exception("Missing implementation")

    def get_references(self) -> list[str]:
        return [ ]

    # Creates a new version of the expression with versions of the function/
    # variable names that are in the global scope.
    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        raise Exception("Missing implementation")

class VariableExpression(Expression):

    def __init__(self, name):
        self.name = name 

    def evaluate(self, context: EvalContext) -> Value:
        return context.get_value(self.name)

    def __repr__(self) -> str:
        return self.name

    def get_references(self) -> list[str]:
        return [ self.name ]

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        return VariableExpression(globalize_name_if_necessary(name_prefix, local_variables, self.name))
    

class ConstantExpression(Expression):

    def __init__(self, value: Value):
        self.value = value

    def evaluate(self, context) -> Value:
        return self.value

    def __repr__(self):
        return str(self.value)

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        return ConstantExpression(self.value)
    

class BinaryExpression(Expression):

    def __init__(self, type, lhs, rhs):
        self.type = type 
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, context: EvalContext) -> Value:
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

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        return BinaryExpression(self.type, 
                                self.lhs.globalize(name_prefix, local_variables),
                                self.rhs.globalize(name_prefix, local_variables))
   

class UnaryExpression(Expression):

    def __init__(self, type, lhs):
        self.type = type 
        self.lhs = lhs

    def evaluate(self, context: EvalContext) -> Value:
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

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        return UnaryExpression(self.type, 
                               self.lhs.globalize(name_prefix, local_variables))

class FunctionExpression(Expression):

    def __init__(self, name: str, params: list[Expression]):

        self.name = name
        self.params = params

    def evaluate(self, global_context: EvalContext) -> Value:

        # Evaluate the parameters to the function
        param_values = [arg.evaluate(global_context) for arg in self.params]
        # Get the function definition based on the name
        function_def = global_context.get_function_def(self.name)
        # Setup the context for use INSIDE of the function execution
        function_context = FunctionEvalContext(function_def, global_context, param_values)
        # Run the procedure block
        function_def.procedure_block.execute(function_context)
        # Extract the return value based on the name of the function
        return function_context.get_value(function_def.get_name())

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        # Globalize the parameter list
        return FunctionExpression(name_prefix + "." + self.name, 
                [p.globalize(name_prefix, local_variables) for p in self.params])

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

# TODO: WORK ON STRENGTH
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
            return LOGIC_X
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

# ----- Declarations -----------------------------------------------------


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

    def __repr__(self) -> str: return self.name

class Statement:

    def execute(self, context):
        raise Exception("Not implemented")

    def elaborate(self, base_name):
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

    def __repr__(self):
        return self.lhs + "=" + str(self.rhs) + ";"

    def elaborate(self, base_name: str, local_variables: list[str]) -> ProcedureAssignment:
        if self.lhs in local_variables:
            elaborated_lhs = self.lhs
        else:
            elaborated_lhs = base_name + "." + self.lhs
        return ProcedureAssignment(elaborated_lhs, self.rhs.globalize(base_name, local_variables))

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
    
    def __repr__(self):
        r = ""
        for statement in self.statements:
            r = r + str(statement) + "\n"
        return r

    def elaborate(self, base_name: str, local_variables: list[str]) -> ProcedureBlock:
        return ProcedureBlock(
            [statement.elaborate(base_name, local_variables) for statement in self.statements]
            )

class FunctionDefinition:
    
    def __init__(self, 
                 name: str, 
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

    def __repr__(self) -> str:
        r = "function " + self.name
        # Add the parameters 
        r = r + "("
        first = True
        for fp in self.params:
            if not first:
                r = r + ","
            r = r + str(fp)
            first = False
        r = r + ");\n"
        r = r + "begin\n"
        r = r + str(self.procedure_block)
        r = r + "end\n"
        r = r + "endfunction\n"
        return r

    def elaborate(self, base_name: str) -> FunctionDefinition:
        # Make a list of the local variables that should not be elaborated
        local_variables = []        
        local_variables.append(self.name)
        # Parameter names should not be elaborated
        for fp in self.params:
            local_variables.append(fp.get_name())
        return FunctionDefinition(self.name,
                                  self.params,
                                  self.local_variables.values(),
                                  self.procedure_block.elaborate(base_name, local_variables))

    def get_references(self) -> list[str]:
        refs = self.procedure_block.get_references()
        for fp in self.params:            
            refs.remove(fp.get_name())
        return refs

class FunctionEvalContext:

    def __init__(self, function_def: FunctionDefinition, value_state, param_values: list[Value]):

        self.value_state = value_state
        self.function_def = function_def

        # Here is where the local variables are stored (transient)
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

class NetAssignment:

    def __init__(self, name: str, exp: Expression):
        self.name = name 
        self.exp = exp

    def get_name(self): return self.name 
    def get_exp(self): return self.exp

class PortAssignment:

    def __init__(self, inside_name: str, outside_name: str):

        self.inside_name = inside_name
        self.outside_name = outside_name

class ModuleInstantiation:

    def __init__(self, 
                 name: str, 
                 instance_name: str, 
                 ports: list[PortAssignment]):

        self.name = name 
        self.instance_name = instance_name 
        self.ports = ports

class ModuleDefinition:

    def __init__(self, 
                 name: str, 
                 port_declarations: list[PortDeclaration],
                 net_declarations: list[NetDeclaration], 
                 net_assignments: list[NetAssignment], 
                 module_instantiations: list[ModuleInstantiation],
                 function_definitions: list[FunctionDefinition]):

        self.name = name
        self.module_instantiations = module_instantiations
        self.function_definitions: list[FunctionDefinition] = function_definitions
        self.port_declarations: dict[str, PortDeclaration] = {} 
        self.net_declarations: list[NetDeclaration] = net_declarations
        self.net_assignments: list[NetAssignment] = net_assignments

        # Move the port declarations into a map 
        for pd in port_declarations:
            if pd.get_name() in self.port_declarations:
                raise Exception("Redundant port declaration " + pd.get_name())
            self.port_declarations[pd.get_name()] = pd

    def elaborate(self, 
                  path: str, 
                  name: str,
                  param_map: dict[str, str], 
                  module_defs: dict[str, ModuleDefinition], 
                  global_net_reg: NetRegistry,
                  global_function_registry: FunctionDefinitionRegistry,
                  global_value_state: ValueState):

        print("Elaborating", path + "." + name, "with", param_map)

        # Register the function definitions into a global repository
        for fd in self.function_definitions:
            global_function_registry.add_function(path + "." + name + "." + fd.get_name(), 
                fd.elaborate(path + "." + name))
            
        # Register the net declarations into a global repository
        for nd in self.net_declarations:
            global_net_reg.declare(path + "." + name + "." + nd.get_name(), 
                                   nd.get_net_type())

        # Create some additional assignments to wire the module parameters. 
        # These assignments depend on the direction of the port.
        for inner_name, global_outer_name in param_map.items():

            # Globalize the names involved in the port assignment
            global_inner_name = path + "." + name + "." + inner_name

            if not inner_name in self.port_declarations:
                raise Exception("Port not defined " + inner_name)
            pd = self.port_declarations[inner_name]

            if pd.port_type == PortType.INPUT:
                # Register the assignment: inner <- outer
                global_net_reg.add_assignment(global_inner_name,
                                              VariableExpression(global_outer_name))                                                 
            elif pd.port_type == PortType.OUTPUT:
                # Register the assignment: outer <- inner
                global_net_reg.add_assignment(global_outer_name,
                                              VariableExpression(global_inner_name))                                                 
            else:
                raise Exception("Invalid port type")

        # Instantiate the required global net assignments
        for na in self.net_assignments:
            global_net_name = path + "." + name + "." + na.get_name()
            # Globalize the RHS of the assignment
            # TODO: DEAL WITH LOCAL VARIABLE LIST
            global_exp = na.exp.globalize(path + "." + name, [])
            # Add the assignment to the global registry
            global_net_reg.add_assignment(global_net_name, global_exp)
            # Set the initial value
            global_value_state.set_value(global_net_name, LOGIC_X)


        # Deal with next level down of modules
        for mi in self.module_instantiations:
            module_def = module_defs[mi.name]
            # Make a mapping between the child's parameter names and the parent's 
            # actual signal names.
            child_param_map = {}
            for port in mi.ports:
                child_param_map[port.inside_name] = path + "." + name + "." + port.outside_name
            module_def.elaborate(path + "." + name, mi.instance_name,
                child_param_map, module_defs, global_function_registry, 
                global_net_assignments, global_value_state)

# ----- Simulation Engine ----------------------------------------------------

class ValueState:

    def __init__(self):
        self.state: dict[str, Value] = {}

    def set_value(self, name, value: Value): 
        self.state[name] = value

    def get_value(self, name) -> Value: 
        if not name in self.state:
            return LOGIC_X
        else:
            return self.state[name]

    def is_value_available(self, name) -> bool: return name in self.state

    def is_value_changed(self, name, value: Value) -> bool:
        return (not name in self.state) or (not self.state[name] == value)

class NetInformation:

    def __init__(self, name: str, type: NetType):
        self.name = name
        self.type = type 
        self.assignments: list[Expression] = []

# Used for storing net types and assignments
class NetRegistry:

    def __init__(self):
        self.reg: dict[str, NetInformation] = {}

    def declare(self, name: str, type: NetType):
        self.reg[name] = NetInformation(name, type)

    def add_assignment(self, name: str, exp: Expression):
        if not name in self.reg:
            raise Exception("Attempt to add assignment to undeclared net " + name)
        self.reg[name].assignments.append(exp)

    def debug(self):
        for name, decl in self.reg.items():
            print(name, "<-", str(decl.assignments))


class FunctionDefinitionRegistry:

    def __init__(self):
        self.reg: dict[str, FunctionDefinition] = {}

    def add_function(self, name: str, func_def: FunctionDefinition):
        if name in self.reg:
            raise Exception("Duplicate function " + name)
        self.reg[name] = func_def

    def get_function_def(self, name: str) -> FunctionDefinition:
        return self.reg[name]

class EvalContext:

    def __init__(self):
        self.value_state: ValueState = ValueState()
        self.func_def_reg = FunctionDefinitionRegistry()
        self.net_reg = NetRegistry()
        self.active_queue: list[UpdateEvent] = []
    
    def get_value(self, name: str):
        if not self.value_state.is_value_available(name):
            raise Exception("No value available for " + name)
        return self.value_state.get_value(name)
    
    def set_value(self, name: str, value: Value):

        print("Setting value of:", name, "to", value)

        # Check to see if this value has changed since the last time
        changed = self.value_state.is_value_changed(name, value)
        if changed:
            print("Value has changed")
            # Save value
            self.value_state.set_value(name, value)

            # Figure out which nets need to be recomputed now
            dirty_nets = set()
            # Go through every registered assignment
            for net_name, net_info in self.net_reg.reg.items():
                # Each signal can have multiple assignments contributing to it
                for assignment in net_info.assignments:
                    if name in assignment.get_references():
                        dirty_nets.add(net_name)

            # Do the recomputation for each dirty symbol
            for dirty_net in dirty_nets:
                print("Dirty Net", dirty_net)

                # The net may have more than one driver, so evaluate them all
                driving_values = []
                for assignment in self.net_reg.reg[dirty_net].assignments:
                    print("   Driving Expression:", str(assignment))
                    driving_value = assignment.evaluate(self)
                    driving_values.append(driving_value)

                new_value = wire_logic_eval(driving_values, self.net_reg.reg[dirty_net].type)

                # Create an event to store back the new value
                self.active_queue.append(UpdateEvent(dirty_net, new_value))
                # TODO: COLLAPSE REDUNDANT ASSIGNMENTS
        else:
            print("Value has not changed, ignoring")

    def flush_active_queue(self):

        # Keep doing this until the active queue is empty
        while len(self.active_queue) > 0:

            # Pull the active events to the side and flush the queue
            active_events = self.active_queue.copy()
            self.active_queue.clear()

            # Apply the events
            for event in active_events:
                self.set_value(event.name, event.value)

    def get_function_def(self, name:str):
        return self.func_def_reg.get_function_def(name)

class UpdateEvent:

    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return "UpdateEvent: " + self.name + " = " + str(self.value)

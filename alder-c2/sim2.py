from __future__ import annotations 
"""
Simple Verilog Simulator
Copyright (C) 2024 - Bruce MacKinnon
 
This work is covered under the terms of the GNU Public License (V3). Please consult the 
LICENSE file for more information.

This work is being made available for non-commercial use. Redistribution, commercial 
use or sale of any part is prohibited.
"""

from enum import Enum
import lark 

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
        if self.is_x():
            return "1'bx"
        elif self.is_z():
            return "1'bz"
        elif self.value == 0:
            return "1'b0"
        elif self.value == 1:
            return "1'b1"
        else:
            return str(self.value)

LOGIC_0 = Value(0)
LOGIC_1 = Value(1)
LOGIC_X = Value("X")
LOGIC_Z = Value("Z")

def parse_binary_constant(c):
    # TODO: COMPLETE
    if c.startswith("1'b"):
        s = c[3:]
        if s == "0":
            return LOGIC_0
        elif s == "1":
            return LOGIC_1
        elif s == "x":
            return LOGIC_X
        elif s == "z":
            return LOGIC_Z
        else:
            raise Exception("Binary constant format error " + c)
    else:
        raise Exception("Binary constant format error " + c)

# See IEEE standard section 5.1.8
def logic_eval_eq(a: Value, b: Value):
    if a == LOGIC_X or a == LOGIC_Z or b == LOGIC_X or b == LOGIC_Z:
        return LOGIC_X
    if a == b:
        return LOGIC_1
    else:
        return LOGIC_0

def logic_eval_neq(a: Value, b: Value):
    if a == LOGIC_X or a == LOGIC_Z or b == LOGIC_X or b == LOGIC_Z:
        return LOGIC_X
    if a == b:
        return LOGIC_0
    else:
        return LOGIC_1

def case_eval_eq(a: Value, b: Value):
    if a == b:
        return LOGIC_1
    else:
        return LOGIC_0

def case_eval_neq(a: Value, b: Value):
    if a == b:
        return LOGIC_0
    else:
        return LOGIC_1

# See IEEE Standard Section 5.1.10
def logic_eval_or(a: Value, b: Value) -> Value:
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

def logic_eval_lt(a: Value, b: Value) -> Value:
    if a.is_x() or a.is_z() or b.is_x() or b.is_z():
        return LOGIC_X
    else:
        if a.get_int() < b.get_int():
            return LOGIC_1
        else:
            return LOGIC_0

def logic_eval_lte(a: Value, b: Value) -> Value:
    if a.is_x() or a.is_z() or b.is_x() or b.is_z():
        return LOGIC_X
    else:
        if a.get_int() <= b.get_int():
            return LOGIC_1
        else:
            return LOGIC_0

def logic_eval_gt(a: Value, b: Value) -> Value:
    if a.is_x() or a.is_z() or b.is_x() or b.is_z():
        return LOGIC_X
    else:
        if a.get_int() > b.get_int():
            return LOGIC_1
        else:
            return LOGIC_0
    
def logic_eval_gte(a: Value, b: Value) -> Value:
    if a.is_x() or a.is_z() or b.is_x() or b.is_z():
        return LOGIC_X
    else:
        if a.get_int() >= b.get_int():
            return LOGIC_1
        else:
            return LOGIC_0

# ----- Expression Related ----------------------------------------------

def join_name(path: str, name: str, name2: str = None) -> str:

    s = None
    if path and name:
        s = path + "." + name 
    elif name:
        s = name

    if name2:
        if not s:
            s = name2
        else:
            s = s + "." + name2

    return s

def globalize_name_if_necessary(prefix, local_variables: list[str], name: str) -> str:
    if "." in name: 
        return name 
    elif name in local_variables: 
        return name
    else:
        return join_name(prefix, name)

class Expression:

    def evaluate(self, contex: EvalContext) -> Value:
        raise Exception("Missing implementation")

    def is_constant(self) -> bool:
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

    def is_constant(self) -> bool:
        return False
    
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

    def is_constant(self) -> bool:
        return True

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

    def is_constant(self) -> bool:
        return self.lhs.is_constant() and self.rhs.is_constant()
        
    def eval(self, lhs: Value, rhs: Value) -> Value:
        if self.type == "|":
            return logic_eval_or(lhs, rhs)
        elif self.type == "&":
            return logic_eval_and(lhs, rhs)
        elif self.type == "==":
            return logic_eval_eq(lhs, rhs)
        elif self.type == "!=":
            return logic_eval_neq(lhs, rhs)
        elif self.type == "===":
            return case_eval_eq(lhs, rhs)
        elif self.type == "!==":
            return case_eval_neq(lhs, rhs)
        elif self.type == "<":
            return logic_eval_lt(lhs, rhs)
        elif self.type == "<=":
            return logic_eval_lte(lhs, rhs)
        elif self.type == ">":
            return logic_eval_gt(lhs, rhs)
        elif self.type == ">=":
            return logic_eval_gte(lhs, rhs)
        else:
            raise Exception("Invalid operation type")
        
    def __repr__(self):
        return "(" + str(self.lhs) + " " + self.type + " " + str(self.rhs) + ")"

    def get_references(self) -> list[str]:
        result = self.lhs.get_references()
        result.extend(self.rhs.get_references())
        return result 

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        print(self.lhs)
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

    def is_constant(self) -> bool:
        return self.lhs.is_constant()
    
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

    def is_constant(self) -> bool:
        for param in self.params:
            if not param.is_constant():
                return False
        return True

    def get_references(self) -> list[str]:
        result = []
        for param in self.params:
            result.extend(param.get_references())
        return result

    def globalize(self, name_prefix: str, local_variables: list[str]) -> Expression:
        # Globalize the parameter list
        return FunctionExpression(name_prefix + "." + self.name, 
                [p.globalize(name_prefix, local_variables) for p in self.params])

    def __repr__(self):
        s = self.name + "("
        first = True
        for param in self.params:
            if not first:
                s = s + ", "
            s = s + str(param)
            first = False
        s = s + ")"
        return s

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

class VariableType(Enum):
    REG = 0
    INTEGER = 1

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

    def __init__(self, name: str, net_type: NetType, assign_exp: Expression = None):
        super().__init__(name, DataType.NET)
        self.net_type = net_type
        self.exp = assign_exp

    def get_net_type(self): return self.net_type

    def __repr__(self):      
        s = self.net_type.name.lower() + " " + self.name
        if self.exp:
            s = s + " = " + str(self.exp)
        return s

class IdentifierWithInit:

    def __init__(self, name: str, init_exp: Expression):
        self.name = name 
        self.init_exp = init_exp

    def __repr__(self):      
        s = self.id.name
        if self.id.init_exp:
            s = s + " = " + str(self.id.init_exp)
        return s

class VariableDeclaration:

    def __init__(self, var_type: VariableType, id: IdentifierWithInit):
        self.var_type = var_type
        self.id = id

    def get_var_type(self): 
        return self.var_type

    def get_name(self):
        return self.id.name

    def __repr__(self):      
        return self.var_type.name.lower() + " " + str(self.id)

class PortDeclaration(NetDeclaration):

    def __init__(self, name: str, port_type: PortType):
        super().__init__(name, NetType.WIRE)
        self.port_type = port_type

    def get_port_type(self): 
        return self.port_type

    def __repr__(self):
        if self.port_type == PortType.INPUT:
            s = "input "
        elif self.port_type == PortType.OUTPUT:
            s = "output "
        else:
            raise Exception("Invalid type " + self.port_type)
        s = s + self.get_name()
        return s

class FunctionParameterDeclaration:

    def __init__(self, name: str, port_type: PortType):
        self.name = name 
        self.port_type = port_type

    def get_name(self): return self.name

    def __repr__(self) -> str: 
        if self.port_type == PortType.INPUT:
            s = "input "
        elif self.port_type == PortType.OUTPUT:
            s = "output "
        else:
            raise Exception("Invalid type")
        s = s + self.name
        return s

class Statement:

    def execute(self, context):
        raise Exception("Not implemented")

    def elaborate(self, base_name):
        raise Exception("Not implemented")

class ProcedureStatement:

    def execute(self, context):
        raise Exception("Not implemented")

    def elaborate(self, base_name):
        raise Exception("Not implemented")

class ProcedureAssignment(ProcedureStatement):

    def __init__(self, lhs: str, rhs: Expression, blocking: bool):
        self.lhs = lhs
        self.rhs = rhs
        self.blocking = blocking

    def execute(self, context):

        # TODO: Make sure the LHS is a variable (i.e. it's illegal to assign
        # to nets).
        
        # Evaluate the RHS
        rhs_value = self.rhs.evaluate(context)
        # Assign the result to the LHS
        if self.blocking:
            context.set_value_blocking(self.lhs, rhs_value)
        else:
            context.set_value_non_blocking(self.lhs, rhs_value)

    def get_references(self):
        return self.rhs.get_references()

    def __repr__(self):
        s = self.lhs
        if self.blocking:
            s = s + " = "
        else:
            s = s + " <= "
        s = s + str(self.rhs)
        return s

    def elaborate(self, base_name: str, local_variables: list[str], context: EvalContext) -> ProcedureAssignment:
        if self.lhs in local_variables:
            elaborated_lhs = self.lhs
        else:
            elaborated_lhs = join_name(base_name, self.lhs)
            # TODO: Make sure we are assigning to a variable
            if not context.is_variable(elaborated_lhs):
                raise Exception("Illegal assignment to " + elaborated_lhs)

        return ProcedureAssignment(elaborated_lhs, 
                                   self.rhs.globalize(base_name, local_variables), self.blocking)

class ProcedureBlock:

    def __init__(self, statements: list[ProcedureStatement]):
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
            r = r + str(statement) + ";\n"
        return r

    def elaborate(self, base_name: str, local_variables: list[str], context: EvalContext) -> ProcedureBlock:
        return ProcedureBlock(
            [statement.elaborate(base_name, local_variables, context) for statement in self.statements]
            )

class FunctionDefinition:
    
    def __init__(self, 
                 name: str, 
                 params: list[FunctionParameterDeclaration], 
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

    def elaborate(self, base_name: str, context: EvalContext) -> FunctionDefinition:
        # Make a list of the local variables that should not be elaborated
        local_variables = []        
        local_variables.append(self.name)
        # Parameter names should not be elaborated
        for fp in self.params:
            local_variables.append(fp.get_name())
        return FunctionDefinition(self.name,
                                  self.params,
                                  self.local_variables.values(),
                                  self.procedure_block.elaborate(base_name, local_variables, context))

    def get_references(self) -> list[str]:
        refs = self.procedure_block.get_references()
        for fp in self.params:            
            refs.remove(fp.get_name())
        return refs

class FunctionEvalContext:

    def __init__(self, function_def: FunctionDefinition, parent_eval_context: EvalContext, 
                 param_values: list[Value]):

        self.function_def = function_def
        self.parent_eval_context = parent_eval_context

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
            return self.parent_eval_context.get_value(name)

    def set_value_blocking(self, name: str, value: Value):
        # Figure out if this is a reference to a local variable or to the function 
        # name itself, which is treated like a local
        if self.is_local_name(name):
            self.local_value_state[name] = value
        # Otherwise, forward out to the wider context
        else:
            self.parent_eval_context.set_value_blocking(name, value)

class NetAssignment:

    def __init__(self, name: str, exp: Expression):
        self.name = name 
        self.exp = exp

    def get_name(self): return self.name 
    def get_exp(self): return self.exp

    def __repr__(self):
        return "assign " + self.name + " = " + str(self.exp)

class PortAssignment:

    def __init__(self, inside_name: str, outside_name: str):

        self.inside_name = inside_name
        self.outside_name = outside_name

    def __repr__(self):
        return "." + self.inside_name + "(" + self.outside_name + ")"

# TODO: Create always/initial subclasses?
class TriggeredProcedure:

    def __init__(self, identifiers, procedure_block: ProcedureBlock):
        self.identifiers = identifiers
        self.procedure_block = procedure_block

    def __repr__(self) -> str:
        s = "always @ ("        
        first = True
        for id in self.identifiers:
            if not first:
                s = s + ", "
            s = s + id 
            first = False 
        s = s + ")\n"
        s = s + "begin\n"
        s = s + str(self.procedure_block)
        s = s + "end\n"
        return s

class ModuleInstantiation:

    def __init__(self, 
                 name: str, 
                 instance_name: str, 
                 ports: list[PortAssignment]):

        self.name = name 
        self.instance_name = instance_name 
        self.ports = ports

    def __repr__(self):
        s = self.name + " " + self.instance_name + "("
        first = True
        for port in self.ports:
            if not first:
                s = s + ", "                
            s = s + str(port)
            first = False
        s = s + ")"
        return s
    
class ModuleDefinition:

    def __init__(self, 
                 name: str, 
                 port_declarations: list[PortDeclaration],
                 net_declarations: list[NetDeclaration], 
                 net_assignments: list[NetAssignment], 
                 module_instantiations: list[ModuleInstantiation],
                 function_definitions: list[FunctionDefinition],
                 var_declarations: list[VariableDeclaration],
                 triggered_procedures: list[TriggeredProcedure]):

        self.name = name
        self.module_instantiations = module_instantiations
        self.function_definitions: list[FunctionDefinition] = function_definitions
        self.port_declarations: list[PortDeclaration] = port_declarations
        self.net_declarations: list[NetDeclaration] = net_declarations
        self.net_assignments: list[NetAssignment] = net_assignments
        self.var_declarations: list[VariableDeclaration] = var_declarations
        self.triggered_procedures: list[TriggeredProcedure] = triggered_procedures

    def get_name(self): return self.name

    def elaborate(self, 
                  path: str, 
                  name: str,
                  param_map: dict[str, str], 
                  module_defs: dict[str, ModuleDefinition], 
                  context: EvalContext):

        # Register the function definitions into a global repository
        for fd in self.function_definitions:
            context.func_def_reg.add_function(join_name(path, name, fd.get_name()), 
                fd.elaborate(join_name(path, name), context))
        
        # Create some additional assignments to wire the module parameters. 
        # These assignments depend on the direction of the port.
        for inner_name, global_outer_name in param_map.items():

            # Globalize the names involved in the port assignment
            global_inner_name = join_name(path, name, inner_name)

            # Find the appropriate port 
            pd = None
            for potential_pd in self.port_declarations:
                if potential_pd.get_name() == inner_name:
                    pd = potential_pd
                    break
            if not pd:
                raise Exception("Port not defined " + inner_name)

            if pd.port_type == PortType.INPUT:
                # Register the assignment: inner <- outer
                # NOTE: We assume that the outer name is already declared
                context.signal_reg.declare_net(global_inner_name, NetType.WIRE)
                context.signal_reg.add_assignment(global_inner_name,
                                              VariableExpression(global_outer_name))                                                 
            elif pd.port_type == PortType.OUTPUT:
                # Register the assignment: outer <- inner
                # NOTE: We assume that the outer name is already declared
                # TODO: THE PORT ASSIGNMENTS CAN BE VARIABLES OR WIRES
                context.signal_reg.declare_net(global_inner_name, NetType.WIRE)
                context.signal_reg.add_assignment(global_outer_name,
                                              VariableExpression(global_inner_name))                                                 
            else:
                raise Exception("Invalid port type")

        # Register the net declarations into a global repository
        # Ex:
        #   wire a;
        for nd in self.net_declarations:
            global_net_name = join_name(path, name, nd.get_name())
            context.signal_reg.declare_net(global_net_name, nd.get_net_type())
            # Set the initial value
            context.value_state.set_value(global_net_name, LOGIC_X)

        # Register the variable declarations into a global repository
        # Ex:
        #   reg a;
        #   reg b = 1;
        for vd in self.var_declarations:
            global_signal_name = join_name(path, name, vd.get_name())
            context.signal_reg.declare_variable(global_signal_name, vd.get_var_type())
            # Set the initial value
            if vd.id.init_exp:
                # Make sure the expression is a constant
                if not vd.id.init_exp.is_constant():
                    raise Exception("Non-constant initialization of variable " + global_signal_name)
                # No context is being passed - should not be needed for a constant!
                context.value_state.set_value(global_signal_name, vd.id.init_exp.evaluate(None))
            # Default initial value is X
            else:
                context.value_state.set_value(global_signal_name, LOGIC_X)

        # Instantiate the required global assignments (stand-alone assignments)
        # Ex:
        #   assign a = (b | c);
        for na in self.net_assignments:
            global_net_name = join_name(path, name, na.get_name())
            # Globalize the RHS of the assignment
            # TODO: DEAL WITH LOCAL VARIABLE LIST
            global_exp = na.exp.globalize(join_name(path, name), [])
            # Add the assignment to the global registry
            context.signal_reg.add_assignment(global_net_name, global_exp)

        # Instantiate the required global assignments (assignments that are part of the declarations)
        # Ex: 
        #   wire a = (b | c);
        for nd in self.net_declarations:
            if nd.exp:
                global_net_name = join_name(path, name, nd.get_name())
                # Globalize the RHS of the assignment
                # TODO: DEAL WITH LOCAL VARIABLE LIST
                global_exp = nd.exp.globalize(join_name(path, name), [])
                # Add the assignment to the global registry
                context.signal_reg.add_assignment(global_net_name, global_exp)

        # Setup the triggers
        for tp in self.triggered_procedures:
            # Elaborate the procedure for this context
            # TODO: LOCAL VARIABLES?
            elaborated_pb = tp.procedure_block.elaborate(join_name(path, name), [], context)      
            # Setup a trigger for each name in the sensitivity list
            for id in tp.identifiers:
                global_net_name = join_name(path, name, id)
                context.signal_reg.add_triggered_procedure(global_net_name, elaborated_pb)

        # Deal with next level down of modules
        for mi in self.module_instantiations:
            module_def = module_defs[mi.name]
            # Make a mapping between the child's parameter names and the parent's 
            # actual signal names.
            child_param_map = {}
            for port in mi.ports:
                child_param_map[port.inside_name] = join_name(path, name, port.outside_name)
            module_def.elaborate(join_name(path, name), mi.instance_name,
                child_param_map, module_defs, context)

    def __repr__(self):
        s = "module " + self.name + "("
        first = True
        for pd in self.port_declarations:
            if not first:
                s = s + ","
            s = s + str(pd)
            first = False
        s = s + ");\n"
        for nd in self.net_declarations:
            s = s + str(nd) + ";\n"
        for vd in self.var_declarations:
            s = s + str(vd) + ";\n"
        for fd in self.function_definitions:
            s = s + str(fd)
        for na in self.net_assignments:
            s = s + str(na) + ";\n"
        for mi in self.module_instantiations:
            s = s + str(mi) + ";\n"
        for tp in self.triggered_procedures:
            s = s + str(tp) 
        s = s + "endmodule"
        return s

# ===== Simulation Engine =====================================================

class ValueState:

    def __init__(self):
        self.state: dict[str, Value] = {}

    # Sets a value and returns an indication of whether the value was changed
    # as a result.
    def set_value(self, name: str, value: Value) -> bool:
        changed = (not name in self.state) or (not self.state[name] == value)
        self.state[name] = value
        return changed

    def get_value(self, name: str) -> Value: 
        if not name in self.state:
            return LOGIC_X
        else:
            return self.state[name]

    def is_value_available(self, name: str) -> bool: 
        return name in self.state

class SignalInformation:

    def __init__(self, name: str, data_type: DataType, net_type: NetType, var_type: VariableType):
        self.name = name
        self.data_type = data_type 
        self.net_type = net_type
        self.var_type = var_type
        self.assignments: list[Expression] = []
        self.dirty: bool = True  
        # These are procedure blocks that should be executed 
        # whenever the net is changed.
        self.triggered_procedure_blocks: list[ProcedureBlock] = []

    def has_any_drivers(self) -> bool:
        return len(self.assignments) > 0

# Used for storing net types and assignments
class SignalRegistry:

    def __init__(self, value_state: ValueState):
        self.value_state = value_state
        self.reg: dict[str, SignalInformation] = {}

    def declare_net(self, name: str, net_type: NetType):
        self.reg[name] = SignalInformation(name, DataType.NET, net_type, None)
        # Initial value
        self.value_state.set_value(name, LOGIC_X)

    def is_net(self, name: str) -> bool:
        return name in self.reg and self.reg[name].data_type == DataType.NET

    def declare_variable(self, name: str, var_type: VariableType):
        self.reg[name] = SignalInformation(name, DataType.VARIABLE, None, var_type)
        # Initial value
        self.value_state.set_value(name, LOGIC_X)

    def is_variable(self, name: str) -> bool:
        return name in self.reg and self.reg[name].data_type == DataType.VARIABLE

    def add_assignment(self, name: str, exp: Expression):
        if not name in self.reg:
            raise Exception("Attempt to add assignment to undeclared net " + name)
        if self.reg[name].data_type != DataType.NET:
            raise Exception("Attempt to assign value to register")
        self.reg[name].assignments.append(exp)

    def add_triggered_procedure(self, name: str, procedure_block: ProcedureBlock):
        if not name in self.reg:
            raise Exception("Attempt to add assignment to undeclared net " + name)
        self.reg[name].triggered_procedure_blocks.append(procedure_block)

    def debug(self):
        for name, decl in self.reg.items():
            s = name + " [" + str(decl.data_type) + "] " 
            if decl.data_type == DataType.NET:
                s = s + " <- " + str(decl.assignments)
            if len(decl.triggered_procedure_blocks) > 0:
                for pb in decl.triggered_procedure_blocks:
                    s = s + "\n"
                    s = s + "Triggered Block:"
                    s = s + str(pb)
            print(s)

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
        self.signal_reg = SignalRegistry(self.value_state)
        self.non_blocking_queue: list[UpdateEvent] = []
        self.triggered_queue: list[ProcedureBlock] = []
    
    def is_variable(self, name) -> bool:
        return self.signal_reg.is_variable(name)

    def is_net(self, name) -> bool:
        return self.signal_reg.is_net(name)

    def start(self):
        # Evaluate everything once to make sure all initial conditions are
        # reflected properly.
        self.update_dirty_signals()
        self.process_non_blocking_queue()

    def get_value(self, name: str):
        if not self.value_state.is_value_available(name):
            raise Exception("No value available for " + name)
        return self.value_state.get_value(name)
    
    def set_value_blocking(self, name: str, value: Value):
        self.set_value_internal(name, value)
        self.update_dirty_signals()

    def set_value_non_blocking(self, name: str, value: Value):
        self.non_blocking_queue.append(UpdateEvent(name, value))

    def process_non_blocking_queue(self):
        while len(self.non_blocking_queue) > 0:
            non_blocking_queue = self.non_blocking_queue.copy()
            self.non_blocking_queue.clear()
            for event in non_blocking_queue:
                self.set_value_internal(event.name, event.value)
            self.update_dirty_signals()

    def set_value_internal(self, name: str, value: Value):

        # Save and check to see if this value has changed since the last time
        changed = self.value_state.set_value(name, value)
        if changed:
            print("Setting", name, "<-", value)
            # Figure out which nets need to be recomputed now as a result
            for net_name, net_info in self.signal_reg.reg.items():
                # Each signal can have multiple assignments contributing to it
                for assignment in net_info.assignments:
                    if name in assignment.get_references():
                        net_info.dirty = True

            # Figure out what blocks need to be triggered now as a result of 
            # this change. There is no need to queue the same procedure block
            # more than once.
            for pb in self.signal_reg.reg[name].triggered_procedure_blocks:
                if not pb in self.triggered_queue:
                    self.triggered_queue.append(pb)

    def update_dirty_signals(self):

        # We keep looping here because each set may cause other signals to 
        # require a recomputation.        
        while True:

            # Fire off any triggers that are pending
            triggered_queue = self.triggered_queue.copy()
            self.triggered_queue.clear()
            for triggered in triggered_queue:
                triggered.execute(self)

            # Now deal with propagation of values
            dirty_count = 0

            for net_name, signal_info in self.signal_reg.reg.items():
                if signal_info.data_type == DataType.NET and signal_info.dirty:
                    dirty_count = dirty_count + 1
                    if signal_info.has_any_drivers():
                        # The net may have more than one driver, so evaluate them all
                        driving_values = []
                        for assignment in signal_info.assignments:
                            driving_value = assignment.evaluate(self)
                            driving_values.append(driving_value)
                        # Combine the values of the drivers to a single value
                        new_value = wire_logic_eval(driving_values, signal_info.net_type)
                        self.set_value_internal(net_name, new_value)

                    # Clear dirty flag
                    signal_info.dirty = False

            if dirty_count == 0:
                return

    def get_function_def(self, name:str):
        return self.func_def_reg.get_function_def(name)

class UpdateEvent:

    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return "UpdateEvent: " + self.name + " = " + str(self.value)

class Engine:

    def __init__(self):
        self.parser = lark.Lark.open("./sim2.lark")
        self.module_defs: dict[str, ModuleDefinition] = {}
        self.first_module_name = None 

    def load_module_files(self, file_names: list[str]):
        for name in file_names:
            tree = self.parser.parse(open(name).read())
            result = Transformer().transform(tree)
            # Move the modules into a map
            for module_def in result:
                if self.first_module_name == None:
                    self.first_module_name = module_def.get_name()
                self.module_defs[module_def.get_name()] = module_def

    def load_module_from_text(self, text: str):
        tree = self.parser.parse(text)
        result = Transformer().transform(tree)
        # Move the modules into a map
        for module_def in result:
            if self.first_module_name == None:
                self.first_module_name = module_def.get_name()
            self.module_defs[module_def.get_name()] = module_def

    def get_value(self, name: str) -> Value:
        return self.eval_context.get_value(name)

    def set_value(self, name: str, value: Value):
        return self.eval_context.set_value_blocking(name, value)

    def start(self):     

        self.eval_context = EvalContext()

        # Elaboration
        param_map = {}

        self.module_defs[self.first_module_name].elaborate(None, 
            #self.first_module_name,
            None,
            param_map, 
            self.module_defs, 
            self.eval_context)

        self.eval_context.signal_reg.debug()
        self.eval_context.start()
        
    def tick(self):
        # Clean up from the previous cycle
        self.eval_context.process_non_blocking_queue()

# ===== Lark Transformer ======================================================

class MultiNetDeclaration:

    def __init__(self, names: list[str], net_type: NetType):
        self.names = names
        self.net_type = net_type

class MultiVariableDeclaration:

    def __init__(self, var_type: VariableType, ids: list[IdentifierWithInit]):
        self.var_type = var_type
        self.ids = ids

class Transformer(lark.visitors.Transformer):

    def IDENTIFIER(self, items):
        return str(items)

    def BINARY_CONSTANT(self, items):
        return parse_binary_constant(str(items))

    def SIGNED_NUMBER(self, items):
        return int(str(items))

    def WIRE(self, items): return NetType.WIRE
    def TRI(self, items): return NetType.WIRE
    def WAND(self, items): return NetType.WAND
    def WOR(self, items): return NetType.WOR
    def SUPPLY0(self, items): return NetType.SUPPLY0
    def SUPPLY1(self, items): return NetType.SUPPLY1

    def REG(self, items): return VariableType.REG
    def INTEGER(self, items): return VariableType.INTEGER

    def INPUT(self, items): return PortType.INPUT
    def OUTPUT(self, items): return PortType.OUTPUT

    def start(self, items) -> list[ModuleDefinition]:
        # Return an array of ModuleDefinitions
        return items

    def module(self, items) -> ModuleDefinition:
        nds = []
        nas = []
        mis = []
        fds = []
        vds = []
        tps = []
        # Distribute the module statements into the proper buckets
        for statement in items[2]:
            if type(statement) is NetDeclaration:
                nds.append(statement)
            # The MutliNetDeclaration is expanded into a series of NetDeclarations
            elif type(statement) is MultiNetDeclaration:
                for name in statement.names:
                    nds.append(NetDeclaration(name, statement.net_type))
            elif type(statement) is NetAssignment:
                nas.append(statement)
            elif type(statement) is ModuleInstantiation:
                mis.append(statement)
            elif type(statement) is FunctionDefinition:
                fds.append(statement)
            elif type(statement) is VariableDeclaration:
                vds.append(statement)
            # This is a special class used to pass multiple variable declarations
            # in a single object. We divide it into its individual parts here.
            elif type(statement) is MultiVariableDeclaration:
                for id in statement.ids:
                    vds.append(VariableDeclaration(statement.var_type, id))
            elif type(statement) is TriggeredProcedure:
                tps.append(statement)
            else:
                raise Exception("Unrecognized statement type " + str(type(statement)))
        return ModuleDefinition(items[0], items[1], nds, nas, mis, fds, vds, tps)

    def portdeclarations(self, items):
        return items

    def portdeclaration(self, items):
        return PortDeclaration(items[1], items[0])

    def porttype(self, items):
        return items[0]

    def modulestatements(self, items):
        return items

    def modulestatement(self, items):
        return items[0]

    def netdeclaration(self, items):
        # items[1] is a list of strings (the identifiers)
        return MultiNetDeclaration(items[1], items[0])

    def variabledeclaration(self, items):
        # items[0] is the VariableType
        # items[1] is a list of IdentifierWithInits
        return MultiVariableDeclaration(items[0], items[1])
    
    def identifier_with_inits(self, items):
        return items
    
    def identifier_with_init(self, items):
        # items[0] is the identifier name
        return IdentifierWithInit(items[0], None)

    def identifier_with_init_exp(self, items):
        # items[0] is the identifier name
        # items[1] is the expression
        return IdentifierWithInit(items[0], items[1])

    def identifiers(self, items) -> list[str]:
        return items

    def netdeclaration_assign(self, items):
        return NetDeclaration(items[1], items[0], items[2]) 

    def netassignment(self, items):
        return NetAssignment(items[0], items[1])

    def functiondeclaration(self, items):
        local_variables = []
        return FunctionDefinition(items[0], items[1], local_variables, ProcedureBlock(items[2]))

    def paramdeclarations(self, items):
        return items

    def paramdeclaration(self, items):
        return FunctionParameterDeclaration(items[1], items[0])

    def moduleinstantiation(self, items):
        return ModuleInstantiation(items[0], items[1], items[2])

    def nettype(self, items):
        return items[0]

    def variabletype(self, items):
        return items[0]

    def port_assignments(self, items):
        return items

    def port_assignment_id(self, items):
        return PortAssignment(items[0], items[1])

    def port_assignment_exp(self, items):
        raise Exception("Not supported yet")   

    def functionbody_single(self, items):
        return [ items[0] ]
    
    def functionbody_block(self, items):
        return items[0]
    
    def functionbody_none(self, items):
        return [ ]

    def functionstatements(self, items):
        return items

    def functionstatement(self, items):
        return items[0]
      
    def procedurestatements(self, items):
        return items
    
    def procedurestatement(self, items):
        return items[0]

    def procedureassignment_blocking(self, items):
        return ProcedureAssignment(items[0], items[1], True)

    def procedureassignment_non_blocking(self, items):
        return ProcedureAssignment(items[0], items[1], False)

    def always(self, items):
        # items[0] - identifiers
        # items[1] - procedurestatements
        return TriggeredProcedure(items[0], ProcedureBlock(items[1]))        

    # ----- Expression Stuff --------------------------------------------------

    def exps(self, items):
        return items

    def exp_or(self, tree):
        return BinaryExpression("|", tree[0], tree[1])

    def exp_and(self, tree):
        return BinaryExpression("&", tree[0], tree[1])

    def exp_xor(self, tree):
        return BinaryExpression("^", tree[0], tree[1])

    def exp_eq(self, tree):
        return BinaryExpression("==", tree[0], tree[1])

    def exp_neq(self, tree):
        return BinaryExpression("!=", tree[0], tree[1])

    def exp_eq3(self, tree):
        return BinaryExpression("===", tree[0], tree[1])

    def exp_neq3(self, tree):
        return BinaryExpression("!==", tree[0], tree[1])
    
    def exp_lt(self, tree):
        return BinaryExpression("<", tree[0], tree[1])

    def exp_lte(self, tree):
        return BinaryExpression("<=", tree[0], tree[1])

    def exp_gt(self, tree):
        return BinaryExpression(">", tree[0], tree[1])

    def exp_gte(self, tree):
        return BinaryExpression(">=", tree[0], tree[1])

    def exp_not(self, tree):
        return UnaryExpression("!", tree[0])

    def exp_paren(self, tree):
        return tree[0]

    def exp_func(self, items):
        return FunctionExpression(items[0], items[1])

    def exp_id(self, items):
        return VariableExpression(items[0])

    def exp_binary_constant(self, items):
        return ConstantExpression(items[0])
    
    def exp_signed_number(self, items):
        return ConstantExpression(Value(items[0]))

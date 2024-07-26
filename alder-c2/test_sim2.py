import sim2 

def test_1():

    # A simple expression: !(a & e)
    e0 = sim2.VariableExpression("a")
    e1 = sim2.VariableExpression("e")
    e3 = sim2.BinaryExpression("&", e0, e1)
    e4 = sim2.UnaryExpression("!", e3)
    assert sorted(e4.get_references()) == [ "a", "e" ]

    # Put the expression into an assignment: b = !(a & e)
    s0 = sim2.ProcedureAssignment("b", e4)
    assert sorted(s0.get_references()) == [ "a", "e" ]

    # Put the assignment into a procedure block
    b0 = sim2.ProcedureBlock([ s0 ])
    assert sorted(b0.get_references()) == [ "a", "e" ]

    # Put the procedure block into a function
    a0 = [ sim2.FunctionParameter("a") ]
    a1 = [ ]
    fd0 = sim2.FunctionDefinition("b", a0, a1, b0)
    # "a" is no longer a reference because it is assumed to be 
    # handled by the caller of the function.
    assert sorted(fd0.get_references()) == [ "e" ]

    # Now execute the function a few ways
    value_state = sim2.ValueState()

    f0 = sim2.FunctionExpression(fd0, [ sim2.ConstantExpression(sim2.Value(True)) ])
    result = f0.evaluate(value_state)
    assert result == sim2.Value("X")

    value_state.set_value("e", sim2.LOGIC_0)
    f0 = sim2.FunctionExpression(fd0, [ sim2.ConstantExpression(sim2.Value(True)) ])
    result = f0.evaluate(value_state)
    assert result == sim2.Value(True)

    f0 = sim2.FunctionExpression(fd0, [ sim2.ConstantExpression(sim2.Value(False)) ])
    value_state.set_value("e", sim2.LOGIC_1)
    result = f0.evaluate(value_state)
    assert result == sim2.Value(True)

    f0 = sim2.FunctionExpression(fd0, [ sim2.ConstantExpression(sim2.Value(True)) ])
    value_state.set_value("e", sim2.LOGIC_1)
    result = f0.evaluate(value_state)
    assert result == sim2.Value(False)

# A basic wire demonstration
def test_2():

    # List of net declarations
    nds = [ sim2.NetDeclaration("a", sim2.NetType.WIRE), 
            sim2.NetDeclaration("b", sim2.NetType.WIRE) ]
    # List of net assignments
    e0 = sim2.BinaryExpression("|", 
                               sim2.VariableExpression("b"), 
                               sim2.ConstantExpression(sim2.LOGIC_0))
    e1 = sim2.ConstantExpression(sim2.Value(1))    
    nas = [ sim2.NetAssignment("a", e0),
            sim2.NetAssignment("b", e1) ]
     
    # Define a module 
    md0 = sim2.ModuleDefinition("mod0", nds, nas)

    # Create a module instance
    value_state = sim2.ValueState()
    mi0 = sim2.ModuleInstance("m0", md0, value_state)
    mi0.init()

    active_queue = []

    # Change the value of "b"
    mi0.set_value("b", sim2.Value(0), active_queue)

    # Apply the events
    for event in active_queue:
        value_state.set_value(event.name, event.value)
    active_queue.clear()

    assert value_state.get_value("a") == sim2.Value(0)

    # Set the same value again, nothing should happen
    mi0.set_value("b", sim2.Value(0), active_queue)

    # We should have no events at this point
    assert len(active_queue) == 0

# Logic level tests
def test_3():

    assert sim2.logic_eval_or(sim2.LOGIC_1, sim2.LOGIC_X) == sim2.LOGIC_1
    assert sim2.logic_eval_and(sim2.LOGIC_1, sim2.LOGIC_X) == sim2.LOGIC_X
    assert sim2.logic_eval_and(sim2.LOGIC_1, sim2.LOGIC_Z) == sim2.LOGIC_X

    drivers = [ sim2.LOGIC_0, sim2.LOGIC_1, sim2.LOGIC_Z ]
    assert sim2.wire_logic_eval(drivers, sim2.NetType.WAND) == sim2.LOGIC_0
    assert sim2.wire_logic_eval(drivers, sim2.NetType.WOR) == sim2.LOGIC_1

    drivers = [ sim2.LOGIC_1, sim2.LOGIC_1, sim2.LOGIC_X, sim2.LOGIC_Z ]
    assert sim2.wire_logic_eval(drivers, sim2.NetType.WAND) == sim2.LOGIC_X

# A wire-OR example
def test_4():

    print("----- test_3 ------------------------------------------------------")

    # List of net declarations
    nds = [ sim2.NetDeclaration("a", sim2.NetType.WOR), 
            sim2.NetDeclaration("b", sim2.NetType.WIRE),
            sim2.NetDeclaration("c", sim2.NetType.WIRE) ]

    # List of net assignments
    e0 = sim2.VariableExpression("b")
    e1 = sim2.VariableExpression("c")

    # Notice that a is driven by two values
    nas = [ sim2.NetAssignment("a", e0),
            sim2.NetAssignment("a", e1) ]

    # Define a module 
    md0 = sim2.ModuleDefinition("mod0", nds, nas)

    # Create a module instance
    value_state = sim2.ValueState()
    mi0 = sim2.ModuleInstance("m0", md0, value_state)
    mi0.init()

    active_queue = []

    mi0.set_value("b", sim2.Value(0), active_queue)
    mi0.set_value("c", sim2.Value(0), active_queue)

    # Apply the events
    for event in active_queue:
        value_state.set_value(event.name, event.value)
    active_queue.clear()

    assert value_state.get_value("a") == sim2.Value(0)

    # Set one of the two drivers to 1
    mi0.set_value("b", sim2.Value(1), active_queue)
    # Apply the events
    for event in active_queue:
        value_state.set_value(event.name, event.value)
    active_queue.clear()

    # Should see wire-OR
    assert value_state.get_value("a") == sim2.Value(1)

test_1()
test_2()
test_3()
test_4()
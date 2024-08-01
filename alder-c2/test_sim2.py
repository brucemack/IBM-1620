import lark
import sim2 

def test_1():

    # A simple expression: !(a & e)
    e0 = sim2.VariableExpression("a")
    e1 = sim2.VariableExpression("e")
    e3 = sim2.BinaryExpression("&", e0, e1)
    e4 = sim2.UnaryExpression("!", e3)
    assert sorted(e4.get_references()) == [ "a", "e" ]

    # Put the expression into an assignment: b = !(a & e)
    s0 = sim2.ProcedureAssignment("b", e4, True)
    assert sorted(s0.get_references()) == [ "a", "e" ]

    # Put the assignment into a procedure block
    b0 = sim2.ProcedureBlock([ s0 ])
    assert sorted(b0.get_references()) == [ "a", "e" ]

    # Put the procedure block into a function
    #
    # function b(a);
    #   begin
    #     b = !(a & e)
    #   end
    # endfunction 

    a0 = [ sim2.FunctionParameterDeclaration("a", sim2.PortType.INPUT) ]
    a1 = [ ]
    fd0 = sim2.FunctionDefinition("b", a0, a1, b0)
    # "a" is no longer a reference because it is assumed to be 
    # handled by the caller of the function.
    assert sorted(fd0.get_references()) == [ "e" ]

    # Elaborate the function
    fd1 = fd0.elaborate("root", None)
    
    # Setup the context
    eval_context = sim2.EvalContext()
    eval_context.func_def_reg.add_function("root.b", fd1)

    # Now execute the function a few ways
    eval_context.value_state.set_value("root.e", sim2.Value("X"))
    f0 = sim2.FunctionExpression("root.b", [ sim2.ConstantExpression(sim2.Value(True)) ])
    result = f0.evaluate(eval_context)
    assert result == sim2.Value("X")

    eval_context.value_state.set_value("root.e", sim2.LOGIC_0)
    f0 = sim2.FunctionExpression("root.b", [ sim2.ConstantExpression(sim2.Value(True)) ])
    result = f0.evaluate(eval_context)
    assert result == sim2.Value(True)

    eval_context.value_state.set_value("root.e", sim2.LOGIC_1)
    f0 = sim2.FunctionExpression("root.b", [ sim2.ConstantExpression(sim2.Value(False)) ])
    result = f0.evaluate(eval_context)
    assert result == sim2.Value(True)

    eval_context.value_state.set_value("root.e", sim2.LOGIC_1)
    f0 = sim2.FunctionExpression("root.b", [ sim2.ConstantExpression(sim2.Value(True)) ])
    result = f0.evaluate(eval_context)
    assert result == sim2.Value(False)

# A basic wire demonstration
def test_2():

    print("----- test_2 ------------------------------------------------------")

    """
    module mod0();
      wire a;
      wire b;
      assign a = b | 0;
      assign b = 1;
    endmodule
    """

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
    module_defs: dict[str, sim2.ModuleDefinition] = {}
    module_defs["mod0"] = sim2.ModuleDefinition("mod0", [ ], nds, nas, [ ], [ ], [ ], [ ])

    # Elaborate a module instance
    eval_context = sim2.EvalContext()
    param_map = {}
    module_defs["mod0"].elaborate("root", 
                                  "main", 
                                  param_map, 
                                  module_defs, 
                                  eval_context)
    
    eval_context.start()

    # Change the value of "b" and demonstrate that "a" is changed as well
    eval_context.set_value_blocking("root.main.b", sim2.Value(0)) 
    assert eval_context.value_state.get_value("root.main.a") == sim2.Value(0)

    # Set the same value again, nothing should happen
    eval_context.set_value_blocking("root.main.b", sim2.Value(0))

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

    print("----- test_4 ------------------------------------------------------")

    """
    module mod0();
      wor a;
      wire b;
      wire c;
      // Notice here we are assigning to the same net twice
      assign a = b;
      assign a = c;
    endmodule
    """
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
    module_defs: dict[str, sim2.ModuleDefinition] = {}
    module_defs["mod0"] = sim2.ModuleDefinition("mod0", [ ], nds, nas, [ ], [ ], [ ], [ ])

    # Instantiate the module

    # Elaborate a module instance
    eval_context = sim2.EvalContext()
    param_map = {}
    module_defs["mod0"].elaborate("root", 
                                  "main", 
                                  param_map, 
                                  module_defs, 
                                  eval_context)
    eval_context.start()
    
    eval_context.set_value_blocking("root.main.b", sim2.Value(0))
    eval_context.set_value_blocking("root.main.c", sim2.Value(0))

    assert eval_context.value_state.get_value("root.main.a") == sim2.Value(0)

    # Set one of the two drivers to 1
    eval_context.set_value_blocking("root.main.b", sim2.Value(1))

    # Should see wire-OR
    assert eval_context.value_state.get_value("root.main.a") == sim2.Value(1)

# A module with a sub-module
def test_5():

    print("----- test_5 ------------------------------------------------------")

    """
    module mod0();
      wire a = 1;
      wire b = 0;
      wire c;
      and m0(.x(a), .y(b), .z(c));
    endmodule;
    module and(input x, input y, output z);
      z = x & y;
    endmodule;
    """

    module_defs = {}

    # Port declarations
    ports = []
    # Net definitions
    nds = [ sim2.NetDeclaration("a", sim2.NetType.WIRE),
            sim2.NetDeclaration("b", sim2.NetType.WIRE),
            sim2.NetDeclaration("c", sim2.NetType.WIRE) ]
    # Net assignments
    nas = [ sim2.NetAssignment("a", sim2.ConstantExpression(sim2.Value(True))),
            sim2.NetAssignment("b", sim2.ConstantExpression(sim2.Value(False))) ]
    # Module instantiations
    mis = [ sim2.ModuleInstantiation("and", "m0", [ sim2.PortAssignment("x", "a"), 
                                                    sim2.PortAssignment("y", "b"),                                                sim2.PortAssignment("z", "c") ] ) ]
    # Function definitions 
    fds = []
    # Define a module 
    module_defs["mod0"] = sim2.ModuleDefinition("mod0", ports, nds, nas, mis, fds, [ ], [ ])

    # Port declarations
    ports = [ sim2.PortDeclaration("x", sim2.PortType.INPUT),
              sim2.PortDeclaration("y", sim2.PortType.INPUT),
              sim2.PortDeclaration("z", sim2.PortType.OUTPUT) ]
    # Net definitions
    nds = [ ]
    # Net assignments
    nas = [ sim2.NetAssignment("z", 
                               sim2.BinaryExpression("&",
                                                     sim2.VariableExpression("x"), 
                                                     sim2.VariableExpression("y"))) ]
    # Module instantiations
    mis = [ ]
    # Function definitions 
    fds = []
    # Define a module 
    module_defs["and"] = sim2.ModuleDefinition("and", ports, nds, nas, mis, fds, [], [])

    # Elaboration
    eval_context = sim2.EvalContext()
    param_map = {}

    module_defs["mod0"].elaborate("root", 
                                  "main", 
                                  param_map, 
                                  module_defs, 
                                  eval_context)
    eval_context.start()

    # Test initial value
    assert eval_context.value_state.get_value("root.main.c") == sim2.LOGIC_0

    # Set some values to show that the submodule is working
    eval_context.set_value_blocking("root.main.b", sim2.Value(1))
    assert eval_context.value_state.get_value("root.main.c") == sim2.LOGIC_1

# A module with a sub-module that contains a function
def test_6():

    print("----- test_6 ------------------------------------------------------")

    """
    module mod0();
      wire a = 1;
      wire b = 0;
      wire c;
      and m0(.x(a), .y(b), .z(c));
    endmodule;
    module and(input x, input y, output z);
      function p(input q, input r);
        begin
          p = q & r;
        end
      endfunction
      z = p(x, y);
    endmodule;
    """

    module_defs = {}

    # Port declarations
    ports = []
    # Net definitions
    nds = [ sim2.NetDeclaration("a", sim2.NetType.WIRE),
            sim2.NetDeclaration("b", sim2.NetType.WIRE),
            sim2.NetDeclaration("c", sim2.NetType.WIRE) ]
    # Net assignments
    nas = [ sim2.NetAssignment("a", sim2.ConstantExpression(sim2.Value(True))),
            sim2.NetAssignment("b", sim2.ConstantExpression(sim2.Value(False))) ]
    # Module instantiations
    mis = [ sim2.ModuleInstantiation("and1", "m0", [ sim2.PortAssignment("x", "a"), 
                                                    sim2.PortAssignment("y", "b"),                                                sim2.PortAssignment("z", "c") ] ) ]
    # Function definitions 
    fds = []
    # Define a module 
    module_defs["mod0"] = sim2.ModuleDefinition("mod0", ports, nds, nas, mis, fds, [ ], [ ])

    # Port declarations
    ports = [ sim2.PortDeclaration("x", sim2.PortType.INPUT),
              sim2.PortDeclaration("y", sim2.PortType.INPUT),
              sim2.PortDeclaration("z", sim2.PortType.OUTPUT) ]
    # Net definitions
    nds = [ ]
    # Net assignments
    nas = [ sim2.NetAssignment("z", sim2.FunctionExpression("p", [
                sim2.VariableExpression("x"), 
                sim2.VariableExpression("y") 
            ]))
        ]
    # Module instantiations
    mis = [ ]
    # Function definitions 
    fds = [ sim2.FunctionDefinition("p", 
                [ sim2.FunctionParameterDeclaration("q", sim2.PortType.INPUT), 
                  sim2.FunctionParameterDeclaration("r", sim2.PortType.INPUT) ], 
                [], 
                sim2.ProcedureBlock( [ sim2.ProcedureAssignment("p",
                                                                sim2.BinaryExpression("&", 
                                                                  sim2.VariableExpression("q"),
                                                                  sim2.VariableExpression("r")),
                                                                True) ] ) )
          ]
    # Define a module 
    module_defs["and1"] = sim2.ModuleDefinition("and1", ports, nds, nas, mis, fds, [ ], [ ])

    # Elaboration
    eval_context = sim2.EvalContext()
    param_map = {}

    module_defs["mod0"].elaborate("root", 
                                  "main", 
                                  param_map, 
                                  module_defs, 
                                  eval_context)

    eval_context.start()

    # Test initial value
    assert eval_context.value_state.get_value("root.main.a") == sim2.LOGIC_1
    assert eval_context.value_state.get_value("root.main.b") == sim2.LOGIC_0
    assert eval_context.value_state.get_value("root.main.c") == sim2.LOGIC_0

    # Set some values to show that the submodule is working
    eval_context.set_value_blocking("root.main.b", sim2.Value(1))
    assert eval_context.value_state.get_value("root.main.c") == sim2.LOGIC_1

def test_7():

    print("----- test_7 ------------------------------------------------------")

    parser = lark.Lark.open("./sim2.lark")
    tree = parser.parse(
"""
// Test
module mod0();
  wire a = 1'b1;
  wire b = 1'b0;
  wire c;
  and m0(.x(a), .y(b), .z(c));
endmodule
module and(input x, input y, output z);
  function p(input q, input r);
    begin
      p = q & r;
    end
  endfunction
  assign z = p(x, y);
endmodule
"""
    )

    result = sim2.Transformer().transform(tree)

    # Move the modules into a map
    module_defs = {}
    for module_def in result:
        module_defs[module_def.get_name()] = module_def

    # Elaboration
    eval_context = sim2.EvalContext()
    param_map = {}

    module_defs["mod0"].elaborate("root", 
                                  "main", 
                                  param_map, 
                                  module_defs, 
                                  eval_context)

    eval_context.start()

    # Test initial values
    assert eval_context.value_state.get_value("root.main.a") == sim2.LOGIC_1
    assert eval_context.value_state.get_value("root.main.b") == sim2.LOGIC_0
    assert eval_context.value_state.get_value("root.main.c") == sim2.LOGIC_0

    # Set some values to show that the submodule is working
    eval_context.set_value_blocking("root.main.b", sim2.Value(1))
    assert eval_context.value_state.get_value("root.main.c") == sim2.LOGIC_1

def test_7a():

    print("----- test_7a ------------------------------------------------------")

    engine = sim2.Engine()
    engine.load_module_from_text(
"""
// Test
module mod0();
//  wire a = 1'b1;
//  wire b = 1'b0;
  wire a, b;
  assign a = 1'b1;
  assign b = 1'b0;
  wire c;
  and m0(.x(a), .y(b), .z(c));
endmodule
module and(input x, input y, output z);
  function p(input q, input r);
    begin
      p = q & r;
    end
  endfunction
  assign z = p(x, y);
endmodule
"""
    )

    engine.start()

    # Test initial values
    assert engine.get_value("mod0.a") == sim2.LOGIC_1
    assert engine.get_value("mod0.b") == sim2.LOGIC_0
    assert engine.get_value("mod0.c") == sim2.LOGIC_0

    # Set some values to show that the submodule is working
    engine.set_value("mod0.b", sim2.Value(1))
    assert engine.get_value("mod0.c") == sim2.LOGIC_1

# Testing equality
def test_8():
    
  exp = sim2.BinaryExpression("==", 
                              sim2.ConstantExpression(sim2.Value(0)), 
                              sim2.ConstantExpression(sim2.Value(0)))
  assert exp.evaluate(None) == sim2.LOGIC_1  

  exp = sim2.BinaryExpression("==", 
                              sim2.ConstantExpression(sim2.Value("Z")), 
                              sim2.ConstantExpression(sim2.Value(0)))
  assert exp.evaluate(None) == sim2.LOGIC_X

  exp = sim2.BinaryExpression("!=", 
                              sim2.ConstantExpression(sim2.Value("Z")), 
                              sim2.ConstantExpression(sim2.Value(0)))
  assert exp.evaluate(None) == sim2.LOGIC_X

  exp = sim2.BinaryExpression("===", 
                              sim2.ConstantExpression(sim2.Value("Z")), 
                              sim2.ConstantExpression(sim2.Value(0)))
  assert exp.evaluate(None) == sim2.LOGIC_0

  exp = sim2.BinaryExpression("===", 
                              sim2.ConstantExpression(sim2.Value("Z")), 
                              sim2.ConstantExpression(sim2.Value("Z")))
  assert exp.evaluate(None) == sim2.LOGIC_1

def test_9():

    print("----- test_9 ------------------------------------------------------")

    engine = sim2.Engine()
    engine.load_module_from_text(
"""
// Test
module mod0();
  reg a;
  reg b;
  reg c, d;
  // Initial value
  reg f = 1'b1;
  // NOT ALLOWED, NON-CONSTANT
  //reg g = f;
  always @ (a) begin
    b = a;
    // Since c isn't in the sensitivity list, this won't fire
    // when c is changed.
    d = c;
  end
endmodule
"""
    )

    engine.start()

    # Test initial values
    assert engine.get_value("mod0.a") == sim2.LOGIC_X
    assert engine.get_value("mod0.b") == sim2.LOGIC_X
    assert engine.get_value("mod0.c") == sim2.LOGIC_X
    assert engine.get_value("mod0.d") == sim2.LOGIC_X
    assert engine.get_value("mod0.f") == sim2.LOGIC_1

    # Set some values to show that the submodule is working
    engine.set_value("mod0.a", sim2.Value(1))
    assert engine.get_value("mod0.b") == sim2.LOGIC_1
    assert engine.get_value("mod0.d") == sim2.LOGIC_X

def test_10():

  print("----- test_10 ------------------------------------------------------")

  engine = sim2.Engine()
  engine.load_module_files([ "../daves-1f/typewriter-mechanical.v" ])
  engine.start() 

  # Test the angle
  engine.set_value("typewriter._angle", sim2.Value(100))
  assert engine.get_value("typewriter.crcb_3no_sw") == sim2.LOGIC_1

  # Test a DUO Relay

  # Pick the relay
  engine.set_value("typewriter.r6_pick_coil", sim2.LOGIC_1)
  engine.tick()
  assert engine.get_value("typewriter.r6_1no_sw") == sim2.LOGIC_1

  # Here we transition from the pick coil to the hold coil - no change
  engine.set_value("typewriter.r6_pick_coil", sim2.LOGIC_0)
  engine.set_value("typewriter.r6_hold_coil", sim2.LOGIC_1)
  engine.tick()
  assert engine.get_value("typewriter.r6_1no_sw") == sim2.LOGIC_1

  # Here we release the hold
  engine.set_value("typewriter.r6_hold_coil", sim2.LOGIC_0)
  engine.tick()
  assert engine.get_value("typewriter.r6_1no_sw") == sim2.LOGIC_0

  # Test a latching relay

  engine.set_value("typewriter.r1_pick_coil", sim2.LOGIC_0)
  engine.set_value("typewriter.r1_trip_coil", sim2.LOGIC_0)

  # Pick the relay
  engine.set_value("typewriter.r1_pick_coil", sim2.LOGIC_1)
  engine.tick()
  assert engine.get_value("typewriter.r1_1no_sw") == sim2.LOGIC_1

  # Remove pick power and show that latch remains
  engine.set_value("typewriter.r1_pick_coil", sim2.LOGIC_0)
  engine.tick()
  assert engine.get_value("typewriter.r1_1no_sw") == sim2.LOGIC_1

  # Trip the relay
  engine.set_value("typewriter.r1_trip_coil", sim2.LOGIC_1)
  engine.tick()
  assert engine.get_value("typewriter.r1_1no_sw") == sim2.LOGIC_0

  # Remove trip power
  engine.set_value("typewriter.r1_trip_coil", sim2.LOGIC_0)
  engine.tick()
  assert engine.get_value("typewriter.r1_1no_sw") == sim2.LOGIC_0

test_1()
test_2()
test_3()
test_4()
test_5()
test_6()
test_7()
test_7a()
test_8()
test_9()
test_10()

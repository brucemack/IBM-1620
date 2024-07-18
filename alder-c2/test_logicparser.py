import lark
import logicbox

def test_1():

    parser = lark.Lark.open("./logic.lark")
    tree = parser.parse(
    """
    // Define the module
    module test1(input wire a, b);
        reg d;
        wire c, e, f;
        d = a;
    endmodule
    // Define another module
    module main(output reg x);
        a = b;
        // Instantiate the module
        test1 test1inst(.a(a1), .b(b1));
    endmodule
    """)
    print(tree.pretty())

    d = logicbox.ModuleDeclarationProcessor()
    for module in d.transform(tree).children:
        print("-----", module, "--------")
        t0 = logicbox.DeclarationProcessor()
        print("XXX", t0.transform(module.body))

def test_2():

    decls = {}
    states = {}

    x0 = logicbox.BinaryExpression("and", logicbox.Constant(logicbox.Value(True)), \
                                  logicbox.Constant(logicbox.Value(True)))
    assert x0.evaluate("root", decls, states).get_bool()

    x1 = logicbox.BinaryExpression("and", logicbox.Constant(logicbox.Value(True)), \
                                  logicbox.Constant(logicbox.Value(False)))
    assert not x1.evaluate("root", decls, states).get_bool()

    states["root.a"] = logicbox.Value(True)
    
    x2 = logicbox.BinaryExpression("and", logicbox.Constant(logicbox.Value(True)), \
                                  logicbox.Variable("a"))
    assert x2.evaluate("root", decls, states).get_bool()

    # Put the last expression into the declaration map
    decls["root.b"] = x2

    x3 = logicbox.UnaryExpression("not", logicbox.Variable("b"))
    assert not x3.evaluate("root", decls, states).get_bool()

def test_3():

    parser = lark.Lark.open("./logic.lark")
    tree = parser.parse(
    """
    // Define the module
    module or(input wire a, input wire b, output wire c);
        c = a | b;
        reg e;
        e <= (10 > 5);
    endmodule
    // Define the module
    module test(input wire a1, input wire b1, output wire c1, output reg d1);
        wire t;
        or m0(.a(a1), .b(b1), .c(c1));
        or m1(.a(a1), .b(b1), .c(t));
        d1 <= t;
    endmodule
    // Define another module
    module main();
        wire a2;
        wire b2;
        wire c2;
        wire d2;
        a2 = 1;
        b2 = 0;
        test t0(.a1(a2), .b1(b2), .c1(c2), .d1(d2));
    endmodule
    """)
    print(tree.pretty())

    modules = {}
    assignment_0_map = {}
    assignment_1_map = {}
    register_list = []

    d = logicbox.ModuleDeclarationProcessor()
    for module in d.transform(tree).children:
        modules[module.name] = module

    logicbox.instantiate(modules, assignment_0_map, assignment_1_map, register_list)

    print("M0", assignment_0_map)
    print("M1", assignment_1_map)
    print("RL", register_list)

    # Cycle through and evaluate
    value_state = {}

    # Initialize the registers to False
    for reg in register_list:
        value_state[reg] = logicbox.Value(False)

    for name, exp in assignment_0_map.items():
        value = exp.evaluate(assignment_0_map, value_state)
        if not name in value_state:
            value_state[name] = value

    # Check values
    assert value_state["t0.m0.a"].get_bool()
    assert not value_state["t0.m0.b"].get_bool()
    assert value_state["c2"].get_bool()


test_3()
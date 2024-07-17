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

    x0 = logicbox.BinaryExpresion("and", logicbox.Constant(logicbox.Value(True)), \
                                  logicbox.Constant(logicbox.Value(True)))
    assert x0.evaluate("root", decls, states).get_bool()

    x1 = logicbox.BinaryExpresion("and", logicbox.Constant(logicbox.Value(True)), \
                                  logicbox.Constant(logicbox.Value(False)))
    assert not x1.evaluate("root", decls, states).get_bool()

    states["root.a"] = logicbox.Value(True)
    
    x2 = logicbox.BinaryExpresion("and", logicbox.Constant(logicbox.Value(True)), \
                                  logicbox.Variable("a"))
    assert x2.evaluate("root", decls, states).get_bool()

    # Put the last expression into the declaration map
    decls["root.b"] = x2

    x3 = logicbox.UnaryExpresion("not", logicbox.Variable("b"))
    assert not x3.evaluate("root", decls, states).get_bool()






test_2()
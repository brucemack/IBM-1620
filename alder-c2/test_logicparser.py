import lark
import logicbox

# Parse some contructs 
def test_1():

    parser = lark.Lark.open("./logic.lark")
    tree = parser.parse(
    """
    // Define the module
    module test1(a, b);
        input a;
        reg b;
        output b;
        output reg e, f;
        b = a;
        b = a;
        b = a;
        b = a;
    endmodule
    // Define another module
    module main(x);
        a = b;
        // Instantiate the module
        test1 test1inst(.a(a1), .b(b1));
    endmodule
    """)
    print(tree.pretty())

    modules = {}
    d = logicbox.ModuleDeclarationProcessor(modules)
    d.transform(tree)
    print(modules)

test_1()
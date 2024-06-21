#include <iostream>
#include <map>
#include <string>
#include <span>
#include <vector>
#include <cassert>

#include "yaml-cpp/yaml.h"

#include "LogicDiagram.h"
#include "Pin.h"
#include "PlugLocation.h"
#include "PinLocation.h"
#include "Components.h"
#include "VerilogWire.h"
#include "CardMeta.h"
#include "Machine.h"

using namespace std;

int test_1() {
    {
        map<string, PinMeta> pins_aaaa = { 
            { string("A"), PinMeta(string("A"), PinType:: OUTPUT) },
            { string("B"), PinMeta(string("B"), PinType:: OUTPUT) }
        };
        CardMeta cardMeta1("AAAA", "Card AAAA", pins_aaaa);
        PlugLocation loc1("01AA","0000");
        PlugLocation loc2("01AA","0002");
        Card card1(cardMeta1, loc1);
        Pin& pina = card1.getPin("A");
        Pin& pinb = card1.getPin("B");
        vector<reference_wrapper<Pin>> pins;
        pins.push_back(pina);
        
        // Connect
        pina.connect(pinb);
        pinb.connect(pina);

        assert(std::hash<Pin>{}(pina) == std::hash<Pin>{}(pina));
        assert(std::hash<Pin>{}(pina) != std::hash<Pin>{}(pinb));

        reference_wrapper<Pin> a1 = pina;
        reference_wrapper<Pin> a2 = pina;
        // See that the underlying objects are equal
        assert(std::addressof(a1.get()) == std::addressof(a2.get()));
        // BE CAREFUL! The wrappers are not equal
        assert(std::addressof(a1) != std::addressof(a2));

        // Search semantics - found
        {
            auto it = std::find_if(pins.begin(), pins.end(), 
                [&pina](const std::reference_wrapper<Pin>& x) { 
                    return std::addressof(pina) == std::addressof(x.get()); 
                });
            assert(it != pins.end());
        }
        {
            auto it = std::find_if(pins.begin(), pins.end(), 
                [&pinb](const std::reference_wrapper<Pin>& x) { 
                    return std::addressof(pinb) == std::addressof(x.get()); 
                });
            assert(it == pins.end());
        }

        // Visitation test
        {
            int a = 0;
            pina.visitImmediateConnections([&a](const Pin& p) {
                cout << "Visiting " << p.getLocation().toString() << endl;
            });
        }

        {
            auto a = LogicDiagram::parsePinRefs("0000.CL");
            assert(a[0].coo == "0000");;
            assert(a[0].pinId == "C");;
            assert(a[1].coo == "0000");;
            assert(a[1].pinId == "L");;
        }

        // Pin location
        {
            PinLocation pinLocA1(loc1, "A");
            PinLocation pinLocA2(loc2, "A");
            PinLocation pinLocB(loc1, "A");
            assert(!(pinLocA1 == pinLocA2));
            assert(pinLocA1 == pinLocB);
        }
    }

    return 0;
}

// Testing the VerilogWire system

int test_2() {
    
    Machine machine;

    // Make some metadata for a few cards
    static map<string, PinMeta> pins_aaaa = { 
        { string("O"), PinMeta(string("O"), PinType:: OUTPUT) },
        { string("O2"), PinMeta(string("O2"), PinType:: OUTPUT) },
    };
    CardMeta cardMeta_aaaa("AAAA", "Card AAAA", pins_aaaa);

    static map<string, PinMeta> pins_bbbb = { 
        { string("I"), PinMeta(string("I"), PinType:: INPUT) }
    };
    CardMeta cardMeta_bbbb("BBBB", "Card BBBB", pins_bbbb);

    // Populate some cards
    machine.createCard(cardMeta_aaaa, PlugLocation("0000", "0000"));
    machine.createCard(cardMeta_aaaa, PlugLocation("0000", "0001"));
    machine.createCard(cardMeta_bbbb, PlugLocation("0000", "0002"));
    machine.createCard(cardMeta_bbbb, PlugLocation("0000", "0003"));

    // Wire up
    Card& c0 = machine.getCard(PlugLocation("0000", "0000"));
    Card& c1 = machine.getCard(PlugLocation("0000", "0001"));
    Card& c2 = machine.getCard(PlugLocation("0000", "0002"));
    Card& c3 = machine.getCard(PlugLocation("0000", "0003"));

    // Here we create a situation where two cards drive the same pin
    c0.getPin("O").connect(c2.getPin("I"));
    c2.getPin("I").connect(c0.getPin("O"));
    c1.getPin("O").connect(c2.getPin("I"));
    c2.getPin("I").connect(c1.getPin("O"));
    // Regular 1->1 hookup
    c0.getPin("O2").connect(c3.getPin("I"));
    c3.getPin("I").connect(c0.getPin("O2"));

    // Make the Verilog wires
    vector<VerilogWire> wires = Machine::generateVerilogWires(machine);
    assert(wires.size() == 2);
    assert(!wires.at(0).empty());
    assert(!wires.at(1).empty());

    cout << "// Wires" << endl;
    for (VerilogWire wire : wires) {
        wire.synthesizeVerilog(cout);
    }

    // Check the connections
    // Grab the single-driven wire.  Both of the pins that are connected to this
    // wire should be connecting to the same Verilog wire (output of driving device)
    {
        PinLocation pl0 = PinLocation(PlugLocation("0000", "0000"), "O2");
        auto it0 = std::find_if(wires.begin(), wires.end(), [&pl0](const VerilogWire& w) -> bool {
            return w.isConnectedToPin(pl0);
        });
        assert(it0 != wires.end());
        assert(!it0->isMultiDriver());
        // Test the driver pin
        assert(it0->getVerilogPortBinding(c0.getPin("O2").getLocation()) == "W_0000_0000_O2");
        assert(it0->getVerilogPortBinding(c3.getPin("I").getLocation()) == "W_0000_0000_O2");
    }
    // Grab the multi-driven wire. 
    // Make sure that the driving pins have their own unique wire names and the driven pins
    // are all connected back to the synthesized DOT-OR.
    {
        PinLocation pl0 = PinLocation(PlugLocation("0000", "0000"), "O");
        auto it0 = std::find_if(wires.begin(), wires.end(), [&pl0](const VerilogWire& w) -> bool {
            return w.isConnectedToPin(pl0);
        });
        assert(it0 != wires.end());
        assert(it0->isMultiDriver());
        // Test the driver pins
        assert(it0->getVerilogPortBinding(c0.getPin("O").getLocation()) == "W_0000_0000_O");
        assert(it0->getVerilogPortBinding(c1.getPin("O").getLocation()) == "W_0000_0001_O");
        // Test the driven pins
        assert(it0->getVerilogPortBinding(c2.getPin("I").getLocation()) == "W_DOT_2");
        assert(it0->getVerilogPortBinding(c3.getPin("I").getLocation()) == "W_DOT_2");
        assert(it0->getConnectedPins().size() == 3);
    }

    // Dump the entire machine
    {
        cout << "// Synthesis of Entire Machine" << endl;
        Machine::generateVerilog(machine, cout);
    }

    return 0;
}

int main(int, const char**) {
    test_1();
    test_2();
}

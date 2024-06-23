/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include <functional>
#include <unordered_map>

#include "Card.h"
#include "VerilogWire.h"
#include "Util.h"
#include "Machine.h"

using namespace std;

Card& Machine::getCard(const PlugLocation& loc) {
    if (_cards.find(loc) == _cards.end()) 
        throw string("No card defined at location " + loc.toString());
    return _cards.at(loc);
}

const Card& Machine::getCardConst(const PlugLocation& loc) const {
    if (_cards.find(loc) == _cards.end()) 
        throw string("No card defined at location " + loc.toString());
    return _cards.at(loc);
}

Card& Machine::getOrCreateCard(const CardMeta& meta, const PlugLocation loc)  {
    // If the slot is open then create a card and plug it in
    if (_cards.find(loc) == _cards.end()) 
        _cards.emplace(loc, Card(meta, loc));
    // Makes sure the card is compatible
    Card& card = _cards.at(loc);
    if (card.getMeta().getType() != meta.getType())
        throw string("Different card already plugged in at " + loc.toString());
    return card;
}

Pin& Machine::getPin(const PinLocation& loc) {
    Card& card = getCard(loc.getPlugLocation());
    return card.getPin(loc.getPinId());
}

const Pin& Machine::getPinConst(const PinLocation& loc) const {
    const Card& card = getCardConst(loc.getPlugLocation());
    return card.getPinConst(loc.getPinId());
}

void Machine::dumpOn(std::ostream& str) const {
    str << "Cards:" << endl;
    visitAllCards([&str](const Card& card) {
        cout << "====================" << endl;
        cout << card.getLocation().toString() << " : " << card.getMeta().getType() << endl;
        cout << card.getMeta().getPinNames().size() << endl;
        card.dumpOn(str);
    });
}

void Machine::visitAllCards(const std::function<void (const Card&)> f) const {
    std::for_each(_cards.begin(), _cards.end(),
        [&f](std::pair<const PlugLocation&, const Card&> p) { f(p.second); }
    );
}

vector<VerilogWire> Machine::generateVerilogWires(const Machine& machine) {

    vector<VerilogWire> result;
    // Used to avoid double-visiting a pin that has already been traversed.
    unordered_set<PinLocation> pinsSeen;

    machine.visitAllCards([&pinsSeen, &result, &machine](const Card& card) {
        card.visitAllPins([&pinsSeen, &result, &card, &machine](const string& pinId, const Pin& workingPin) {
            // Ignore duplicate visits
            if (pinsSeen.find(workingPin.getLocation()) == pinsSeen.end()) {
                // Here is where we accumulate the connections to the Wire
                VerilogWire potentialWire(machine);
                // Visit all pins that are electrically connect tied this pin
                workingPin.visitAllConnections([&pinsSeen, &potentialWire](const Pin& connectedPin) {                    
                    // Connect 
                    potentialWire.addConnection(connectedPin);
                    // Make sure not to hit this again.
                    pinsSeen.insert(connectedPin.getLocation());                    
                });
                if (!potentialWire.empty()) 
                    result.push_back(potentialWire);
            }
        });
    });

    return result;
}

void Machine::generateVerilog(const Machine& machine, ostream& str) {

    str << "// IBM 1620 Logic Reproduction Project" << endl;
    str << "// Copyright (c) 2024 - Bruce MacKinnon" << endl;
    str << "// MACHINE-GENERATED VERILOG" << endl;
    str << endl;
    str << "`timescale 1ns/1ns" << endl;
    str << "module ibm1620_core;" << endl;

    // Generate all Verilog wires
    vector<VerilogWire> wires = Machine::generateVerilogWires(machine);
    // Dump the wires
    for (const VerilogWire& wire : wires)
        wire.synthesizeVerilog(str);
    
    // Make a map from pin location to wire to accelerate the cross-connect process
    unordered_map<PinLocation, reference_wrapper<const VerilogWire>> pinToWire;
    for (const VerilogWire& wire : wires) {
        for (PinLocation pl : wire.getConnectedPins()) {
            if (pinToWire.count(pl) > 0) 
                throw string("More than one wire is connected to " + pl.toString());
            pinToWire.insert_or_assign(pl, wire);
        }
    }

    // Dump the cards
    machine.visitAllCards([&pinToWire, &str](const Card& card) mutable {

        string moduleId = "X_" + card.getLocation().toString();

        str << "    // Card " << card.getMeta().getType() + " at location " + card.getLocation().toString() 
            + " - " + card.getMeta().getDesc() << endl;
        // Display page numbers
        str << "    // (ALD Pages: ";
        for (string p : card.getPageReferences())
            str << p << " ";
        str << ")" << endl;

        str << "    SMS_CARD_";
        str << card.getMeta().getType();
        str << " ";
        str << moduleId;
        str << "(";

        // Pin binding
        bool first = true;
        for (string pinName : card.getMeta().getSignalPinNames()) {
            const Pin& pin = card.getPinConst(pinName);
            if (pin.isConnected()) {
                if (!first) 
                    str << ", ";
                str << "." << toLower(pinName) << "(";
                // Figure out which wire the pin is connected to
                if (pinToWire.find(pin.getLocation()) == pinToWire.end()) {
                    throw string("Unable to resolve connection for pin " + pin.getLocation().toString());
                }
                else {
                    str << pinToWire.at(pin.getLocation()).get().getVerilogPortBinding(pin.getLocation());
                }
                str << ")";
                first = false;
            } 
        }

        str << ");" << endl;
    });

    str << endl;
    str << "    initial begin" << endl;
    str << "        $dumpfile(\"wave.vcd\");" << endl;
    str << "        $dumpvars(0, ibm1620_core);" << endl;
    str << "        #100000 $stop;" << endl;
    str << "    end" << endl;
    str << endl;
    str << "endmodule;" << endl;
}


#include "Components.h"
#include "VerilogWire.h"

using namespace std;

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
                // Visit all pins that are electrically connect toed this pin
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

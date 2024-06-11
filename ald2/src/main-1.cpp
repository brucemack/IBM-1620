#include <iostream>
#include <map>
#include <string>
#include <span>
#include <unordered_set>
#include <vector>

#include "yaml-cpp/yaml.h"

#include "LogicDiagram.h"
#include "Components.h"

using namespace std;

static bool isPinRef(const string& ref) {
    if (ref.find('.') != std::string::npos) {
        return true;
    } else {
        return false;
    }
}

vector<LogicDiagram::Page> loadAldPages(const vector<string> fns) {
    auto result = vector<LogicDiagram::Page>();
    for (auto fn : fns) {
        YAML::Node c = YAML::LoadFile(fn);
        LogicDiagram::Page page = c.as<LogicDiagram::Page>();
        result.push_back(page);
    }
    return result;
}

void processAlds(const vector<LogicDiagram::Page>& pages, 
    const map<string, CardMeta>& cardMeta, 
    Machine& machine, 
    map<string, Pin&>& namedSignals) {

    // PASS #1
    // - Register all cards
    // - Record aliases for all output pins 
    // - Record aliases for all named nets that are page outputs
    for (const LogicDiagram::Page& page : pages) {
        for (const LogicDiagram::Block& block : page.blocks) {
            // Register all of the cards mentioned on the pages
            if (cardMeta.find(block.typ) == cardMeta.end())
                throw string("Invalid card type on page/block " + 
                    page.num + "/" + block.coo + " : " + block.typ);
            Card& card = machine.getOrCreateCard(cardMeta.at(block.typ), block.loc);
            // Register signal names for outputs
            for (auto [outputPinId, driverRefList] : block.out) {
                // Resolve the Pin
                Pin& pin = card.getPin(outputPinId);
                // Look through everything that the pin is connected to
                for (auto driverRef : driverRefList) {
                    // Only pay attention to outputs that use signal names
                    if (!isPinRef(driverRef)) {
                        // Check for conflict
                        if (namedSignals.find(driverRef) != namedSignals.end()) {
                            if (!(namedSignals.at(driverRef) == pin)) {
                                throw string("Conflicting signal name on page " + 
                                    page.num + " :  " + driverRef);
                            }
                        } 
                        // Register named signal
                        else {
                            namedSignals.emplace(driverRef, pin);
                        }
                    }
                }
            }
        }
        // Register all of the cross-page net aliases
        for (const LogicDiagram::Output& output : page.outputs) {
            for (auto driverRef : output.inp) {                
                if (isPinRef(driverRef)) {
                    // REMEMBER: It's possible to mention multiple pins in one reference.
                    for (LogicDiagram::BlockCooPin bp : LogicDiagram::parsePinRefs(driverRef)) {
                        // Resolve the local block on this page
                        const LogicDiagram::Block& block = page.getBlockByCoordinate(bp.coo);
                        // Determine the card/pin
                        Card& card = machine.getCard(block.loc);
                        Pin& pin = card.getPin(bp.pinId);
                        // Check for conflict
                        if (namedSignals.find(output.net) != namedSignals.end()) {
                            if (!(namedSignals.at(output.net) == pin)) {
                                throw string("Conflicting signal name on page " + 
                                    page.num + " :  " + output.net);
                            }
                        } 
                        // Register named signal
                        else {
                            namedSignals.emplace(output.net, pin);
                        }
                    }
                }
            }
        }
    }

    // PASS #2
    // - Get the inputs connected
    for (const LogicDiagram::Page& page : pages) {
        for (const LogicDiagram::Block& block : page.blocks) {
            try {
                Card& card = machine.getCard(block.loc);
                // Get the inputs connected
                for (auto [inputPinId, driverRefList] : block.inp) {            
                    Pin& inputPin = card.getPin(inputPinId);
                    for (auto driverRef : driverRefList) {
                        
                        // Trace back to what is driving this input.  There are two 
                        // cases:
                        // 1. A block.pin(s) reference on the same page.
                        // 2. A global signal name
                        
                        if (isPinRef(driverRef)) {
                            // It is possible to reference multiple pins in one reference!
                            for (LogicDiagram::BlockCooPin driverBlockPin : LogicDiagram::parsePinRefs(driverRef)) {
                                // Map the blockId to the block
                                const LogicDiagram::Block& driverBlock = 
                                    page.getBlockByCoordinate(driverBlockPin.coo);
                                // Map the block to the card
                                Card& driverCard = machine.getCard(driverBlock.loc);
                                // Get the pin
                                Pin& driverPin = driverCard.getPin(driverBlockPin.pinId);
                                // Make the connection back to the driver
                                inputPin.connect(driverPin);
                                driverPin.connect(inputPin);
                            }
                        }
                        else {
                            // Find what block/pin the signal name points to
                            if (namedSignals.find(driverRef) == namedSignals.end()) 
                                throw string("Input reference to unknown signal: " + driverRef);
                            // Get the pin
                            Pin& driverPin = namedSignals.at(driverRef);
                            // Make the connection back to the driver
                            inputPin.connect(driverPin);
                            driverPin.connect(inputPin);
                        }
                    }
                }
            } catch (const std::string& ex) {
                throw string("Error in page/block " + page.num + "/" + block.coo + " : " + ex);
            }
        }
    }
}

int main(int, const char**) {

    // Load the card metadata
    map<string, CardMeta> cardMeta;   
    cardMeta["MX"] = CardMeta("MX");
    cardMeta["CAB"] = CardMeta("CAB");
    cardMeta["MH"] = CardMeta("MH");
    cardMeta["CEYB"] = CardMeta("CEYB");
    cardMeta["SW"] = CardMeta("SW");

    // Read ALD and popular machine
    Machine machine;

    // Named signals
    map<string, Pin&> namedSignals;

    vector<string> fns;
    fns.push_back("../tests/01.06.01.1.yaml");
    fns.push_back("../tests/controls.yaml");
    vector<LogicDiagram::Page> pages = loadAldPages(fns);

    try {
        processAlds(pages, cardMeta, machine, namedSignals);
        machine.dumpOn(cout);
    }
    catch (const string& ex) {
        cout << ex << endl;
    }

    cout << "Named Signals:" << endl;
    for (auto [key, value] : namedSignals)
        cout << key << " : " << value.getDesc() << endl;

    // Generate wires
    vector<Wire> wires = machine.generateWires();
    /*
    // Setup the mapping between pins and wires
    map<string, string> pinToWire;
    for (const Wire& w : wires) {
        string wireName = w.pins.at(0);
        for (const string& pin : w.pins) {
            pinToWire(pin, wireName);
        }
    }
    
    // Create a spice block for each 




    std::for_each(begin(wires), end(wires), [](const Wire& wire) {
        for (const string& p : wire.pins) {
            cout << p << " ";
        }
        cout << endl;
    });
    */
}

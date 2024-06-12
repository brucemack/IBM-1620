#include <iostream>
#include <map>
#include <string>
#include <span>
#include <unordered_set>
#include <vector>
#include <memory>

#include "yaml-cpp/yaml.h"

#include "LogicDiagram.h"

#include "Components.h"
#include "cards/CardONE.h"
#include "cards/CardZERO.h"
#include "cards/CardHIZ.h"

using namespace std;

static bool isPinRef(const string& ref) {
    if (ref.find('.') != std::string::npos) {
        return true;
    } else {
        return false;
    }
}

unique_ptr<CardMeta> loadCardMeta(const string& baseDir, const string& code) {
    YAML::Node c = YAML::LoadFile(baseDir + "/sms-cards/" + code + "/" + code + ".yaml");
    unique_ptr<CardMeta> m = make_unique<CardMeta>(code, c["description"].as<string>());
    return m;
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
    const map<string, unique_ptr<CardMeta>>& cardMeta, 
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
            
            Card& card = machine.getOrCreateCard(*(cardMeta.at(block.typ).get()), block.loc);
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

    string baseDir = "/home/bruce/IBM1620/hardware";

    // Load the card metadata
    map<string, unique_ptr<CardMeta>> cardMeta;   

    // Special purpose cards
    cardMeta["ONE"] = make_unique<CardONEMeta>();
    cardMeta["ZERO"] = make_unique<CardZEROMeta>();
    cardMeta["HIZ"] = make_unique<CardHIZMeta>();
    {
        YAML::Node c = YAML::LoadFile(baseDir + "/sms-cards/cards.yaml");
        for (auto it = begin(c["cards"]); it != end(c["cards"]); it++) {
            string id = it->as<string>();
            cardMeta[id] = loadCardMeta(baseDir, id);
        }
    }

    // Read ALD and popular machine
    Machine machine;

    // Named signals
    map<string, Pin&> namedSignals;

    vector<string> fns;
    //fns.push_back("../tests/01.06.01.1.yaml");
    //fns.push_back("../tests/controls.yaml");
    fns.push_back("../../model_1f_aetna_ald/pages/01.10.05.1.yaml");
    fns.push_back("../../model_1f_aetna_ald/pages/controls.yaml");
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
    
    // Setup the mapping between pins and wires
    cout << "Wires" << endl;
    map<string, string> pinToWire;
    for (const Wire& w : wires) {
        string wireName = w.pins.at(0);
        for (const string& pin : w.pins) {
            pinToWire[pin] = wireName;
            cout << pin << " -> " << wireName << endl;
        }
    }
    
    // SPICE GENERATION
    // Create a spice line for each card
    int lineCounter = 1;
    machine.visitAllCards([&lineCounter, &pinToWire](const Card& card) mutable {
        string line = "X_" + card.getLocation().toString();
        //line = line + std::to_string(lineCounter);
        // Pins
        for (string pinName : card.getMeta().getPinNames()) {
            if (card.isPinUsed(pinName)) {
                const Pin& pin = card.getPinConst(pinName);
                // Figure out which wire 
                if (pinToWire.find(pin.getDesc()) == pinToWire.end()) {
                    //throw string("Pin " + pin.getDesc() + " not wired")
                    line = line + " ";
                    line = line + "?";
                }
                else {
                    line = line + " W.";
                    line = line + pinToWire[pin.getDesc()];
                }
            } 
            else if (!card.getMeta().getDefaultNode(pinName).empty()) {
                line = line + " ";
                line = line + card.getMeta().getDefaultNode(pinName);
            }
            else 
            {
                // Tie to unused
                line = line + " W.";
                line = line + card.getLocation().toString() + "." + pinName;
            }
        }

        line = line + " SMS_CARD_" + card.getMeta().getType();

        cout << "* Card " << card.getMeta().getType() + " at location " + card.getLocation().toString() 
            + " - " + card.getMeta().getDesc() << endl;
        cout << line << endl;
        lineCounter++;
    });


    /*
    std::for_each(begin(wires), end(wires), [](const Wire& wire) {
        for (const string& p : wire.pins) {
            cout << p << " ";
        }
        cout << endl;
    });
    */
}

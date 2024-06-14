#include <iostream>
#include <fstream>
#include <map>
#include <string>
#include <span>
#include <unordered_set>
#include <vector>
#include <memory>
#include <algorithm>

#include "yaml-cpp/yaml.h"

#include "LogicDiagram.h"
#include "Components.h"
#include "cards/CardONE.h"
#include "cards/CardZERO.h"
#include "cards/CardHIZ.h"
#include "cards/CardIND.h"
#include "cards/CardRST.h"

using namespace std;

static bool isPinRef(const string& ref) {
    if (ref.find('.') != std::string::npos) {
        return true;
    } else {
        return false;
    }
}

string toLower(const string& r) {
    string data = r;
    std::transform(data.begin(), data.end(), data.begin(),
        [](char c){ return std::tolower(c); });
    return data;
}

string dotToUnder(const string& r) {
    string data = r;
    std::transform(data.begin(), data.end(), data.begin(),
        [](char c){ if (c == '.') return '_'; else return c; });
    return data;
}

string safeVerilogIdentifier(const string& r) {
    return "W" + dotToUnder(r);
}

unique_ptr<CardMeta> loadCardMeta(const string& baseDir, const string& code) {
    
    YAML::Node c = YAML::LoadFile(baseDir + "/sms-cards/" + code + "/" + code + ".yaml");

    std::map<std::string, PinMeta> pinMeta;
    YAML::Node pins = c["pins"];
    if (!pins.IsMap()) 
        throw string("Format error in card meta file : " + code);
    for (auto it = begin(pins); it != end(pins); it++) {
        string pinId = it->first.as<std::string>();
        YAML::Node pin = it->second;
        if (!pin.IsMap()) 
            throw string("Format error in card meta file : " + code);
        string type = pin["type"].as<std::string>();
        // Ignore not connected pins
        if (type == "NC")
            continue;
        PinMeta pm { pinId, str2PinType(type) };
        pinMeta[pinId] = pm;
    }
    return make_unique<CardMeta>(code, c["description"].as<string>(), pinMeta);
}

vector<LogicDiagram::Page> loadAldPages(const vector<string> fns) {
    auto result = vector<LogicDiagram::Page>();
    for (auto fn : fns) {
        cout << "Working on " << fn << endl;
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
            
            Card& card = machine.getOrCreateCard(*(cardMeta.at(block.typ).get()), { block.gate, block.loc });

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
        for (const LogicDiagram::Alias& alias : page.aliases) {
            for (auto driverRef : alias.inp) {                
                if (isPinRef(driverRef)) {
                    // REMEMBER: It's possible to mention multiple pins in one reference.
                    for (LogicDiagram::BlockCooPin bp : LogicDiagram::parsePinRefs(driverRef)) {
                        // Resolve the local block on this page
                        const LogicDiagram::Block& block = page.getBlockByCoordinate(bp.coo);
                        // Determine the card/pin
                        Card& card = machine.getCard({ block.gate, block.loc});
                        Pin& pin = card.getPin(bp.pinId);
                        // Register the alias
                        namedSignals.emplace(alias.name, pin);
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
                Card& card = machine.getCard({ block.gate, block.loc });
                // Get the inputs connected
                for (auto [inputPinId, driverRefList] : block.inp) {            
                    Pin& inputPin = card.getPin(inputPinId);
                    for (auto driverRef : driverRefList) {
                        
                        // Trace back to what is driving this input.  There are two 
                        // cases:
                        // 1. A block.pin(s) reference on the same page.
                        // 2. A global signal alias
                        if (isPinRef(driverRef)) {
                            // It is possible to reference multiple pins in one reference!
                            for (LogicDiagram::BlockCooPin driverBlockPin : LogicDiagram::parsePinRefs(driverRef)) {
                                // Map the blockId to the block
                                const LogicDiagram::Block& driverBlock = 
                                    page.getBlockByCoordinate(driverBlockPin.coo);
                                // Map the block to the card
                                Card& driverCard = machine.getCard({ driverBlock.gate, driverBlock.loc });
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
                            //cout << "Connecting " << driverRef << endl;
                            //cout << "  "  << driverPin.getDesc() << endl;
                            //cout << "  "  << inputPin.getDesc() << endl;
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

static void generateSpice(const Machine& machine, const map<string, string>& pinToWire) {

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
                    line = line + " W_";
                    line = line + pinToWire.at(pin.getDesc());
                }
            } 
            else if (!card.getMeta().getDefaultNode(pinName).empty()) {
                line = line + " ";
                line = line + card.getMeta().getDefaultNode(pinName);
            }
            else 
            {
                // Tie to unused
                line = line + " W_";
                line = line + card.getLocation().toString() + "_" + pinName;
            }
        }

        line = line + " SMS_CARD_" + card.getMeta().getType();

        cout << "* Card " << card.getMeta().getType() + " at location " + card.getLocation().toString() 
            + " - " + card.getMeta().getDesc() << endl;
        cout << line << endl;
        lineCounter++;
    });
}

static void generateVerilog(const Machine& machine, const map<string, string>& pinToWire,
    const vector<string>& wireNames, ostream& str) {

    str << "// IBM 1620 Logic Reproduction Project" << endl;
    str << "// Copyright (c) 2024 - Bruce MacKinnon" << endl;
    str << "// MACHINE-GENERATED VERILOG" << endl;
    str << endl;
    str << "`timescale 1ns/1ns" << endl;
    str << "module ibm1620_core;" << endl;

    // Dump the wire names
    for (string w : wireNames) {
        str << "    wire " << safeVerilogIdentifier(w) << ";" << endl;
    }

    // Dump the cards
    machine.visitAllCards([&pinToWire, &str](const Card& card) mutable {

        string moduleId = "X_" + card.getLocation().toString();

        str << "    // Card " << card.getMeta().getType() + " at location " + card.getLocation().toString() 
            + " - " + card.getMeta().getDesc() << endl;

        str << "    SMS_CARD_";
        str << card.getMeta().getType();
        str << " ";
        str << moduleId;
        str << "(";

        // Pins
        bool first = true;
        for (string pinName : card.getMeta().getSignalPinNames()) {
            if (card.isPinUsed(pinName)) {
                if (!first) 
                    str << ", ";
                const Pin& pin = card.getPinConst(pinName);
                str << "." << toLower(pinName) << "(";
                // Figure out which wire the pin is connected to
                if (pinToWire.find(pin.getDesc()) == pinToWire.end()) {
                    // It's OK to have a port connected to nothing
                }
                else {
                    str << safeVerilogIdentifier(dotToUnder(pinToWire.at(pin.getDesc())));
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

int main(int, const char**) {

    string baseDir = "/home/bruce/IBM1620/hardware";
    string outDir = baseDir + "/sms-cards/tests";
    string aldBaseDir = "../../model_1f_aetna_ald/pages";

    // Load the card metadata
    map<string, unique_ptr<CardMeta>> cardMeta;   

    // Special purpose cards
    cardMeta["ONE"] = make_unique<CardONEMeta>();
    cardMeta["ZERO"] = make_unique<CardZEROMeta>();
    cardMeta["HIZ"] = make_unique<CardHIZMeta>();
    cardMeta["IND"] = make_unique<CardINDMeta>();
    cardMeta["RST"] = make_unique<CardRSTMeta>();

    // Load defined cards
    try {
        YAML::Node c = YAML::LoadFile(baseDir + "/sms-cards/cards.yaml");
        for (auto it = begin(c["cards"]); it != end(c["cards"]); it++) {
            string id = it->as<string>();
            cardMeta[id] = loadCardMeta(baseDir, id);
        }
    }
    catch (const string& ex) {
        cout << "Failed to load SMS metadata : " + ex << endl;
        return -1;
    }

    // Read ALD and popular machine
    Machine machine;

    // Named signals
    map<string, Pin&> namedSignals;

    // Build the list of filenames
    vector<string> fns;
    {
        YAML::Node c = YAML::LoadFile(aldBaseDir + "/core-pages.yaml");
        for (auto it = begin(c["pages"]); it != end(c["pages"]); it++) {
            string id = it->as<string>();
            fns.push_back(aldBaseDir + "/" + id + ".yaml");
        }
    }
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
    
    // TODO: MOVE THIS INTO THE SPICE/VERILOG GENERATION BECAUSE
    // THE PROCESS WILL DIFFER (EX: DOT ORs)

    // Setup the mapping between pins and wires
    map<string, string> pinToWire;
    vector<string> wireNames;
    for (const Wire& w : wires) {
        string wireName = w.pins.at(0);
        wireNames.push_back(wireName);
        for (const string& pin : w.pins) {
            pinToWire[pin] = wireName;
        }
    }

    //generateSpice(machine, pinToWire);

    try {
        ofstream verilogFile(outDir + "/core.v",  std::ios::trunc);
        generateVerilog(machine, pinToWire, wireNames, verilogFile);
    } catch (const string& ex) {
        cout << "Failed to generate Verilog: " << ex << endl;
    }
}

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
#include "Card.h"
#include "Machine.h"
#include "Util.h"

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
        // Default drive type
        string driveType = "AH_PD";
        if (pin["drivetype"])
            driveType = pin["drivetype"].as<std::string>();
        // Default tie
        string tieType = "NONE";
        if (type == "PASSIVE" && pin["tie"])
            tieType = pin["tie"].as<std::string>();
        pinMeta.insert_or_assign(pinId, PinMeta(pinId, 
            str2PinType(type), str2DriveType(driveType), str2TieType(tieType)));

    }
    return make_unique<CardMeta>(code, c["description"].as<string>(), pinMeta);
}

vector<LogicDiagram::Page> loadAldPages(const vector<string> fns) {
    auto result = vector<LogicDiagram::Page>();
    for (auto fn : fns) {
        cout << "Loading page " << fn << endl;
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
            
            Card& card = machine.getOrCreateCard(*(cardMeta.at(block.typ).get()), 
                { block.gate, block.loc });
            // Keep track of which pages we see the card defined
            card.addPageReference(page.num);

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

    cout << "Linking" << endl;

    // PASS #2
    // Go through each block and look at each input pin. Establish the linkage 
    // for each input.
    for (const LogicDiagram::Page& page : pages) {
        for (const LogicDiagram::Block& block : page.blocks) {
            try {
                Card& card = machine.getCard({ block.gate, block.loc });
                cout << "Working on card " << card.getLocation().toString() << endl;
                // Get the inputs connected
                for (auto [inputPinId, driverRefList] : block.inp) {  
                    cout << "  Working on pin "<< inputPinId << endl;          
                    Pin& inputPin = card.getPin(inputPinId);
                    for (auto driverRef : driverRefList) {
                        cout << "     Working on driver " << driverRef << endl; 
                        
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

static void generateSpice(const Machine& machine, const unordered_map<PinLocation, string>& pinToWire) {

    // Create a spice line for each card
    int lineCounter = 1;
    machine.visitAllCards([&lineCounter, &pinToWire](const Card& card) mutable {
        string line = "X_" + card.getLocation().toString();
        //line = line + std::to_string(lineCounter);
        // Pins
        for (string pinName : card.getMeta().getPinNames()) {
            const Pin& pin = card.getPinConst(pinName);
            if (pin.isConnected()) {
                // Figure out which wire 
                if (pinToWire.find(pin.getLocation()) == pinToWire.end()) {
                    //throw string("Pin " + pin.getDesc() + " not wired")
                    line = line + " ";
                    line = line + "?";
                }
                else {
                    line = line + " W_";
                    line = line + pinToWire.at(pin.getLocation());
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

int main(int, const char**) {

    string baseDir = "/home/bruce/IBM1620/hardware";
    string outDir = baseDir + "/sms-cards/tests";
    string aldBaseDir = "../../daves-1f/pages";
    string pagesFile = "core-pages.yaml";
    //string outDir = ".";
    //string aldBaseDir = "../tests";
    //string pagesFile = "dot-or-test-1-pages.yaml";

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
            try {
                cardMeta[id] = loadCardMeta(baseDir, id);
            } catch (const string& str) {
                throw string("Card " + id + " " + str);
            }
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
        YAML::Node c = YAML::LoadFile(aldBaseDir + "/" + pagesFile);
        for (auto it = begin(c["pages"]); it != end(c["pages"]); it++) {
            string id = it->as<string>();
            fns.push_back(aldBaseDir + "/" + id + ".yaml");
        }
    }

    cout << "Processing ALDs " << endl;

    try {
        vector<LogicDiagram::Page> pages = loadAldPages(fns);
        processAlds(pages, cardMeta, machine, namedSignals);
        machine.dumpOn(cout);
    }
    catch (const string& ex) {
        cout << ex << endl;
        return -1;
    }

    cout << "Named Signals:" << endl;
    for (auto [key, value] : namedSignals)
        cout << key << " : " << value.getLocation().toString() << endl;

    try {
        ofstream verilogFile(outDir + "/core.v",  std::ios::trunc);
        Machine::generateVerilog(machine, verilogFile);
    } catch (const string& ex) {
        cout << "Failed to generate Verilog: " << ex << endl;
        return -1;
    }
}

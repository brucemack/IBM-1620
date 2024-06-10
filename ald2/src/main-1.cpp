#include <iostream>
#include <map>
#include <string>

#include "yaml-cpp/yaml.h"

#include "LogicDiagram.h"
#include "Components.h"

using namespace std;

void loadAld(const string& fn, const map<string, CardMeta>& cardMeta, Machine& machine) {

    YAML::Node c = YAML::LoadFile(fn);
    LogicDiagram::Page page = c.as<LogicDiagram::Page>();

    // Register the nets
    for (const LogicDiagram::Output& out : page.outputs) {
        machine.getOrCreateWire(out.net);
    }

    // Register the blocks
    for (const LogicDiagram::Block& block : page.blocks) {
        if (cardMeta.find(block.typ) == cardMeta.end())
            throw string("Card type not found: " + block.typ);
        machine.getOrCreateCard(cardMeta.at(block.typ), block.loc);
    }
}

int main(int, const char**) {

    // Load the card metadata
    map<string, CardMeta> cardMeta;   
    cardMeta["MX"] = CardMeta();
    cardMeta["CAB"] = CardMeta();
    cardMeta["MH"] = CardMeta();
    cardMeta["CEYB"] = CardMeta();

    // Read ALD and popular machine
    Machine machine;

    //YAML::Node c = YAML::LoadFile("../tests/01.06.01.1.yaml");
    //LogicDiagram::Page page = c.as<LogicDiagram::Page>();
    //cout << page.part << endl;
    //cout << page.blocks.size() << endl;
    //cout << page.outputs.size() << endl;

    try {
        loadAld("../tests/01.06.01.1.yaml", cardMeta, machine);
        machine.dumpOn(cout);
    }
    catch (const string& ex) {
        cout << ex << endl;
    }
}

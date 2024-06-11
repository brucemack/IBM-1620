#include<vector>
#include "LogicDiagram.h"

using namespace std;

namespace LogicDiagram {

vector<string> PinNames { "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R" };

const Block& Page::getBlockByCoordinate(const string& coo) const {
    for (const LogicDiagram::Block& b : blocks) {
        if (b.coo == coo)
            return b;
    }
    throw string("Invalid block coordinate: " + coo);
}

bool validPinName(const string& pinName) {
    return std::find(begin(PinNames), end(PinNames), pinName) 
        != PinNames.end();
}

vector<BlockCooPin> parsePinRefs(const string& ref) {

    vector<BlockCooPin> result = vector<BlockCooPin>();
    std::size_t p = ref.find('.');

    if (p > 0 && p < ref.size() - 1) {
        string block = ref.substr(0, p);
        string pins = ref.substr(p + 1);
        for (unsigned int i = 0; i < pins.length(); i++) {
            string pin(pins.substr(i, 1));
            if (!LogicDiagram::validPinName(pin)) {
                throw string("Invalid pin name in reference : " + ref);
            }
            result.push_back(BlockCooPin { block, pin});
        }
    } else {
        throw string("Invalid block/pin reference: " + ref);
    }

    return result;
}

}



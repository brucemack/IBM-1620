/* IBM 1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include <iostream>
#include <algorithm>
#include <unordered_set>
#include <string>

#include "LogicDiagram.h"
#include "Card.h"
#include "CardMeta.h"

using namespace std;


Card::Card(const CardMeta& meta, const PlugLocation& loc)
:   _meta(meta),
    _loc(loc) {
    // Create all of the pins that are defined in the metadata
    _meta.visitAllPinMeta([&](const PinMeta& pm) {
        _pins.emplace(pm.getId(), Pin(pm, *this));
    });
}

Card::Card(const Card& other) 
:   _meta(other._meta),
    _loc(other._loc) {
    // Setup new pins that have the same metadata but are pointing to this card
    std::for_each(begin(other._pins), end(other._pins),
        [&](std::pair<const std::string, const Pin&> p) {
            _pins.emplace(p.first, Pin(p.second.getMeta(), *this));
        }
    );
}

Pin& Card::getPin(const string& id) {
    if (_pins.find(id) == _pins.end())
        throw string("Pin not defined: " + id + " on card " + _loc.toString());
    return _pins.at(id);
}

const Pin& Card::getPinConst(const string& id) const {
    if (_pins.find(id) == _pins.end())
        throw string("Pin not defined: " + id + " on card " + _loc.toString());
    return _pins.at(id);
}

void Card::dumpOn(std::ostream& str) const {
    str << "Card: " + _loc.toString() << endl;
    str << "Pins:" << endl;
    visitAllPins([&](const string& pinId, const Pin& pin) {
        PinType pt = _meta.getPinType(pinId);
        str << pinId << " " << (int)pt << " -> " << pin.getConnectionsDesc() << endl;
    });
    str << "Page References:" << endl;
    for (auto s : _pageRefs) 
        str << s << " ";
    str << endl;
}

void Card::visitAllPins(const std::function<void (const string& id, const Pin&)> f) const {
    std::for_each(_pins.begin(), _pins.end(),
        [&f](std::pair<const string&, const Pin&> p) { f(p.first, p.second); }
    );
}


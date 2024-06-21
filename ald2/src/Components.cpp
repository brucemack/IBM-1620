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
#include "Components.h"
#include "CardMeta.h"

using namespace std;

PinType str2PinType(const string& str) {
    if (str == "UNKNOWN") 
        return PinType::UNKNOWN;
    else if (str == "INPUT")
        return PinType::INPUT;
    else if (str == "OUTPUT")
        return PinType::OUTPUT;
    else if (str == "GND")
        return PinType::GND;
    else if (str == "VP12")
        return PinType::VP12;
    else if (str == "VN12")
        return PinType::VN12;
    else 
        throw string("Unrecognized pin type: " + str);
}

Card::Card(const CardMeta& meta, const PlugLocation& loc)
:   _meta(meta),
    _loc(loc) {
    _meta.visitAllPinMeta([&](const PinMeta& pm) {
        _pins.emplace(pm.id, Pin(pm, *this));
    });
}

Pin& Card::getPin(const string& id) {
    if (_pins.find(id) == _pins.end())
        throw string("Pin not defined: " + id);
    return _pins.at(id);
}

const Pin& Card::getPinConst(const string& id) const {
    if (_pins.find(id) == _pins.end())
        throw string("Pin not defined: " + id);
    return _pins.at(id);
}

void Card::dumpOn(std::ostream& str) const {
    str << "Pins:" << endl;
    visitAllPins([&str, &meta = _meta](const string& pinId, const Pin& pin) {
        PinType pt = meta.getPinType(pinId);
        str << pinId << " " << (int)pt << " -> " << pin.getConnectionsDesc() << endl;
    });
}

void Card::visitAllPins(const std::function<void (const string& id, const Pin&)> f) const {
    for (auto [ pinId, pin] : _pins) 
        f(pinId, pin);
}

Card& Machine::getCard(const PlugLocation& loc) {
    if (_cards.find(loc) == _cards.end()) 
        throw string("No card defined at location " + loc.toString());
    return _cards.at(loc);
}

Card& Machine::createCard(const CardMeta& meta,const PlugLocation& loc)  {
    if (_cards.find(loc) != _cards.end()) {
        throw string("Card already plugged in at " + loc.toString());
    }
    _cards.emplace(loc, Card(meta, loc));
    return _cards.at(loc);
}

Pin& Machine::getPin(const PinLocation& loc) {
    Card& card = getCard(loc.getPlugLocation());
    return card.getPin(loc.getPinId());
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
    for (auto [loc, card] : _cards)
        f(card);
}


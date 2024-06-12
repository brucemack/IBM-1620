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

CardMeta::CardMeta(const string& type, const string& desc, 
    const map<string, PinMeta>& pinMeta)
:   _type(type),
    _desc(desc) {    
    _pinMeta.insert(begin(pinMeta), end(pinMeta));
}

// TODO: PREDICATE SUPPORT
std::vector<std::string> CardMeta::getPinNames() const {
    std::vector<std::string> result;
    for (auto [n, v] : _pinMeta)
        result.push_back(n);
    return result;
}

std::vector<std::string> CardMeta::getSignalPinNames() const {
    std::vector<std::string> result;
    for (auto [n, v] : _pinMeta)
        if (v.type == PinType::INPUT ||
            v.type == PinType::OUTPUT)
            result.push_back(n);
    return result;
}

PinType CardMeta::getPinType(const string pinId) const {
    if (_pinMeta.find(pinId) == _pinMeta.end()) 
        throw string("Invalid pin ID : " + pinId);
    return _pinMeta.at(pinId).type;
}

// TODO: Move to metadata
std::string CardMeta::getDefaultNode(const std::string& pinName) const {
    if (pinName == "J") {
        return "gnd";
    } else if (pinName == "N") {
        return "vp12";
    } else if (pinName == "M") {
        return "vn12";
    } else {
        return string();
    }
}

Card::Card(const CardMeta& meta, const PlugLocation& loc)
:   _meta(meta),
    _loc(loc) {
}

Pin& Card::getPin(const string& id) {
    if (_pins.find(id) == _pins.end())
        _pins.emplace(id, Pin(*this, id));
    return _pins.at(id);
}

const Pin& Card::getPinConst(const string& id) const {
    if (_pins.find(id) == _pins.end())
        throw string("Pin not defined: " + id);
    return _pins.at(id);
}

bool Card::isPinUsed(const std::string& id) const {
    return !(_pins.find(id) == _pins.end());
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

Card& Machine::getOrCreateCard(const CardMeta& meta,const PlugLocation& loc)  {
    if (_cards.find(loc) == _cards.end()) 
        _cards.emplace(loc, Card(meta, loc));
    return _cards.at(loc);
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

std::vector<Wire> Machine::generateWires() const {

    auto result = std::vector<Wire>();
    unordered_set<string> pinsSeen;

    visitAllCards([&pinsSeen, &result](const Card& card) {
        card.visitAllPins([&pinsSeen, &result, &card](const string& pinId, const Pin& pin) {
            if (pinsSeen.find(pin.getDesc()) == pinsSeen.end()) {
                // Here is where we accumulate the pins on the wire
                vector<string> wirePins;
                // Visit all pins that connect to this pin
                pin.visitAllConnections([&pinsSeen, &wirePins](const Pin& connectedPin) {                    
                    wirePins.push_back(connectedPin.getDesc());
                    // Make sure not to hit this again.
                    pinsSeen.insert(connectedPin.getDesc());                    
                });
                if (!wirePins.empty()) 
                    result.push_back({ wirePins } );
            }
        });
    });

    return result;
}

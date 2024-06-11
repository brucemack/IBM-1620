#include <iostream>
#include <algorithm>

#include "Components.h"

using namespace std;

CardMeta::CardMeta(const std::string& type)
:   _type(type) {    
}

Pin::Pin(Card& card, const string& id) 
:   _card(card),
    _id(id) {        
}

string Pin::getDesc() const {
    return _card.getLocation().toString() + "/" + _id;
}

string Pin::getConnectionDesc() const {
    string res;
    bool first = true;
    for (auto conn : _connections) {
        if (!first)
            res = res + ", ";
        res = res + conn.get().getDesc();
        first = false;
    }
    return res;
}

void Pin::connect(Pin& pin) { 
    // Check to see if the connection is redundant
    if (std::find_if(_connections.begin(), _connections.end(), 
        [&pin](const std::reference_wrapper<Pin>& x) { 
            return std::addressof(pin) == std::addressof(x.get()); 
        }
    ) != _connections.end()) {
        throw string("Redundant pin connection: " + pin.getDesc());
    }
    _connections.push_back(std::reference_wrapper<Pin>(pin));
}

bool Pin::operator== (const Pin& other) const { 
    return this == std::addressof(other); 
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

void Card::dumpOn(std::ostream& str) const {
    str << "Pins:" << endl;
    for (auto [ pinId, pin] : _pins) {
        str << pinId << " -> " << pin.getConnectionDesc() << endl;
    }
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
    for (auto [loc, card] : _cards) {
        cout << loc.toString() << " : " << card.getMeta()._type << endl;
        card.dumpOn(str);
    }
}

#include <iostream>
#include <algorithm>

#include "Components.h"

using namespace std;

CardMeta::CardMeta(const std::string& type)
:   _type(type) {    
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
    visitAllPins([&str](const string& pinId, const Pin& pin) {
        str << pinId << " -> " << pin.getConnectionsDesc() << endl;
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
        cout << card.getLocation().toString() << " : " << card.getMeta()._type << endl;
        card.dumpOn(str);
    });
}

void Machine::visitAllCards(const std::function<void (const Card&)> f) const {
    for (auto [loc, card] : _cards)
        f(card);
}


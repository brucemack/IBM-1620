#include <iostream>
#include "Components.h"

using namespace std;

CardMeta::CardMeta(const std::string& type)
:   _type(type) {    
}

Pin::Pin(Card& card, const string& id) 
:   _card(card),
    _id(id) {        
}

Card::Card(const CardMeta& meta)
:   _meta(meta) {
}

Pin& Card::getPin(const string& id) {
    if (_pins.find(id) == _pins.end())
        _pins.emplace(id, Pin(*this, id));
    return _pins.at(id);
}

void Card::dumpOn(std::ostream& str) const {
    str << "Pins:" << endl;
    for (auto [ pinId, pin] : _pins) {
        str << pinId << endl;
    }
}

Card& Machine::getCard(const string& loc) {
    if (_cards.find(loc) == _cards.end()) 
        throw string("No card defined at location " + loc);
    return _cards.at(loc);
}

Card& Machine::getOrCreateCard(const CardMeta& meta,const string& loc)  {
    if (_cards.find(loc) == _cards.end()) 
        _cards.emplace(loc, Card(meta));
    return _cards.at(loc);
}



void Machine::dumpOn(std::ostream& str) const {
    str << "Cards:" << endl;
    for (auto [loc, card] : _cards) {
        cout << loc << " : " << card.getMeta()._type << endl;
        card.dumpOn(str);
    }
}

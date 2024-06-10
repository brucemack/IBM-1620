#include <iostream>
#include "Components.h"

using namespace std;

Card::Card(const CardMeta& meta)
:   _meta(meta) {
}


Wire& Machine::getOrCreateWire(const std::string& name) {
    if (_wires.find(name) == _wires.end()) 
        _wires.emplace(name, Wire());
    return _wires.at(name);
}


Card& Machine::getOrCreateCard(const CardMeta& meta,const string& loc)  {
    if (_cards.find(loc) == _cards.end()) 
        _cards.emplace(loc, Card(meta));
    return _cards.at(loc);
}

void Machine::dumpOn(std::ostream& str) const {
    str << "Nets:" << endl;
    for (auto [name, wire] : _wires) {
        cout << name << endl;
    }
}

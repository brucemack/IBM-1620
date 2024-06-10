/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _Components_h
#define _Components_h

#include <string>
#include <map>
#include <set>
#include <iostream>

class CardMeta {
};

class Card {
public:

    Card(const CardMeta& meta);

private:

    const CardMeta& _meta;
};

class Wire {
};

class Machine {
public:

    Card& getOrCreateCard(const CardMeta& cardMeta, const std::string& location);
    Wire& getOrCreateWire(const std::string& name);

    void dumpOn(std::ostream& str) const;

private:

    std::map<std::string, Card> _cards;
    std::map<std::string, Wire> _wires;
};


#endif



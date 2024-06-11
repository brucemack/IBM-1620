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
#include <vector>

class PinMeta {
};

class CardMeta {
public:

    CardMeta() { }
    CardMeta(const std::string& type);

    std::string _type;
};

class Card;

class Pin {
public:

    Pin(Card& card, const std::string& id);

    void connect(Pin& pin) { }

private:

    Card& _card;
    std::string _id;
};

class Card {
public:

    Card(const CardMeta& meta);

    const CardMeta& getMeta() const { return _meta; }

    /**
     * Gets the pin with the ID provided, creating one 
     * if necessary.
     */
    Pin& getPin(const std::string& id);

    void dumpOn(std::ostream& str) const;

private:

    const CardMeta& _meta;
    std::map<std::string, Pin> _pins;
};

class Machine {
public:

    Card& getCard(const std::string& location);
    Card& getOrCreateCard(const CardMeta& cardMeta, const std::string& location);

    void dumpOn(std::ostream& str) const;

private:

    std::map<std::string, Card> _cards;
};


#endif



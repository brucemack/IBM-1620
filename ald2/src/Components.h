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
#include <unordered_map>
#include <set>
#include <iostream>
#include <vector>

#include "Pin.h"
#include "PlugLocation.h"

class PinMeta {
};

class CardMeta {
public:

    CardMeta() { }
    CardMeta(const std::string& type);

    std::string getType() const { return _type; }

    virtual std::vector<std::string> getPinNames() const;

    /**
     * Used when a pin is not explicitly connected in the ALD.
     * This is helpful for ground/rail pins.
     */
    virtual std::string getDefaultNode(const std::string& pinName) const;

private:

    std::string _type;
};

class Card {
public:

    Card(const CardMeta& meta, const PlugLocation& loc);

    const CardMeta& getMeta() const { return _meta; }

    const PlugLocation& getLocation() const { return _loc; }

    bool isPinUsed(const std::string& id) const;

    /**
     * Gets the pin with the ID provided, creating one 
     * if necessary.
     */
    Pin& getPin(const std::string& id);

    const Pin& getPinConst(const std::string& id) const;

    void dumpOn(std::ostream& str) const;

    void visitAllPins(const std::function<void (const std::string& id, const Pin&)> f) const;

private:

    const CardMeta& _meta;
    PlugLocation _loc;
    std::map<std::string, Pin> _pins;
};

struct Wire {
    std::vector<std::string> pins;
};

class Machine {
public:

    Card& getCard(const PlugLocation& location);
    Card& getOrCreateCard(const CardMeta& cardMeta, const PlugLocation& location);

    void dumpOn(std::ostream& str) const;

    void visitAllCards(const std::function<void (const Card&)> c) const;

    /**
     * Generates all of the unique wires, given the current state of the machine.
     */
    std::vector<Wire> generateWires() const;

private:

    std::unordered_map<PlugLocation, Card> _cards;
};

#endif

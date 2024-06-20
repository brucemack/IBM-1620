/* IBM 1620 Logic Reproduction Project
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
#include <unordered_set>
#include <set>
#include <iostream>
#include <vector>

#include "Pin.h"
#include "PlugLocation.h"
#include "PinLocation.h"

enum PinType {
    UNKNOWN,
    INPUT, 
    OUTPUT,
    GND,
    VP12,
    VN12
};

// TODO: static member - conversion operator??
PinType str2PinType(const std::string& str);

struct PinMeta {
    std::string id;
    PinType type;
};

class CardMeta {
public:

    CardMeta() { }
    CardMeta(const std::string& type, const std::string& desc,
        const std::map<std::string, PinMeta>& pinMeta);

    std::string getType() const { return _type; }
    std::string getDesc() const { return _desc; }

    std::vector<std::string> getPinNames() const;

    std::vector<std::string> getSignalPinNames() const;

    // TODO: Add a way to get the pinmeta in its entirety
    PinType getPinType(const std::string pinId) const;

    /**
     * Used when a pin is not explicitly connected in the ALD.
     * This is helpful for ground/rail pins.
     */
    virtual std::string getDefaultNode(const std::string& pinName) const;

private:

    std::string _type;
    std::string _desc;
    std::unordered_map<std::string, PinMeta> _pinMeta;
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

/**
 * A wire is a set of electrically connected pins.
*/
struct Wire {
    std::vector<PinLocation> pins;
};

class Machine {
public:

    Card& getCard(const PlugLocation& location);

    Card& getOrCreateCard(const CardMeta& cardMeta, const PlugLocation& location);

    Pin& getPin(const PinLocation& loc);

    void dumpOn(std::ostream& str) const;

    void visitAllCards(const std::function<void (const Card&)> c) const;

    /**
     * Generates all of the unique wires, given the current state of the machine.
     * A wire is defined as a series of electrically connected pins.
     */
    std::vector<Wire> generateWires() const;

private:

    std::unordered_map<PlugLocation, Card> _cards;
};

#endif

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

class PlugLocation {
public:

    PlugLocation(const std::string& locationCode) : _loc(locationCode) { }
    PlugLocation(const PlugLocation& other) : _loc(other._loc) { }

    std::string toString() const { return _loc; }
    bool operator==(const PlugLocation& other) const { return _loc == other._loc; }

private:

    std::string _loc;
};

template<>
struct std::hash<PlugLocation>
{
    std::size_t operator()(const PlugLocation& s) const noexcept
    {
        return std::hash<std::string>{}(s.toString());
    }
};

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

    bool operator== (const Pin& other) const;

    void connect(Pin& pin);

    std::string getDesc() const;
    std::string getConnectionDesc() const;

private:

    Card& _card;
    std::string _id;
    std::vector<std::reference_wrapper<Pin>> _connections;
};

class Card {
public:

    Card(const CardMeta& meta, const PlugLocation& loc);

    const CardMeta& getMeta() const { return _meta; }
    const PlugLocation& getLocation() const { return _loc; }

    /**
     * Gets the pin with the ID provided, creating one 
     * if necessary.
     */
    Pin& getPin(const std::string& id);

    void dumpOn(std::ostream& str) const;

private:

    const CardMeta& _meta;
    PlugLocation _loc;
    std::map<std::string, Pin> _pins;
};


class Machine {
public:

    Card& getCard(const PlugLocation& location);
    Card& getOrCreateCard(const CardMeta& cardMeta, const PlugLocation& location);

    void dumpOn(std::ostream& str) const;

private:

    std::unordered_map<PlugLocation, Card> _cards;
};

#endif

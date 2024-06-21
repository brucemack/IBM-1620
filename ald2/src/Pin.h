/* IBM-1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _Pin_h
#define _Pin_h

#include <string>
#include <iostream>
#include <vector>
#include <functional>

#include "PinLocation.h"

class Card;
class PinMeta;

class Pin {
public:

    Pin(const PinMeta& meta, Card& card);

    const PinMeta& getMeta() const { return _meta; }

    bool operator== (const Pin& other) const;

    void connect(Pin& pin);

    bool isConnected() const { return !_connections.empty(); }

    PinLocation getLocation() const;
    
    /**
     * @returns A human-friendly list of the pins that this pin
     * is directly connected to.
     */
    std::string getConnectionsDesc() const;

    size_t hash() const;

    void visitImmediateConnections(const std::function<void (const Pin&)> f) const;

    void visitAllConnections(const std::function<void (const Pin&)> f) const;

private:

    const PinMeta& _meta;
    Card& _card;
    std::vector<std::reference_wrapper<Pin>> _connections;
};

template<>
struct std::hash<Pin>
{
    std::size_t operator()(const Pin& s) const noexcept { return s.hash(); }
};

#endif

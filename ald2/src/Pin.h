/* IBM-1620 Logic Reproduction 
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

class Card;

class Pin {
public:

    Pin(Card& card, const std::string& id);

    bool operator== (const Pin& other) const;

    void connect(Pin& pin);

    std::string getDesc() const;
    
    /**
     * @returns A human-friendly list of the pins that this pin
     * is directly connected to.
     */
    std::string getConnectionsDesc() const;

    size_t hash() const;

    void visitImmediateConnections(const std::function<void (const Pin&)> f) const;

    void visitAllConnections(const std::function<void (const Pin&)> f) const;

private:

    Card& _card;
    std::string _id;
    std::vector<std::reference_wrapper<Pin>> _connections;
};

template<>
struct std::hash<Pin>
{
    std::size_t operator()(const Pin& s) const noexcept { return s.hash(); }
};

#endif

/* IBM-1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _Machine_h
#define _Machine_h

#include <string>
#include <iostream>

#include "Card.h"
#include "Pin.h"
#include "PlugLocation.h"

class VerilogWire;

class Machine {
public:

    Card& getCard(const PlugLocation& location);

    Pin& getPin(const PinLocation& loc);

    Card& getOrCreateCard(const CardMeta& cardMeta, const PlugLocation location);

    void dumpOn(std::ostream& str) const;

    void visitAllCards(const std::function<void (const Card&)> c) const;

    /**
     * A utility function that traverses the machine and generates all of the 
     * VerilogWires needed to connect the cards.
    */
    static std::vector<VerilogWire> generateVerilogWires(const Machine& machine);

    static void generateVerilog(const Machine& machine, std::ostream& str);

private:

    std::unordered_map<PlugLocation, Card> _cards;
};

#endif

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
#include "CardMeta.h"

class Card {
public:

    Card(const Card&);
    Card(const CardMeta& meta, const PlugLocation& loc);

    const CardMeta& getMeta() const { return _meta; }

    PlugLocation getLocation() const { return _loc; }

    Pin& getPin(const std::string& id);

    const Pin& getPinConst(const std::string& id) const;

    void dumpOn(std::ostream& str) const;

    void visitAllPins(const std::function<void (const std::string& id, const Pin&)> f) const;

    void addPageReference(const std::string& pageRef) { _pageRefs.push_back(pageRef); }

private:

    const CardMeta& _meta;
    PlugLocation _loc;
    std::map<std::string, Pin> _pins;
    std::vector<std::string> _pageRefs;
};

#endif

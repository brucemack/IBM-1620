/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _PinLocation_h
#define _PinLocation_h

#include <string>
#include <iostream>
#include "PlugLocation.h"

/*
 * Describes a unique location for a pin on a card
 */
class PinLocation {
public:

    PinLocation() { }
    PinLocation(const PlugLocation& plugLoc, const std::string& pinId) : _plugLoc(plugLoc), _pinId(pinId) { }
    PinLocation(const PinLocation& other) : _plugLoc(other._plugLoc), _pinId(other._pinId) { }

    std::string toString() const { return _plugLoc.toString() + "_" + _pinId; }
    PlugLocation getPlugLocation() const { return _plugLoc; }
    std::string getPinId() const { return _pinId; }

    bool operator==(const PinLocation& other) const;

private:

    PlugLocation _plugLoc;
    std::string _pinId;
};

template<>
struct std::hash<PinLocation>
{
    std::size_t operator()(const PinLocation& s) const noexcept
    {
        return std::hash<std::string>{}(s.toString());
    }
};

#endif

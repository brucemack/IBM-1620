/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _PlugLocation_h
#define _PlugLocation_h

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
    bool operator==(const PlugLocation& other) const;

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

#endif

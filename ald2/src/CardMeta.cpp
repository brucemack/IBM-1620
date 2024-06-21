/* IBM 1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include "CardMeta.h"

using namespace std;

CardMeta::CardMeta(const string& type, const string& desc, 
    const map<string, PinMeta>& pinMeta)
:   _type(type),
    _desc(desc) {    
    std::for_each(begin(pinMeta), end(pinMeta),
        [&](std::pair<const string&, const PinMeta&> p) {
            _pinMeta.insert_or_assign(p.first, PinMeta(p.second));
        }
    );
}

// TODO: PREDICATE SUPPORT
std::vector<std::string> CardMeta::getPinNames() const {
    std::vector<std::string> result;
    for (auto [n, v] : _pinMeta)
        result.push_back(n);
    return result;
}

std::vector<std::string> CardMeta::getSignalPinNames() const {
    std::vector<std::string> result;
    for (auto [n, v] : _pinMeta)
        if (v.type == PinType::INPUT ||
            v.type == PinType::OUTPUT)
            result.push_back(n);
    return result;
}

PinType CardMeta::getPinType(const string pinId) const {
    if (_pinMeta.find(pinId) == _pinMeta.end()) 
        throw string("Invalid pin ID : " + pinId);
    return _pinMeta.at(pinId).type;
}

// TODO: Move to metadata
std::string CardMeta::getDefaultNode(const std::string& pinName) const {
    if (pinName == "J") {
        return "gnd";
    } else if (pinName == "N") {
        return "vp12";
    } else if (pinName == "M") {
        return "vn12";
    } else {
        return string();
    }
}

void CardMeta::visitAllPinMeta(const std::function<void (const PinMeta&)> f) const {
    std::for_each(_pinMeta.begin(), _pinMeta.end(),
        [&f](std::pair<string,const PinMeta&> p) { f(p.second); }
    );
}

/* IBM 1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _CardMeta_h
#define _CardMeta_h

#include <string>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <set>
#include <iostream>
#include <vector>
#include <functional>

#include "PinMeta.h"

class CardMeta {
public:

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

    void visitAllPinMeta(const std::function<void (const PinMeta&)> f) const;

private:

    std::string _type;
    std::string _desc;
    std::unordered_map<std::string, PinMeta> _pinMeta;
};

#endif


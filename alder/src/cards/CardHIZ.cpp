/* IBM 1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include "cards/CardHIZ.h"

using namespace std;

static map<string, PinMeta> Pins = { 
    { "A", PinMeta { "A", PinType:: OUTPUT } }
};

CardHIZMeta::CardHIZMeta() 
: CardMeta("HIZ", "High Impedance", Pins) {     
}

std::vector<std::string> CardHIZMeta::getPinNames() const {
    return std::vector<std::string> { "A" };
}

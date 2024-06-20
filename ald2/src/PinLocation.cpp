/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include "PinLocation.h"

bool PinLocation::operator== (const PinLocation& other) const { 
    return _plugLoc == other._plugLoc && _pinId == other._pinId; 
}

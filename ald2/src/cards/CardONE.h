/* IBM-1620 Logic Reproduction 
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _CardONE_h
#define _CardONE_h

#include "Components.h"

class CardONEMeta : public CardMeta {
public:

    CardONEMeta(); 

    virtual std::vector<std::string> getPinNames() const {
        return std::vector<std::string> { "A" };
    }
};

#endif



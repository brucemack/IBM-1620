/* IBM 1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _CardHIZ_h
#define _CardHIZ_h

#include "CardMeta.h"

class CardHIZMeta : public CardMeta {
public:

    CardHIZMeta();
    virtual ~CardHIZMeta() { }

    virtual std::vector<std::string> getPinNames() const;
};

#endif



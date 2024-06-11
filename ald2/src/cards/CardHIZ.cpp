#include "cards/CardHIZ.h"

using namespace std;

CardHIZMeta::CardHIZMeta() 
: CardMeta("HIZ") {     
}

std::vector<std::string> CardHIZMeta::getPinNames() const {
    return std::vector<std::string> { "A" };
}

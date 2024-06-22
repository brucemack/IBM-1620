#include "PinMeta.h"

using namespace std;

PinType str2PinType(const string& str) {
    if (str == "UNKNOWN") 
        return PinType::UNKNOWN;
    else if (str == "PASSIVE") 
        return PinType::PASSIVE;
    else if (str == "INPUT")
        return PinType::INPUT;
    else if (str == "OUTPUT")
        return PinType::OUTPUT;
    else if (str == "GND")
        return PinType::GND;
    else if (str == "VP12")
        return PinType::VP12;
    else if (str == "VN12")
        return PinType::VN12;
    else 
        throw string("Unrecognized pin type: " + str);
}

DriveType str2DriveType(const string& str) {
    if (str == "AH") 
        return DriveType::AH;
    else if (str == "AH_PD") 
        return DriveType::AH_PD;
    else if (str == "AL") 
        return DriveType::AL;
    else if (str == "AL_PD") 
        return DriveType::AL_PU;
    else
        throw string("Unrecognized drive type " + str);
}

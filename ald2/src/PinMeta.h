/* IBM 1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _PinMeta_h
#define _PinMeta_h

#include <string>

enum PinType {
    UNKNOWN,
    PASSIVE,
    INPUT, 
    OUTPUT,
    NC,
    GND,
    VP12,
    VN12
};

enum DriveType {
    NONE,
    S01,
    S0Z,
    S1Z,
    S01Z
};

// TODO: static member - conversion operator??
PinType str2PinType(const std::string& str);
DriveType str2DriveType(const std::string& str);

class PinMeta {
public: 

    PinMeta(const std::string& i, PinType t, DriveType dt = DriveType::S01) 
        : _id(i), _type(t), _driveType(dt) { }
    PinMeta(const PinMeta& other) 
        : _id(other._id), _type(other._type), _driveType(other._driveType) { }

    std::string getId() const { return _id; }

    PinType getType() const { return _type; }

    DriveType getDriveType() const { return _driveType; }

    /**
     * @returns Indication of whether this pin is used for logic signal, as opposed
     * to power/ground/passive/etc.
    */
    bool isLogicSignal() const { return _type == PinType::INPUT || _type == PinType::OUTPUT; }

private:

    std::string _id;
    PinType _type;
    DriveType _driveType;
};

#endif

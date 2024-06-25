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
    VN12,
    SYSCLOCK
};

enum DriveType {
    NO_DRIVE,
    // Active high, no pull-down (open collector)
    AH,
    // Active high, pull-down
    AH_PD,
    // Active low, no pull-up (emmitter follower)
    AL,
    // Active low, pull-up
    AL_PU
};

enum TieType {
    TIE_NONE,
    TIE_GND,
    TIE_VP12,
    TIE_VN12
};

// TODO: static member - conversion operator??
PinType str2PinType(const std::string& str);
DriveType str2DriveType(const std::string& str);
TieType str2TieType(const std::string& str);

class PinMeta {
public: 

    PinMeta(const std::string& i, PinType t, 
        DriveType dt = DriveType::AH_PD, TieType tt = TieType::TIE_NONE) 
        : _id(i), _type(t), _driveType(dt), _tieType(tt) { }
    PinMeta(const PinMeta& other) 
        : _id(other._id), _type(other._type), 
          _driveType(other._driveType), _tieType(other._tieType) { }

    std::string getId() const { return _id; }

    PinType getType() const { return _type; }

    DriveType getDriveType() const { return _driveType; }

    TieType getTieType() const { return _tieType; }

    /**
     * @returns Indication of whether this pin is used for logic signal, as opposed
     * to power/ground/passive/etc.
    */
    bool isLogicSignal() const { return _type == PinType::INPUT || _type == PinType::OUTPUT || 
        _type == PinType::SYSCLOCK; }

private:

    std::string _id;
    PinType _type;
    DriveType _driveType;
    TieType _tieType;
};

#endif

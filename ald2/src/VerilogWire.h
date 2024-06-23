/* IBM-1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#ifndef _VerilogWire_h
#define _VerilogWire_h

#include <string>
#include <iostream>
#include <vector>

class Pin;
class PinLocation;
class Machine;

class VerilogWire {
public:

    VerilogWire(const Machine& mach);

    /**
     * @return true if there are no pins connected to this wire.
    */
    bool empty() const { return _drivenPins.empty() && _drivingPins.empty(); }

    bool isMultiDriver() const { return _drivingPins.size() > 1; }

    /**
     * Includes a pin in the list that are joined together by this wire.
    */
    void addConnection(const Pin& pin);

    bool isConnectedToPin(const PinLocation& pl) const;

    std::vector<PinLocation> getConnectedPins() const;

    std::string getConnectedPinsString() const;

    /**
     * Synthesizes any Verilog statements that go with this wire.
    */
    void synthesizeVerilog(std::ostream& str);

    /**
     * Returns the string representation of what the designated
     * pin should be bound to. Suitable for using in a port
     * connection. Ex:
     * 
     * (.a(RETURNED_STRING))
    */
    std::string getVerilogPortBinding(const PinLocation& pin) const;

    void dumpOn(std::ostream& str) const;

private:

    // Uniquely generated
    const unsigned int _id;
    const Machine& _machine;
    std::vector<PinLocation> _drivenPins;
    std::vector<PinLocation> _drivingPins;
    std::vector<PinLocation> _passivePins;
    // This is the name of the wire that all of the DRIVEN pins 
    // should be connected to.  This depends on whether any 
    // special logical adjustments are made due to multi-drivers
    // and/or passives on the wire.
    std::string _drivenName;
};

#endif

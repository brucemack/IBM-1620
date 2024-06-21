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

    /**
     * Includes a pin in the list that are joined together by this wire.
    */
    void addConnection(const Pin& pin);

    /**
     * Synthesizes any Verilog statements that go with this wire.
    */
    void synthesizeVerilog(std::ostream& str) const;

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

    const Machine& _machine;
    std::vector<PinLocation> _drivenPins;
    std::vector<PinLocation> _drivingPins;
};

#endif

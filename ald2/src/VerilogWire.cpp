/* IBM-1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include <string>
#include "VerilogWire.h"
#include "Components.h"

using namespace std;

VerilogWire::VerilogWire(const Machine& mach) 
:  _machine(mach) { }

void VerilogWire::addConnection(const Pin& pin) {
}

void VerilogWire::synthesizeVerilog(ostream& str) const {
}

string VerilogWire::getVerilogPortBinding(const PinLocation& pin) const {
   string result;
   return result;
}

void VerilogWire::dumpOn(std::ostream& str) const {
}


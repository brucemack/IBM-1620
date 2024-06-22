/* IBM-1620 Logic Reproduction Project
   Copyright (C) 2024 - Bruce MacKinnon
 
   This work is covered under the terms of the GNU Public License (V3). Please consult the 
   LICENSE file for more information.

   This work is being made available for non-commercial use. Redistribution, commercial 
   use or sale of any part is prohibited.
*/
#include <string>

#include "VerilogWire.h"
#include "Card.h"
#include "CardMeta.h"
#include "Machine.h"

using namespace std;

static unsigned int idCounter = 0;

VerilogWire::VerilogWire(const Machine& mach) 
:  _id(++idCounter), _machine(mach) { }

void VerilogWire::addConnection(const Pin& pin) {
   if (pin.getMeta().getType() == PinType::INPUT)
      _drivenPins.push_back(pin.getLocation());
   else if (pin.getMeta().getType() == PinType::OUTPUT)
      _drivingPins.push_back(pin.getLocation());
   else if (pin.getMeta().getType() == PinType::PASSIVE)
      _passivePins.push_back(pin.getLocation());
   else {
      throw string("addConnection() on invalid pin type " + pin.getLocation().toString());
   }
}

void VerilogWire::synthesizeVerilog(ostream& str) const {
   // No drivers is an error
   if (_drivingPins.empty()) {
      dumpOn(cout);
      throw string("No driving pins on wire");
   }
   // If there's only one driver then things are easy
   else if (_drivingPins.size() == 1) {
      // The whole net is named by the output
      auto pl = _drivingPins.at(0);
      str << "    wire W_" << pl.toString() << ";" << endl;
   }
   // Multi-drivers
   else {
      // Create a wire for each driving pin
      for (auto pl : _drivingPins) {
         str << "    wire W_" << pl.toString() << ";" << endl;
      }

      const DriveType dt = _machine.getPinConst(_drivingPins.at(0)).getMeta().getDriveType();

      // Look for the case where the drivers are active high
      if (dt == DriveType::AH || dt == DriveType::AH_PD) {  
         // Check compatibility, and determine if a pull down exists anywhere
         // in the drivers.
         bool hasPullDown = false;
         for (const PinLocation& pl : _drivingPins) {
            const DriveType dt  = _machine.getPinConst(pl).getMeta().getDriveType();
            if (!(dt == DriveType::AH || dt == DriveType::AH_PD)) {
               throw string("Driving pin compatibility problem: " + pl.toString());
            }
            if (dt == DriveType::AH_PD)
               hasPullDown = true;
         }
         // Generate a suitable net. Any of the drivers can pull the net high with a 1.
         // The default value depends on whether there is a pull down amongst the
         // driving nets.
         string defaultValue;
         if (!hasPullDown) 
            defaultValue = "1'bz";
         else
            defaultValue = "0";
         str << "    // Automatically generated DOT-OR (active high)" << endl;
         str << "    wire W_DOT_" << to_string(_id) << " = ";
         bool first = true;
         str << "(";
         for (auto pl : _drivingPins) {
            if (!first)
               str << " || ";
            str << "W_" << pl.toString() << " === 1";
            first = false;
         }
         str << ") ? 1 : " << defaultValue << ";";
         str << endl;
      }
      else if (dt == DriveType::AL || dt == DriveType::AL_PU) {
         // Check compatibility, and determine if a pull up exists anywhere in the drivers.
         bool hasPullUp = false;
         for (const PinLocation& pl : _drivingPins) {
            const DriveType dt  = _machine.getPinConst(pl).getMeta().getDriveType();
            if (!(dt == DriveType::AL || dt == DriveType::AL_PU)) {
               throw string("Driving pin compatibility problem: " + pl.toString());
            }
            if (dt == DriveType::AL_PU)
               hasPullUp = true;
         }
         // Generate a suitable net. Any of the drivers can pull the net low with a 0.
         // The default value depends on whether there is a pull up amongst the
         // driving nets.
         string defaultValue;
         if (!hasPullUp) 
            defaultValue = "1'bz";
         else
            defaultValue = "1";
         str << "    // Automatically generated DOT-OR (active low)" << endl;
         str << "    wire W_DOT_" << to_string(_id) << " = ";
         bool first = true;
         str << "(";
         for (auto pl : _drivingPins) {
            if (!first)
               str << " || ";
            str << "W_" << pl.toString() << " === 0";
            first = false;
         }
         str << ") ? 0 : " << defaultValue << ";";
         str << endl;
      }
   }
}

bool VerilogWire::isConnectedToPin(const PinLocation& pl) const {
   return std::find(begin(_drivingPins), end(_drivingPins), pl) != end(_drivingPins) ||
      std::find(begin(_drivenPins), end(_drivenPins), pl) != end(_drivenPins);
}

vector<PinLocation> VerilogWire::getConnectedPins() const  {
   vector<PinLocation> result;
   result.insert(end(result), begin(_drivingPins), end(_drivingPins));
   result.insert(end(result), begin(_drivenPins), end(_drivenPins));
   return result;
}

string VerilogWire::getVerilogPortBinding(const PinLocation& pin) const {
   string result;

   if (isMultiDriver()) {
      // In the multi-driver situation we tell the driving pins to connect
      // to the pin-specific wires
      if (std::find(begin(_drivingPins), end(_drivingPins), pin) != end(_drivingPins)) {
         return "W_" + pin.toString();
      }
      // Everything else connects to the synthesized DOT-OR net.
      else {
         return "W_DOT_" + to_string(_id);
      }
   }
   else {
      // In a single-driver situation everything on the wire is connected to 
      // the same single driving pin
      auto pl = _drivingPins.at(0);
      return "W_" + pl.toString();
   }
   return result;
}

void VerilogWire::dumpOn(std::ostream& str) const {
   str << "Verilog Wire:" << endl;
   str << "  Driving Pins:" << endl;
   for (auto p : _drivingPins) {
      cout << "    " << p.toString() << endl;
   }
   str << "  Driven Pins:" << endl;
   for (auto p : _drivenPins) {
      cout << "    " << p.toString() << endl;
   }
   if (!_passivePins.empty()) {
      str << "  Passive Pins:" << endl;
      for (auto p : _passivePins) {
         cout << "    " << p.toString() << endl;
      }
   }
}


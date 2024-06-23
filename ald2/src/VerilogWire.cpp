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
   else if (pin.getMeta().getType() == PinType::PASSIVE) {
      if (!_passivePins.empty())
         throw string("addConnection() with multiple passive pins " + pin.getLocation().toString());
      _passivePins.push_back(pin.getLocation());
   } else {
      throw string("addConnection() on invalid pin type " + pin.getLocation().toString());
   }
}

void VerilogWire::synthesizeVerilog(ostream& str) {

   // No drivers is an error
   if (_drivingPins.empty()) 
      throw string("No driving pins on wire: " + getConnectedPinsString());

   // If there's only one driver and no passives then things are easy:
   // The whole net is named by the output
   else if (_drivingPins.size() == 1 && _passivePins.size() == 0) {
      auto pl = _drivingPins.at(0);
      _drivenName = "W_" + pl.toString();
      str << "    wire W_" << _drivenName << ";" << endl;
   }
   // Everything else is more complicated because it involves combinations
   // of drivers and passives.
   else {

      // Figure out what we've got on the line
      bool activePullUp = false;
      bool activePullDown = false;
      bool passivePullUp = false;
      bool passivePullDown = false;

      // Consider the drivers first
      for (auto pl : _drivingPins) {

         // Create a wire for each driving pin
         str << "    wire W_" << pl.toString() << ";" << endl;

         const DriveType dt = _machine.getPinConst(pl).getMeta().getDriveType();
         if (dt == DriveType::AH || dt == DriveType::AH_PD) {
            activePullUp = true;
            if (dt == DriveType::AH_PD) {
               passivePullDown = true;
            }
         }
         if (dt == DriveType::AL || dt == DriveType::AL_PU) {
            activePullDown = true;
            if (dt == DriveType::AL_PU) {
               passivePullUp = true;
            }
         }
      }

      // Check to see what the passives are doing
      for (auto pl : _passivePins) {
         const TieType tt = _machine.getPinConst(pl).getMeta().getTieType();
         //cout << "  Passive check on " << pl << " " << tt << endl;
         if (tt == TieType::TIE_GND || tt == TieType::TIE_VP12)
            passivePullUp = true;
         else if (tt == TieType::TIE_VN12)
            passivePullDown = true;
      }

      // Look for problem combinations
      if (activePullDown && activePullUp)
         throw string("Conflicting drive types on wire: " + getConnectedPinsString());
      if (activePullUp && passivePullUp)
         throw string("Active and passive pull up on wire: " + getConnectedPinsString());
      if (activePullDown && passivePullDown)
         throw string("Active and passive pull down on wire: " + getConnectedPinsString());
      // This case is a problem because there is nothing to pull down.
      // In the oppose case (activePullDown) we have the benefit of the input pull up
      if (activePullUp && !passivePullDown)
         throw string("Active pull up with no pull down on wire: " + getConnectedPinsString());

      // Synthesize a Verilog combination of the drivers/passives.

      // The pull up case looks for any 1's driving the wire
      if (activePullUp) {
         // Generate a suitable net. Any of the drivers can pull the net high with a 1.
         // The default value depends on whether there is a pull down amongst the
         // driving nets.
         string defaultValue;
         string desc;
         if (!passivePullDown) {
            defaultValue = "1'bz";
            desc = "active high, no pull down";
         } else {
            defaultValue = "0";
            desc = "active high with pull down";
         }
         _drivenName = "W_DOT_" + to_string(_id);
         str << "    // Automatically generated DOT-OR (" << desc << ")" << endl;
         str << "    wire " << _drivenName << " = ";
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
      else  {
         // Generate a suitable net. Any of the drivers can pull the net low with a 0.
         // The default value depends on whether there is a pull up amongst the
         // driving nets.
         string defaultValue;
         string desc;
         if (!passivePullUp) {
            defaultValue = "1'bz";
            desc = "active low, no pull up";
         } else {
            defaultValue = "1";
            desc = "active low with pull up";
         }
         _drivenName = "W_DOT_" + to_string(_id);
         str << "    // Automatically generated DOT-OR (" << desc << ")" << endl;
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

string VerilogWire::getConnectedPinsString() const {
   string result;
   for (PinLocation pl : getConnectedPins()) {
      if (!result.empty())
         result = result + " ";
      result = result + pl.toString();
   }
   return result;
}

vector<PinLocation> VerilogWire::getConnectedPins() const  {
   vector<PinLocation> result;
   result.insert(end(result), begin(_drivingPins), end(_drivingPins));
   result.insert(end(result), begin(_drivenPins), end(_drivenPins));
   result.insert(end(result), begin(_passivePins), end(_passivePins));
   return result;
}

string VerilogWire::getVerilogPortBinding(const PinLocation& pin) const {
   // Driver pins always connect to their own wire
   if (std::find(begin(_drivingPins), end(_drivingPins), pin) != end(_drivingPins)) {
      return "W_" + pin.toString();
   }
   // Driven pins connect to something that is a function of whether extra logic
   // needed to be added to the net.
   else {
      return _drivenName;
   }
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


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

using namespace std;

static unsigned int idCounter = 0;

VerilogWire::VerilogWire(const Machine& mach) 
:  _id(++idCounter), _machine(mach) { }

void VerilogWire::addConnection(const Pin& pin) {
   if (pin.getMeta().getType() == PinType::INPUT)
      _drivenPins.push_back(pin.getLocation());
   else if (pin.getMeta().getType() == PinType::OUTPUT) {
      // Do a sanity check for multi-driving
      if (_drivingPins.size() > 0 && !pin.getMeta().canMultidrive())
         throw string("Not allowed to connect multiple outputs on pin " + pin.getLocation().toString());
      _drivingPins.push_back(pin.getLocation());
   }
   else {
      throw string("addConnection() on invalid pin type " + pin.getLocation().toString());
   }
}

void VerilogWire::synthesizeVerilog(ostream& str) const {
   if (isMultiDriver()) {
      // Create a wire for each driving pin
      for (auto pl : _drivingPins) {
         str << "    wire W_" << pl.toString() << ";" << endl;
      }
      // Create the or expression.
      str << "    // Automatically generated DOT-OR" << endl;
      str << "    wire W_DOT_" << to_string(_id) << " = ";
      bool first = true;
      str << "(";
      for (auto pl : _drivingPins) {
         if (!first)
            str << " || ";
         str << "W_" << pl.toString() << " === 0";
         first = false;
      }
      str << ") ? 0 : 1'bz;";
      str << endl;
   } 
   else {
      // The whole net is named by the output
      auto pl = _drivingPins.at(0);
      str << "    wire W_" << pl.toString() << ";" << endl;
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
   str << "Driving Pins:" << endl;
   for (auto p : _drivingPins) {
      cout << " " << p.toString() << endl;
   }
   str << "Driven Pins:" << endl;
   for (auto p : _drivenPins) {
      cout << " " << p.toString() << endl;
   }
}


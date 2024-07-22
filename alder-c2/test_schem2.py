"""
IBM-1620 Logic Reproduction 
Copyright (C) 2024 - Bruce MacKinnon
 
This work is covered under the terms of the GNU Public License (V3). Please consult the 
LICENSE file for more information.

This work is being made available for non-commercial use. Redistribution, commercial 
use or sale of any part is prohibited.
"""
import pytest 
import schem2

def test_1():

    m = schem2.Machine()
    m.load_from_ald2("../daves-1f/pages/01.82.70.1.yaml")
    m.load_from_ald1("../daves-1f/pages/01.06.01.1.yaml")
    print(m.get_device_names())

    def v2(pin):
        print("  ", pin.get_id())
        for c in pin.get_connections():
            print("       Conn :", c.get_global_id())

    def v1(device):
        print(device.get_id())
        device.visit_pins(v2)

    m.visit_devices(v1)        

    m.create_nodes()

test_1()

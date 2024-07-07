Commands
========

We are not using a virtual environment. This command was used to create a shell with 
Python configured properly:

        nix-shell -p 'python3.withPackages (ps: with ps; [ numpy matplotlib tk pytest pyyaml lark])'

Notes on Mechanical Linkages
============================

* Current in either of two coils -> multiple switch closure, with spring return.  Observes 
a current in the electronic network.  Provides a set of binary state variables 
that can be observed.
  * Ganged duo relays
  * Linkage between shift solenoid and SHIFT CONTACT switch
* Current in coil 1 -> multiple switch closure, current in coil 2 -> multiple switch open, 
no spring return.  Observes two currents in the electronic network.  Provides a set of 
binary state variables that can be observed.
  * Ganged latching relays
* Rotating cam contact switch with specific make and break angles. Provides a binary state
variable that can be observed.
  * CRCB switches

devices:
  tw_r30:
    type: duorelay
    triggerthreshold: 0.001
    triggercurrents:
      - name of branch 0 (to observe)
      - name of branch 1 (to observe)
    ncstates:
      - name of state 0
      - name of state 1
      - ...
    nostates:
      - name of state 0
      - name of state 1
      - ...
  tw_crcb:
     type: crcb
     points:
       - make: 150
         break: 300
         state: name_of_state 



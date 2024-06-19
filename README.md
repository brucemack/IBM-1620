This project contains tools used to digitize ALD diagrams from the IBM 1620.

More to follow ...

Copyright
=========

Copyright (C) 2024 - Bruce MacKinnon

This work is covered under the terms of the GNU Public License (V3). Please consult the LICENSE file for more information.

This work is being made available for non-commercial use. Redistribution, commercial use or sale of any part is prohibited.


Commands
========

This command was used to create a shell with Python configured properly:

        nix-shell -p 'python3.withPackages (ps: with ps; [ numpy matplotlib tk pytest])'

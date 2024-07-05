Commands
========

We are not using a virtual environment. This command was used to create a shell with 
Python configured properly:

        nix-shell -p 'python3.withPackages (ps: with ps; [ numpy matplotlib tk pytest pyyaml])'


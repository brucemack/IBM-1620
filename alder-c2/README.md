Commands
========

On NixOS we are not using a virtual environment. This command was used to create a shell with 
Python configured properly:

    nix-shell -p 'python3.withPackages (ps: with ps; [ numpy matplotlib tk pytest pyyaml lark])'

On Windows we are using a virtual environment.  These are the setup commands:

    python -m venv dev
    dev\scripts\activate
    pip install -r requirements.txt
    
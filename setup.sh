#!/bin/bash

# YESSSSS SETUP.SH
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip3 not found. Installing..."
    sudo apt install -y python3-pip
fi

# stfu bro
pip3 install --upgrade pip
pip3 install pyngrok pycryptodome

# CHECK DA FAKING INSTALLATION
echo "Verifying installations... BECAUSE I SAID SO"
python3 -c "import pyngrok; import Crypto; print('Packages installed successfully')"

echo "Setup completed."

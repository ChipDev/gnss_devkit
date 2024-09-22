#!/bin/bash
sudo apt update
sudo apt install gpsd
gpsd --version
sudo apt install python3
python3 --version
sudo apt install python3-pip
pip3 --version
sudo apt install socat

echo "apt-get requirements satisfied"

pip install -r requirements.txt --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org

echo "pip requirements satisfied. You should be good to go!"

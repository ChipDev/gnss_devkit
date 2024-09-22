#!/bin/bash

# Function to check if a command was successful
check_success() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

# Update package lists
sudo apt update
check_success "apt update"

# Install gpsd
sudo apt install -y gpsd
check_success "gpsd installation"

# Check gpsd version
gpsd --version
check_success "gpsd version check"

# Install Python3
sudo apt install -y python3
check_success "Python3 installation"

# Check Python3 version
python3 --version
check_success "Python3 version check"

# Install pip3
sudo apt install -y python3-pip
check_success "pip3 installation"

# Check pip3 version
pip3 --version
check_success "pip3 version check"

# Install python is python3
sudo apt install -y python-is-python3
check_success "python-is-python3 installation"

# Install socat
sudo apt install -y socat
check_success "socat installation"

echo "apt-get requirements satisfied"

# Install Python requirements
pip3 install -r requirements.txt --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org
check_success "Python requirements installation"

echo "MASKING GPSD FOR DEVELOPMENT WITH COMMAND."
sudo systemctl mask gpsd

echo "Requirements satisfied. You should be good to go!"

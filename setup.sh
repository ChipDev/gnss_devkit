#!/bin/bash

# Function to check if a command was successful
check_success() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

# Install required system deps
sudo apt update
check_success "apt update"

sudo apt install -y gpsd python3 python3-pip python-is-python3 socat python3-venv
check_success "System dependencies installation"

# Check versions
gpsd --version
check_success "gpsd version check"
python3 --version
check_success "Python3 version check"
pip3 --version
check_success "pip3 version check"

echo "apt-get requirements satisfied"

# Create a virtual environment for pip to not throw errors
python3 -m venv .venv
check_success "Virtual environment creation"

# Activate the virtual environment
source .venv/bin/activate
check_success "Virtual environment activation"

# Install Python requirements in the virtual environment
pip install -r requirements.txt
check_success "Python requirements installation"

echo "MASKING GPSD FOR DEVELOPMENT WITH COMMAND."
sudo systemctl mask gpsd

# Deactivate the virtual environment
deactivate

# Create an activation script
cat << EOF > activate_venv.sh
#!/bin/bash
source .venv/bin/activate
EOF
chmod +x activate_venv.sh

echo "Setup successful. Activate the virtual environment (before running start_gps.py) via: source activate_venv.sh"

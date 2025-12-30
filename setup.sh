#!/bin/bash

# Setup script for Fog-based AI Network Anomaly Detection System
# This script installs all dependencies and sets up the environment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fog AI Anomaly Detection - Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root for system packages
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else
    SUDO="sudo"
fi

# Update package list
echo -e "${YELLOW}[1/5] Updating package list...${NC}"
$SUDO apt-get update -qq

# Install system dependencies
echo -e "${YELLOW}[2/5] Installing system dependencies...${NC}"
$SUDO apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    tshark \
    wireshark-common \
    iperf3 \
    hping3 \
    nmap \
    net-tools \
    > /dev/null 2>&1

# Install Mininet (if not already installed)
if ! command -v mn &> /dev/null; then
    echo -e "${YELLOW}[3/5] Installing Mininet...${NC}"
    $SUDO apt-get install -y mininet > /dev/null 2>&1
else
    echo -e "${GREEN}[3/5] Mininet already installed${NC}"
fi

# Install Python dependencies
echo -e "${YELLOW}[4/5] Installing Python dependencies...${NC}"
pip3 install --user -r requirements.txt > /dev/null 2>&1 || {
    echo -e "${YELLOW}Retrying with sudo...${NC}"
    $SUDO pip3 install -r requirements.txt
}

# Set up Wireshark permissions
echo -e "${YELLOW}[5/5] Setting up permissions...${NC}"
$SUDO usermod -a -G wireshark $USER 2>/dev/null || true

# Create directories
mkdir -p logs models datasets

# Set permissions
chmod +x run.sh
chmod +x mininet/topology.py
chmod +x fog_node/*.py
chmod +x example_usage.py

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Note: You may need to log out and log back in for Wireshark permissions to take effect.${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Review README.md for usage instructions"
echo -e "  2. Run: ./run.sh"
echo -e "  3. Or test components: python3 example_usage.py"
echo ""


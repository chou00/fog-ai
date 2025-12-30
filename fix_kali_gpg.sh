#!/bin/bash

# Script to fix Kali Linux GPG key issues
# Run this before setup.sh if you encounter GPG errors

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fix Kali Linux GPG Keys${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}This script needs sudo privileges${NC}"
    echo -e "${YELLOW}Running with sudo...${NC}"
    exec sudo bash "$0" "$@"
fi

echo -e "${YELLOW}[1/3] Updating GPG keys...${NC}"

# Method 1: Update keys from Kali archive
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5 2>/dev/null || {
    echo -e "${YELLOW}Trying alternative method...${NC}"
    
    # Method 2: Download and add key directly
    wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add - 2>/dev/null || {
        echo -e "${YELLOW}Trying method 3...${NC}"
        
        # Method 3: Use gpg directly
        gpg --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5 2>/dev/null || true
        gpg --export ED65462EC8D5E4C5 | apt-key add - 2>/dev/null || true
    }
}

echo -e "${YELLOW}[2/3] Updating package list...${NC}"
apt-get update -qq

echo -e "${YELLOW}[3/3] Verifying fix...${NC}"
if apt-get update -qq 2>&1 | grep -q "GPG error"; then
    echo -e "${RED}GPG issue still exists. Trying manual fix...${NC}"
    
    # Manual fix: Remove problematic sources and re-add
    echo -e "${YELLOW}Attempting manual repository fix...${NC}"
    
    # Backup sources.list
    cp /etc/apt/sources.list /etc/apt/sources.list.backup 2>/dev/null || true
    
    # Try to fix by updating the keyring package
    apt-get install -y kali-archive-keyring 2>/dev/null || {
        echo -e "${YELLOW}Installing keyring from archive...${NC}"
        wget -q -O /tmp/kali-archive-keyring.deb http://http.kali.org/kali/pool/main/k/kali-archive-keyring/kali-archive-keyring_2022.2_all.deb 2>/dev/null || \
        wget -q -O /tmp/kali-archive-keyring.deb http://http.kali.org/kali/pool/main/k/kali-archive-keyring/kali-archive-keyring_2023.2_all.deb 2>/dev/null || \
        echo -e "${YELLOW}Could not download keyring package${NC}"
        
        if [ -f /tmp/kali-archive-keyring.deb ]; then
            dpkg -i /tmp/kali-archive-keyring.deb 2>/dev/null || true
            apt-get update -qq
        fi
    }
else
    echo -e "${GREEN}GPG issue resolved!${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GPG Fix Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "You can now run: ./setup.sh"
echo ""


#!/bin/bash

# Fog-based AI Network Anomaly Detection System
# Execution Script
#
# This script starts all components of the system:
# 1. Ryu SDN Controller
# 2. Mininet Topology
# 3. Fog Agents

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Create necessary directories
mkdir -p logs models datasets

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fog-based AI Network Anomaly Detection${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# Check Mininet
if ! command -v mn &> /dev/null; then
    echo -e "${RED}Error: Mininet not found. Install with: sudo apt-get install mininet${NC}"
    exit 1
fi

# Check Ryu
if ! command -v ryu-manager &> /dev/null; then
    echo -e "${RED}Error: Ryu not found. Install with: pip3 install ryu${NC}"
    exit 1
fi

echo -e "${GREEN}Prerequisites OK${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    pkill -f "ryu-manager" 2>/dev/null || true
    pkill -f "fog_agent.py" 2>/dev/null || true
    sudo pkill -f "mininet" 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete${NC}"
}

trap cleanup EXIT INT TERM

# Start Ryu Controller
echo -e "${YELLOW}Starting Ryu SDN Controller...${NC}"
cd ryu_controller
ryu-manager controller.py --verbose > ../logs/controller.log 2>&1 &
RYU_PID=$!
cd ..
sleep 3

if ps -p $RYU_PID > /dev/null; then
    echo -e "${GREEN}Ryu Controller started (PID: $RYU_PID)${NC}"
else
    echo -e "${RED}Failed to start Ryu Controller${NC}"
    exit 1
fi

# Start Fog Agents
echo -e "${YELLOW}Starting Fog Agents...${NC}"
cd fog_node

# Fog Node 1
python3 fog_agent.py --node-id fog1 --simulated --model isolation_forest > ../logs/fog1.log 2>&1 &
FOG1_PID=$!

# Fog Node 2
python3 fog_agent.py --node-id fog2 --simulated --model isolation_forest > ../logs/fog2.log 2>&1 &
FOG2_PID=$!

cd ..
sleep 2

if ps -p $FOG1_PID > /dev/null && ps -p $FOG2_PID > /dev/null; then
    echo -e "${GREEN}Fog Agents started (PIDs: $FOG1_PID, $FOG2_PID)${NC}"
else
    echo -e "${RED}Failed to start Fog Agents${NC}"
    exit 1
fi

# Start Mininet Topology
echo -e "${YELLOW}Starting Mininet Topology...${NC}"
echo -e "${YELLOW}Note: This requires sudo privileges${NC}"
echo ""
echo -e "${GREEN}System is running!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all components${NC}"
echo ""

# Start Mininet (this will block)
cd mininet
sudo python3 topology.py

# If we get here, Mininet exited
echo -e "${YELLOW}Mininet stopped${NC}"


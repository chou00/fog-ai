# Fog-Based AI Network Anomaly Detection System

**Production-quality simulation of a Fog Computing-based AI Network Anomaly Detection System using Mininet and SDN (Ryu Controller)**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Components](#components)
9. [Performance Metrics](#performance-metrics)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

---

## 🎯 Project Overview

This project implements a **fully simulated Fog-based AI Network Anomaly Detection System** that:

- Simulates realistic network topologies using **Mininet**
- Uses **SDN (Software-Defined Networking)** with **Ryu Controller** for dynamic traffic management
- Deploys **Fog Nodes** that perform local AI-powered anomaly detection
- Detects network anomalies in **real-time** with low latency
- Automatically mitigates threats via **dynamic SDN rules**

### Key Benefits

- **Low Latency**: Analysis at the edge (Fog level) reduces detection time
- **Scalable**: Modular architecture allows adding more Fog nodes
- **Intelligent**: Multiple AI models (Isolation Forest, Autoencoder, LSTM)
- **Automatic Mitigation**: SDN controller blocks suspicious traffic automatically

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SDN Controller (Ryu)                      │
│              - Flow Statistics Collection                    │
│              - Dynamic Rule Application                      │
│              - Communication with Fog Nodes                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼───┐      ┌───▼───┐      ┌───▼───┐
    │  S1   │──────│  S2   │──────│  S3   │
    │Switch │      │Switch │      │Switch │
    └───┬───┘      └───┬───┘      └───┬───┘
        │              │              │
   ┌────┼────┐    ┌────┼────┐    ┌────┼────┐
   │    │    │    │    │    │    │    │    │
  h1   h2  fog1  h3    │   h4  fog2
  │    │    │          │    │    │
  └────┴────┘          └────┴────┘
  Hosts              Fog Nodes
  (Traffic           (AI Analysis)
   Generators)
```

### Component Flow

1. **Traffic Generation**: Hosts generate normal and anomalous traffic
2. **Traffic Capture**: Fog nodes capture local network traffic
3. **Feature Extraction**: Extract network features (packet rate, flow duration, etc.)
4. **AI Analysis**: Anomaly detection models analyze features
5. **Decision Making**: Fog nodes decide if traffic is anomalous
6. **SDN Action**: Controller applies rules to block/limit suspicious traffic
7. **Logging**: All events logged in JSON format

---

## ✨ Features

### Core Features

- ✅ **Mininet Network Simulation**: Realistic network topology with multiple hosts and switches
- ✅ **SDN Control**: Ryu controller for dynamic flow management
- ✅ **Fog Computing**: Distributed analysis at network edge
- ✅ **AI Anomaly Detection**: Multiple ML models (Isolation Forest, Autoencoder, LSTM)
- ✅ **Real-time Analysis**: Low-latency detection and response
- ✅ **Automatic Mitigation**: SDN rules block suspicious traffic
- ✅ **Comprehensive Logging**: JSON-formatted logs for analysis

### Anomaly Detection Capabilities

- **Port Scanning**: Detects network reconnaissance attacks
- **TCP/UDP Floods**: Identifies DDoS attempts
- **Burst Traffic**: Detects sudden traffic spikes
- **Protocol Anomalies**: Identifies unusual protocol distributions
- **Flow Anomalies**: Detects abnormal connection patterns

---

## 📦 Prerequisites

### System Requirements

- **OS**: Kali Linux (recommended) or Ubuntu 20.04+
- **Python**: 3.10 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: Multi-core recommended

### Software Dependencies

```bash
# System packages (Kali Linux / Ubuntu)
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    tshark \
    wireshark-common \
    iperf3 \
    hping3 \
    nmap \
    net-tools
```

### Python Dependencies

All Python dependencies are listed in `requirements.txt` and will be installed automatically.

---

## 🚀 Installation

### 1. Clone or Download Project

```bash
cd fog-ai-anomaly-detection
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

**Note**: If you encounter issues with TensorFlow on some systems, you can skip it (Isolation Forest will work without it).

### 3. Verify Installation

```bash
# Check Mininet
sudo mn --version

# Check Ryu
ryu-manager --version

# Check Python packages
python3 -c "import numpy, sklearn, ryu; print('Dependencies OK')"
```

### 4. Set Permissions

```bash
chmod +x run.sh
chmod +x mininet/topology.py
chmod +x fog_node/*.py
```

---

## 💻 Usage

### Quick Start

```bash
# Run the complete system
./run.sh
```

### Manual Execution

#### Step 1: Start Ryu Controller

```bash
# Terminal 1
cd ryu_controller
ryu-manager controller.py --verbose
```

#### Step 2: Start Mininet Topology

```bash
# Terminal 2
cd mininet
sudo python3 topology.py
```

#### Step 3: Start Fog Agents

```bash
# Terminal 3 - Fog Node 1
cd fog_node
python3 fog_agent.py --node-id fog1 --simulated --model isolation_forest

# Terminal 4 - Fog Node 2
python3 fog_agent.py --node-id fog2 --simulated --model isolation_forest
```

### Generate Anomalous Traffic

In the Mininet CLI:

```bash
# Port scan
h1 nmap -sS -p 1-1000 10.0.0.2-4

# TCP flood
h1 hping3 -S -p 80 --flood 10.0.0.2

# UDP flood
h1 hping3 --udp -p 53 --flood 10.0.0.3

# Burst traffic
h1 for i in {1..100}; do iperf3 -c 10.0.0.2 -t 0.1 -b 100M; done
```

### View Logs

```bash
# Fog node detections
tail -f logs/fog_fog1_detections.jsonl

# Fog node alerts
tail -f logs/fog_fog1_alerts.jsonl

# Controller logs
tail -f logs/controller.log
```

---

## 📁 Project Structure

```
fog-ai-anomaly-detection/
│
├── mininet/
│   └── topology.py              # Mininet network topology
│
├── ryu_controller/
│   └── controller.py             # Ryu SDN controller
│
├── fog_node/
│   ├── traffic_capture.py        # Traffic capture module
│   ├── feature_extraction.py     # Feature extraction module
│   ├── anomaly_detection.py      # AI anomaly detection
│   └── fog_agent.py              # Main Fog agent orchestrator
│
├── datasets/                     # Training datasets (optional)
│
├── logs/                         # Log files
│   ├── controller.log
│   ├── fog_fog1_detections.jsonl
│   ├── fog_fog1_alerts.jsonl
│   └── fog_agent.log
│
├── models/                       # Trained AI models
│
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── run.sh                        # Execution script
```

---

## 🔧 Components

### 1. Mininet Topology (`mininet/topology.py`)

- Creates network with 4 hosts, 3 switches, 2 Fog nodes
- Configures links with bandwidth and delay
- Generates normal and anomalous traffic
- Provides CLI for network interaction

### 2. Ryu Controller (`ryu_controller/controller.py`)

- Collects flow statistics from switches
- Analyzes traffic patterns
- Applies dynamic OpenFlow rules
- Blocks suspicious flows automatically
- Logs all events

### 3. Traffic Capture (`fog_node/traffic_capture.py`)

- Captures network packets using Tshark
- Simulated mode for testing without Tshark
- Provides packet queue for analysis
- Real-time packet processing

### 4. Feature Extraction (`fog_node/feature_extraction.py`)

Extracts 21 network features:
- Packet count and rate
- Byte count and rate
- Protocol distribution (TCP/UDP/ICMP)
- Flow duration and statistics
- Connection patterns
- Packet size statistics

### 5. Anomaly Detection (`fog_node/anomaly_detection.py`)

Supports three models:
- **Isolation Forest**: Fast, unsupervised (default)
- **Autoencoder**: Deep learning for complex patterns
- **LSTM**: Time series analysis

### 6. Fog Agent (`fog_node/fog_agent.py`)

- Orchestrates all components
- Real-time analysis loop
- Logging and alerting
- Statistics collection

---

## 📊 Performance Metrics

### Metrics Collected

- **Detection Latency**: Time from anomaly to detection
- **False Positive Rate**: Percentage of false alarms
- **CPU Usage**: Resource consumption at Fog nodes
- **Throughput**: Packets analyzed per second
- **Accuracy**: Detection accuracy vs. ground truth

### Viewing Metrics

```bash
# Analyze logs
python3 -c "
import json
with open('logs/fog_fog1_detections.jsonl') as f:
    anomalies = sum(1 for line in f if json.loads(line)['is_anomaly'])
    print(f'Anomalies detected: {anomalies}')
"
```

---

## 🐛 Troubleshooting

### Issue: Mininet requires sudo

**Solution**: Run Mininet commands with `sudo`

```bash
sudo python3 topology.py
```

### Issue: Tshark permission denied

**Solution**: Add user to wireshark group

```bash
sudo usermod -a -G wireshark $USER
# Log out and log back in
```

### Issue: Ryu controller not connecting

**Solution**: Check controller is running and port 6633 is open

```bash
# Check if Ryu is running
ps aux | grep ryu-manager

# Check port
netstat -tuln | grep 6633
```

### Issue: Import errors

**Solution**: Ensure all dependencies are installed

```bash
pip3 install -r requirements.txt --upgrade
```

### Issue: Model training fails

**Solution**: Use Isolation Forest (doesn't require TensorFlow)

```bash
python3 fog_agent.py --model isolation_forest
```

---

## 📈 Advanced Usage

### Custom Topology

Edit `mininet/topology.py` to modify:
- Number of hosts/switches
- Link bandwidth and delay
- Network topology

### Custom Features

Edit `fog_node/feature_extraction.py` to add:
- New feature calculations
- Different time windows
- Custom statistics

### Model Training

Train on custom data:

```python
from fog_node.anomaly_detection import AnomalyDetector
import numpy as np

detector = AnomalyDetector(model_type='isolation_forest')
training_data = np.load('datasets/training_data.npy')
detector.train(training_data)
```

---

## 🎓 Academic & Professional Value

This project demonstrates:

- **Fog Computing** architecture
- **SDN** implementation
- **AI/ML** for network security
- **Real-time** system design
- **Production-quality** code

**Ideal for**:
- Network Security courses
- Cloud Computing projects
- AI/ML applications
- SDN research
- SOC (Security Operations Center) training

---

## 📝 License

This project is provided as-is for educational and research purposes.

---

## 👥 Contributing

Contributions welcome! Areas for improvement:

- Additional anomaly detection models
- Better visualization
- Docker containerization
- Integration with SIEM systems
- Performance optimizations

---

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in `logs/` directory
3. Verify all prerequisites are met

---

## 🎯 Future Enhancements

- [ ] Docker containerization
- [ ] Real-time dashboard
- [ ] SIEM integration
- [ ] Multi-Fog coordination
- [ ] Advanced visualization
- [ ] Export to CSV/Excel
- [ ] Performance benchmarking tools

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production-ready


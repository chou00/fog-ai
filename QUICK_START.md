# Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Run the System

```bash
chmod +x run.sh
./run.sh
```

### Step 3: Generate Anomalies (in Mininet CLI)

```bash
# Port scan
h1 nmap -sS -p 1-1000 10.0.0.2-4

# TCP flood
h1 hping3 -S -p 80 --flood 10.0.0.2

# UDP flood
h1 hping3 --udp -p 53 --flood 10.0.0.3
```

### Step 4: View Results

```bash
# Terminal 1: Fog detections
tail -f logs/fog_fog1_detections.jsonl

# Terminal 2: Alerts
tail -f logs/fog_fog1_alerts.jsonl

# Terminal 3: Controller logs
tail -f logs/controller.log
```

## 📋 Manual Execution (Step-by-Step)

### Terminal 1: Ryu Controller

```bash
cd ryu_controller
ryu-manager controller.py --verbose
```

### Terminal 2: Mininet

```bash
cd mininet
sudo python3 topology.py
```

### Terminal 3: Fog Agent 1

```bash
cd fog_node
python3 fog_agent.py --node-id fog1 --simulated --model isolation_forest
```

### Terminal 4: Fog Agent 2

```bash
cd fog_node
python3 fog_agent.py --node-id fog2 --simulated --model isolation_forest
```

## 🔍 Common Commands

### Test Components

```bash
python3 example_usage.py
```

### Check System Status

```bash
# Check if Ryu is running
ps aux | grep ryu-manager

# Check if Fog agents are running
ps aux | grep fog_agent

# Check Mininet
sudo mn --test pingall
```

### View Statistics

```bash
# Count anomalies
grep -c '"is_anomaly": true' logs/fog_fog1_detections.jsonl

# View last detection
tail -1 logs/fog_fog1_detections.jsonl | python3 -m json.tool
```

## ⚠️ Troubleshooting

### Permission Denied

```bash
sudo chmod +x run.sh setup.sh
```

### Tshark Permission Error

```bash
sudo usermod -a -G wireshark $USER
# Log out and log back in
```

### Port Already in Use

```bash
# Kill existing processes
pkill -f ryu-manager
pkill -f fog_agent
sudo pkill -f mininet
```

## 📊 Expected Output

### Normal Operation

```
[NORMAL] Score: 0.234 | Packets: 45 | Rate: 0.75 pkt/s
[NORMAL] Score: 0.189 | Packets: 52 | Rate: 0.87 pkt/s
```

### Anomaly Detected

```
[ANOMALY] Score: 0.856 | Packets: 15234 | Rate: 254.23 pkt/s
WARNING: ANOMALY DETECTED! Score: 0.856
```

## 🎯 Next Steps

1. Read `README.md` for detailed documentation
2. Review `PROJECT_SUMMARY.md` for architecture
3. Experiment with different anomaly types
4. Try different AI models (autoencoder, lstm)
5. Analyze logs for patterns

---

**Need Help?** Check `README.md` Troubleshooting section.


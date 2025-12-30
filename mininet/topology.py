#!/usr/bin/env python3
"""
Mininet Topology for Fog-based AI Network Anomaly Detection System

This script creates a network topology with:
- Multiple hosts (traffic generators)
- SDN switches (OpenFlow)
- Fog nodes (local analyzers)
- Connection to Ryu Controller
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import subprocess
import os


class FogTopology:
    """Fog Computing Network Topology"""
    
    def __init__(self):
        self.net = None
        self.controller_ip = '127.0.0.1'
        self.controller_port = 6633
        
    def create_topology(self):
        """Create the network topology"""
        info('*** Creating Fog-based Network Topology\n')
        
        # Create Mininet network
        self.net = Mininet(
            controller=None,  # We'll add remote controller
            switch=OVSSwitch,
            link=TCLink,
            autoStaticArp=True
        )
        
        # Add remote Ryu controller
        info('*** Adding Ryu Controller\n')
        controller = self.net.addController(
            'ryu',
            controller=RemoteController,
            ip=self.controller_ip,
            port=self.controller_port
        )
        
        # Create switches
        info('*** Creating SDN Switches\n')
        s1 = self.net.addSwitch('s1', cls=OVSSwitch, protocols='OpenFlow13')
        s2 = self.net.addSwitch('s2', cls=OVSSwitch, protocols='OpenFlow13')
        s3 = self.net.addSwitch('s3', cls=OVSSwitch, protocols='OpenFlow13')
        
        # Create hosts (traffic generators)
        info('*** Creating Hosts\n')
        h1 = self.net.addHost('h1', ip='10.0.0.1/24')
        h2 = self.net.addHost('h2', ip='10.0.0.2/24')
        h3 = self.net.addHost('h3', ip='10.0.0.3/24')
        h4 = self.net.addHost('h4', ip='10.0.0.4/24')
        
        # Create Fog nodes (with additional capabilities)
        info('*** Creating Fog Nodes\n')
        fog1 = self.net.addHost('fog1', ip='10.0.0.10/24')
        fog2 = self.net.addHost('fog2', ip='10.0.0.11/24')
        
        # Create links
        info('*** Creating Links\n')
        # Core switch connections
        self.net.addLink(s1, s2, bw=1000, delay='1ms')
        self.net.addLink(s2, s3, bw=1000, delay='1ms')
        
        # Host connections to switches
        self.net.addLink(h1, s1, bw=100, delay='2ms')
        self.net.addLink(h2, s1, bw=100, delay='2ms')
        self.net.addLink(h3, s2, bw=100, delay='2ms')
        self.net.addLink(h4, s3, bw=100, delay='2ms')
        
        # Fog node connections
        self.net.addLink(fog1, s1, bw=1000, delay='1ms')
        self.net.addLink(fog2, s3, bw=1000, delay='1ms')
        
        return self.net
    
    def start_network(self):
        """Start the network"""
        if not self.net:
            self.create_topology()
        
        info('*** Starting Network\n')
        self.net.start()
        
        # Wait for controller connection
        info('*** Waiting for Controller Connection\n')
        time.sleep(3)
        
        # Configure hosts
        self.configure_hosts()
        
        info('*** Network Started Successfully\n')
        return self.net
    
    def configure_hosts(self):
        """Configure host network settings"""
        info('*** Configuring Hosts\n')
        
        # Set default routes
        for host in self.net.hosts:
            if host.name.startswith('h') or host.name.startswith('fog'):
                host.cmd('route add default gw 10.0.0.254 2>/dev/null || true')
        
        # Enable IP forwarding on Fog nodes
        for host in self.net.hosts:
            if host.name.startswith('fog'):
                host.cmd('sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1')
    
    def generate_normal_traffic(self):
        """Generate normal background traffic"""
        info('*** Starting Normal Traffic Generation\n')
        
        h1, h2, h3, h4 = self.net.get('h1', 'h2', 'h3', 'h4')
        
        # Start iperf servers
        h2.cmd('iperf3 -s -D')
        h3.cmd('iperf3 -s -D')
        h4.cmd('iperf3 -s -D')
        
        time.sleep(1)
        
        # Start periodic traffic
        h1.cmd('while true; do iperf3 -c 10.0.0.2 -t 5 -b 10M; sleep 10; done &')
        h1.cmd('while true; do ping -c 5 10.0.0.3; sleep 15; done &')
        h2.cmd('while true; do curl -s http://10.0.0.3:80 > /dev/null 2>&1; sleep 20; done &')
        
        info('*** Normal Traffic Generation Started\n')
    
    def generate_anomalous_traffic(self, anomaly_type='scan'):
        """Generate anomalous traffic patterns
        
        Args:
            anomaly_type: Type of anomaly ('scan', 'flood', 'burst')
        """
        info(f'*** Generating Anomalous Traffic: {anomaly_type}\n')
        
        h1 = self.net.get('h1')
        
        if anomaly_type == 'scan':
            # Port scanning
            info('*** Starting Port Scan Attack\n')
            h1.cmd('nmap -sS -p 1-1000 10.0.0.2-4 > /dev/null 2>&1 &')
            
        elif anomaly_type == 'flood':
            # TCP/UDP flood
            info('*** Starting Flood Attack\n')
            h1.cmd('hping3 -S -p 80 --flood 10.0.0.2 > /dev/null 2>&1 &')
            h1.cmd('hping3 --udp -p 53 --flood 10.0.0.3 > /dev/null 2>&1 &')
            
        elif anomaly_type == 'burst':
            # Burst traffic
            info('*** Starting Burst Traffic\n')
            h1.cmd('for i in {1..100}; do iperf3 -c 10.0.0.2 -t 0.1 -b 100M; done &')
    
    def stop_network(self):
        """Stop the network"""
        if self.net:
            info('*** Stopping Network\n')
            self.net.stop()


def main():
    """Main execution function"""
    setLogLevel('info')
    
    topology = FogTopology()
    net = topology.start_network()
    
    try:
        # Start normal traffic
        topology.generate_normal_traffic()
        
        # Run CLI or keep network running
        info('*** Network is running. Use CLI to interact.\n')
        info('*** To generate anomalies, use: python3 generate_anomalies.py\n')
        CLI(net)
        
    except KeyboardInterrupt:
        info('\n*** Interrupted by user\n')
    finally:
        topology.stop_network()


if __name__ == '__main__':
    main()


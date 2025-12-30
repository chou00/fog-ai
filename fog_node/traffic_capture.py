#!/usr/bin/env python3
"""
Traffic Capture Module for Fog Nodes

Captures network traffic using Tshark/sFlow and provides
real-time packet data for analysis.
"""

import subprocess
import json
import threading
import queue
import logging
from datetime import datetime
import os


logger = logging.getLogger(__name__)


class TrafficCapture:
    """Capture network traffic for analysis"""
    
    def __init__(self, interface='any', capture_filter='', buffer_size=1000):
        """
        Initialize traffic capture
        
        Args:
            interface: Network interface to capture on
            capture_filter: BPF filter (e.g., 'tcp port 80')
            buffer_size: Size of capture buffer
        """
        self.interface = interface
        self.capture_filter = capture_filter
        self.buffer_size = buffer_size
        self.capture_queue = queue.Queue(maxsize=buffer_size)
        self.capture_thread = None
        self.is_capturing = False
        self.tshark_process = None
        
    def start_capture(self):
        """Start capturing traffic"""
        if self.is_capturing:
            logger.warning("Capture already running")
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info(f"Started traffic capture on interface {self.interface}")
    
    def stop_capture(self):
        """Stop capturing traffic"""
        self.is_capturing = False
        if self.tshark_process:
            try:
                self.tshark_process.terminate()
                self.tshark_process.wait(timeout=5)
            except:
                self.tshark_process.kill()
        logger.info("Stopped traffic capture")
    
    def _capture_loop(self):
        """Main capture loop"""
        # Tshark command for JSON output
        cmd = [
            'tshark',
            '-i', self.interface,
            '-T', 'json',
            '-l',  # Line buffered
            '-q'   # Quiet mode
        ]
        
        if self.capture_filter:
            cmd.extend(['-f', self.capture_filter])
        
        try:
            self.tshark_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True
            )
            
            buffer = ""
            for line in iter(self.tshark_process.stdout.readline, ''):
                if not self.is_capturing:
                    break
                
                buffer += line
                try:
                    # Try to parse JSON
                    packet_data = json.loads(buffer.strip())
                    self._process_packet(packet_data)
                    buffer = ""
                except json.JSONDecodeError:
                    # Incomplete JSON, continue reading
                    if len(buffer) > 10000:  # Prevent buffer overflow
                        buffer = ""
                    continue
                        
        except Exception as e:
            logger.error(f"Error in capture loop: {e}")
        finally:
            if self.tshark_process:
                self.tshark_process.terminate()
    
    def _process_packet(self, packet_data):
        """Process captured packet"""
        try:
            # Extract relevant fields from Tshark JSON
            packet_info = {
                'timestamp': datetime.now().isoformat(),
                'layers': {}
            }
            
            if '_source' in packet_data:
                layers = packet_data.get('_source', {}).get('layers', {})
                
                # Extract layer information
                for layer_name, layer_data in layers.items():
                    if isinstance(layer_data, dict):
                        packet_info['layers'][layer_name] = layer_data
            
            # Add to queue (non-blocking)
            try:
                self.capture_queue.put_nowait(packet_info)
            except queue.Full:
                # Queue full, drop oldest
                try:
                    self.capture_queue.get_nowait()
                    self.capture_queue.put_nowait(packet_info)
                except queue.Empty:
                    pass
                    
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
    
    def get_packets(self, timeout=1.0, max_packets=100):
        """
        Get captured packets
        
        Args:
            timeout: Timeout in seconds
            max_packets: Maximum number of packets to return
            
        Returns:
            List of packet dictionaries
        """
        packets = []
        end_time = datetime.now().timestamp() + timeout
        
        while len(packets) < max_packets and datetime.now().timestamp() < end_time:
            try:
                packet = self.capture_queue.get(timeout=0.1)
                packets.append(packet)
            except queue.Empty:
                break
        
        return packets
    
    def get_packet_count(self):
        """Get current queue size"""
        return self.capture_queue.qsize()


class SimulatedTrafficCapture:
    """Simulated traffic capture for testing without Tshark"""
    
    def __init__(self, interface='any', capture_filter='', buffer_size=1000):
        self.interface = interface
        self.capture_filter = capture_filter
        self.buffer_size = buffer_size
        self.capture_queue = queue.Queue(maxsize=buffer_size)
        self.capture_thread = None
        self.is_capturing = False
        self.packet_counter = 0
        
    def start_capture(self):
        """Start simulated capture"""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._simulate_capture, daemon=True)
        self.capture_thread.start()
        logger.info(f"Started simulated traffic capture on interface {self.interface}")
    
    def stop_capture(self):
        """Stop simulated capture"""
        self.is_capturing = False
        logger.info("Stopped simulated traffic capture")
    
    def _simulate_capture(self):
        """Simulate packet capture"""
        import random
        import time
        
        protocols = ['tcp', 'udp', 'icmp']
        ports = [80, 443, 22, 53, 3389]
        
        while self.is_capturing:
            # Simulate normal traffic
            packet = {
                'timestamp': datetime.now().isoformat(),
                'layers': {
                    'ip': {
                        'ip_src': f'10.0.0.{random.randint(1, 4)}',
                        'ip_dst': f'10.0.0.{random.randint(1, 4)}',
                        'ip_len': random.randint(64, 1500)
                    },
                    random.choice(protocols): {
                        f'{random.choice(protocols)}_srcport': random.choice(ports),
                        f'{random.choice(protocols)}_dstport': random.choice(ports)
                    }
                }
            }
            
            try:
                self.capture_queue.put_nowait(packet)
            except queue.Full:
                try:
                    self.capture_queue.get_nowait()
                    self.capture_queue.put_nowait(packet)
                except queue.Empty:
                    pass
            
            self.packet_counter += 1
            time.sleep(random.uniform(0.01, 0.1))  # Variable packet rate
    
    def get_packets(self, timeout=1.0, max_packets=100):
        """Get captured packets"""
        packets = []
        end_time = datetime.now().timestamp() + timeout
        
        while len(packets) < max_packets and datetime.now().timestamp() < end_time:
            try:
                packet = self.capture_queue.get(timeout=0.1)
                packets.append(packet)
            except queue.Empty:
                break
        
        return packets
    
    def get_packet_count(self):
        """Get current queue size"""
        return self.capture_queue.qsize()


#!/usr/bin/env python3
"""
Feature Extraction Module for Fog Nodes

Extracts network features from captured traffic for AI analysis:
- Packet rate
- Flow duration
- Protocol distribution
- Byte count
- Connection patterns
"""

import numpy as np
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from network traffic"""
    
    def __init__(self, window_size=60):
        """
        Initialize feature extractor
        
        Args:
            window_size: Time window in seconds for feature calculation
        """
        self.window_size = window_size
        self.packet_buffer = deque(maxlen=10000)
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0,
            'byte_count': 0,
            'start_time': None,
            'end_time': None,
            'protocol': None
        })
        
    def add_packets(self, packets):
        """Add packets for feature extraction"""
        for packet in packets:
            self.packet_buffer.append({
                'timestamp': datetime.fromisoformat(packet['timestamp']),
                'layers': packet.get('layers', {})
            })
    
    def extract_features(self):
        """
        Extract features from current packet buffer
        
        Returns:
            Dictionary of extracted features
        """
        if not self.packet_buffer:
            return self._get_default_features()
        
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_size)
        
        # Filter packets in time window
        window_packets = [
            p for p in self.packet_buffer
            if p['timestamp'] >= window_start
        ]
        
        if not window_packets:
            return self._get_default_features()
        
        features = {}
        
        # Basic statistics
        features['packet_count'] = len(window_packets)
        features['packet_rate'] = len(window_packets) / self.window_size
        
        # Protocol distribution
        protocol_counts = defaultdict(int)
        total_bytes = 0
        
        for packet in window_packets:
            layers = packet['layers']
            
            # Extract protocol
            if 'tcp' in layers:
                protocol_counts['tcp'] += 1
            elif 'udp' in layers:
                protocol_counts['udp'] += 1
            elif 'icmp' in layers:
                protocol_counts['icmp'] += 1
            else:
                protocol_counts['other'] += 1
            
            # Extract byte count
            if 'ip' in layers:
                ip_layer = layers['ip']
                if isinstance(ip_layer, dict):
                    ip_len = ip_layer.get('ip_len', {})
                    if isinstance(ip_len, list):
                        ip_len = ip_len[0] if ip_len else 0
                    elif isinstance(ip_len, (int, str)):
                        try:
                            total_bytes += int(ip_len)
                        except:
                            pass
        
        features['total_bytes'] = total_bytes
        features['byte_rate'] = total_bytes / self.window_size if self.window_size > 0 else 0
        
        # Protocol ratios
        total_protocol = sum(protocol_counts.values())
        if total_protocol > 0:
            features['tcp_ratio'] = protocol_counts['tcp'] / total_protocol
            features['udp_ratio'] = protocol_counts['udp'] / total_protocol
            features['icmp_ratio'] = protocol_counts['icmp'] / total_protocol
            features['other_ratio'] = protocol_counts['other'] / total_protocol
        else:
            features['tcp_ratio'] = 0
            features['udp_ratio'] = 0
            features['icmp_ratio'] = 0
            features['other_ratio'] = 0
        
        # Flow statistics
        flow_features = self._extract_flow_features(window_packets)
        features.update(flow_features)
        
        # Connection patterns
        connection_features = self._extract_connection_features(window_packets)
        features.update(connection_features)
        
        # Packet size statistics
        size_features = self._extract_size_features(window_packets)
        features.update(size_features)
        
        return features
    
    def _extract_flow_features(self, packets):
        """Extract flow-related features"""
        flows = defaultdict(lambda: {
            'packets': [],
            'start_time': None,
            'end_time': None
        })
        
        for packet in packets:
            layers = packet['layers']
            timestamp = packet['timestamp']
            
            # Create flow key
            src_ip = None
            dst_ip = None
            src_port = None
            dst_port = None
            
            if 'ip' in layers:
                ip_layer = layers['ip']
                if isinstance(ip_layer, dict):
                    src_ip = ip_layer.get('ip_src', [''])[0] if isinstance(ip_layer.get('ip_src'), list) else ip_layer.get('ip_src', '')
                    dst_ip = ip_layer.get('ip_dst', [''])[0] if isinstance(ip_layer.get('ip_dst'), list) else ip_layer.get('ip_dst', '')
            
            if 'tcp' in layers:
                tcp_layer = layers['tcp']
                if isinstance(tcp_layer, dict):
                    src_port = tcp_layer.get('tcp_srcport', [''])[0] if isinstance(tcp_layer.get('tcp_srcport'), list) else tcp_layer.get('tcp_srcport', '')
                    dst_port = tcp_layer.get('tcp_dstport', [''])[0] if isinstance(tcp_layer.get('tcp_dstport'), list) else tcp_layer.get('tcp_dstport', '')
            elif 'udp' in layers:
                udp_layer = layers['udp']
                if isinstance(udp_layer, dict):
                    src_port = udp_layer.get('udp_srcport', [''])[0] if isinstance(udp_layer.get('udp_srcport'), list) else udp_layer.get('udp_srcport', '')
                    dst_port = udp_layer.get('udp_dstport', [''])[0] if isinstance(udp_layer.get('udp_dstport'), list) else udp_layer.get('udp_dstport', '')
            
            if src_ip and dst_ip:
                flow_key = (src_ip, dst_ip, src_port, dst_port)
                flows[flow_key]['packets'].append(packet)
                if flows[flow_key]['start_time'] is None:
                    flows[flow_key]['start_time'] = timestamp
                flows[flow_key]['end_time'] = timestamp
        
        # Calculate flow statistics
        flow_durations = []
        flow_packet_counts = []
        
        for flow_key, flow_data in flows.items():
            if flow_data['start_time'] and flow_data['end_time']:
                duration = (flow_data['end_time'] - flow_data['start_time']).total_seconds()
                flow_durations.append(duration)
                flow_packet_counts.append(len(flow_data['packets']))
        
        features = {
            'num_flows': len(flows),
            'avg_flow_duration': np.mean(flow_durations) if flow_durations else 0,
            'max_flow_duration': np.max(flow_durations) if flow_durations else 0,
            'avg_packets_per_flow': np.mean(flow_packet_counts) if flow_packet_counts else 0,
            'max_packets_per_flow': np.max(flow_packet_counts) if flow_packet_counts else 0,
        }
        
        return features
    
    def _extract_connection_features(self, packets):
        """Extract connection pattern features"""
        unique_sources = set()
        unique_destinations = set()
        connections = set()
        
        for packet in packets:
            layers = packet['layers']
            
            if 'ip' in layers:
                ip_layer = layers['ip']
                if isinstance(ip_layer, dict):
                    src_ip = ip_layer.get('ip_src', [''])[0] if isinstance(ip_layer.get('ip_src'), list) else ip_layer.get('ip_src', '')
                    dst_ip = ip_layer.get('ip_dst', [''])[0] if isinstance(ip_layer.get('ip_dst'), list) else ip_layer.get('ip_dst', '')
                    
                    if src_ip:
                        unique_sources.add(src_ip)
                    if dst_ip:
                        unique_destinations.add(dst_ip)
                    if src_ip and dst_ip:
                        connections.add((src_ip, dst_ip))
        
        features = {
            'unique_sources': len(unique_sources),
            'unique_destinations': len(unique_destinations),
            'unique_connections': len(connections),
            'connection_diversity': len(connections) / max(len(unique_sources) * len(unique_destinations), 1)
        }
        
        return features
    
    def _extract_size_features(self, packets):
        """Extract packet size features"""
        packet_sizes = []
        
        for packet in packets:
            layers = packet['layers']
            if 'ip' in layers:
                ip_layer = layers['ip']
                if isinstance(ip_layer, dict):
                    ip_len = ip_layer.get('ip_len', {})
                    if isinstance(ip_len, list):
                        ip_len = ip_len[0] if ip_len else 0
                    elif isinstance(ip_len, (int, str)):
                        try:
                            packet_sizes.append(int(ip_len))
                        except:
                            pass
        
        if packet_sizes:
            features = {
                'avg_packet_size': np.mean(packet_sizes),
                'min_packet_size': np.min(packet_sizes),
                'max_packet_size': np.max(packet_sizes),
                'std_packet_size': np.std(packet_sizes),
            }
        else:
            features = {
                'avg_packet_size': 0,
                'min_packet_size': 0,
                'max_packet_size': 0,
                'std_packet_size': 0,
            }
        
        return features
    
    def _get_default_features(self):
        """Return default feature values when no data available"""
        return {
            'packet_count': 0,
            'packet_rate': 0,
            'total_bytes': 0,
            'byte_rate': 0,
            'tcp_ratio': 0,
            'udp_ratio': 0,
            'icmp_ratio': 0,
            'other_ratio': 0,
            'num_flows': 0,
            'avg_flow_duration': 0,
            'max_flow_duration': 0,
            'avg_packets_per_flow': 0,
            'max_packets_per_flow': 0,
            'unique_sources': 0,
            'unique_destinations': 0,
            'unique_connections': 0,
            'connection_diversity': 0,
            'avg_packet_size': 0,
            'min_packet_size': 0,
            'max_packet_size': 0,
            'std_packet_size': 0,
        }
    
    def get_feature_vector(self):
        """
        Get feature vector as numpy array for ML models
        
        Returns:
            numpy array of features
        """
        features = self.extract_features()
        
        # Order features consistently
        feature_order = [
            'packet_count',
            'packet_rate',
            'total_bytes',
            'byte_rate',
            'tcp_ratio',
            'udp_ratio',
            'icmp_ratio',
            'other_ratio',
            'num_flows',
            'avg_flow_duration',
            'max_flow_duration',
            'avg_packets_per_flow',
            'max_packets_per_flow',
            'unique_sources',
            'unique_destinations',
            'unique_connections',
            'connection_diversity',
            'avg_packet_size',
            'min_packet_size',
            'max_packet_size',
            'std_packet_size',
        ]
        
        return np.array([features.get(key, 0) for key in feature_order])


#!/usr/bin/env python3
"""
Fog Agent - Main orchestrator for Fog Node

Coordinates:
- Traffic capture
- Feature extraction
- Anomaly detection
- Communication with SDN controller
- Logging and reporting
"""

import time
import threading
import logging
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fog_node.traffic_capture import TrafficCapture, SimulatedTrafficCapture
from fog_node.feature_extraction import FeatureExtractor
from fog_node.anomaly_detection import AnomalyDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fog_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FogAgent:
    """Main Fog Node Agent"""
    
    def __init__(self, node_id='fog1', interface='any', use_simulated_capture=True, model_type='isolation_forest'):
        """
        Initialize Fog Agent
        
        Args:
            node_id: Unique identifier for this Fog node
            interface: Network interface to monitor
            use_simulated_capture: Use simulated capture instead of Tshark
            model_type: Type of anomaly detection model
        """
        self.node_id = node_id
        self.interface = interface
        self.use_simulated_capture = use_simulated_capture
        self.model_type = model_type
        
        # Initialize components
        if use_simulated_capture:
            self.capture = SimulatedTrafficCapture(interface=interface)
        else:
            self.capture = TrafficCapture(interface=interface)
        
        self.feature_extractor = FeatureExtractor(window_size=60)
        self.anomaly_detector = AnomalyDetector(model_type=model_type)
        
        # State
        self.is_running = False
        self.analysis_thread = None
        self.detection_count = 0
        self.normal_count = 0
        
        # Create directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        # Load or train model
        if not self.anomaly_detector.load_model():
            logger.info("No pre-trained model found, generating training data...")
            training_data = self.anomaly_detector.generate_training_data()
            self.anomaly_detector.train(training_data)
        
        logger.info(f"Fog Agent {node_id} initialized")
    
    def start(self):
        """Start the Fog agent"""
        if self.is_running:
            logger.warning("Agent already running")
            return
        
        self.is_running = True
        
        # Start traffic capture
        self.capture.start_capture()
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        logger.info(f"Fog Agent {self.node_id} started")
    
    def stop(self):
        """Stop the Fog agent"""
        self.is_running = False
        self.capture.stop_capture()
        logger.info(f"Fog Agent {self.node_id} stopped")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        logger.info("Analysis loop started")
        
        while self.is_running:
            try:
                # Get captured packets
                packets = self.capture.get_packets(timeout=5.0, max_packets=1000)
                
                if packets:
                    # Add packets to feature extractor
                    self.feature_extractor.add_packets(packets)
                    
                    # Extract features
                    features = self.feature_extractor.extract_features()
                    feature_vector = self.feature_extractor.get_feature_vector()
                    
                    # Detect anomalies
                    if feature_vector is not None and len(feature_vector) > 0:
                        prediction = self.anomaly_detector.predict(feature_vector.reshape(1, -1))
                        score = self.anomaly_detector.predict_proba(feature_vector.reshape(1, -1))
                        
                        is_anomaly = prediction[0] == -1
                        anomaly_score = score[0]
                        
                        # Log result
                        self._log_detection(features, is_anomaly, anomaly_score)
                        
                        # Take action if anomaly detected
                        if is_anomaly and anomaly_score > 0.7:  # Threshold
                            self._handle_anomaly(features, anomaly_score)
                            self.detection_count += 1
                        else:
                            self.normal_count += 1
                
                # Sleep before next iteration
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}", exc_info=True)
                time.sleep(5)
    
    def _log_detection(self, features, is_anomaly, anomaly_score):
        """Log detection result"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'node_id': self.node_id,
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': float(anomaly_score),
            'features': features,
            'packet_count': features.get('packet_count', 0),
            'packet_rate': features.get('packet_rate', 0),
            'byte_rate': features.get('byte_rate', 0)
        }
        
        log_file = f'logs/fog_{self.node_id}_detections.jsonl'
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing log: {e}")
        
        # Console output
        status = "ANOMALY" if is_anomaly else "NORMAL"
        logger.info(f"[{status}] Score: {anomaly_score:.3f} | "
                   f"Packets: {features.get('packet_count', 0)} | "
                   f"Rate: {features.get('packet_rate', 0):.2f} pkt/s")
    
    def _handle_anomaly(self, features, anomaly_score):
        """Handle detected anomaly"""
        logger.warning(f"ANOMALY DETECTED! Score: {anomaly_score:.3f}")
        logger.warning(f"Features: {json.dumps(features, indent=2)}")
        
        # In a real implementation, this would:
        # 1. Send alert to SDN controller
        # 2. Request flow blocking
        # 3. Notify other Fog nodes
        # 4. Send to central SIEM
        
        # For simulation, we'll just log it
        alert = {
            'timestamp': datetime.now().isoformat(),
            'node_id': self.node_id,
            'severity': 'HIGH' if anomaly_score > 0.8 else 'MEDIUM',
            'anomaly_score': anomaly_score,
            'features': features,
            'action': 'logged'  # In production: 'blocked', 'rate_limited', etc.
        }
        
        alert_file = f'logs/fog_{self.node_id}_alerts.jsonl'
        try:
            with open(alert_file, 'a') as f:
                f.write(json.dumps(alert) + '\n')
        except Exception as e:
            logger.error(f"Error writing alert: {e}")
    
    def get_statistics(self):
        """Get current statistics"""
        return {
            'node_id': self.node_id,
            'is_running': self.is_running,
            'detection_count': self.detection_count,
            'normal_count': self.normal_count,
            'total_analyzed': self.detection_count + self.normal_count,
            'anomaly_rate': self.detection_count / max(self.detection_count + self.normal_count, 1),
            'packet_queue_size': self.capture.get_packet_count()
        }


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fog Agent for Anomaly Detection')
    parser.add_argument('--node-id', default='fog1', help='Fog node identifier')
    parser.add_argument('--interface', default='any', help='Network interface')
    parser.add_argument('--simulated', action='store_true', help='Use simulated capture')
    parser.add_argument('--model', default='isolation_forest', 
                       choices=['isolation_forest', 'autoencoder', 'lstm'],
                       help='Anomaly detection model type')
    
    args = parser.parse_args()
    
    # Create and start agent
    agent = FogAgent(
        node_id=args.node_id,
        interface=args.interface,
        use_simulated_capture=args.simulated,
        model_type=args.model
    )
    
    try:
        agent.start()
        
        # Keep running
        while True:
            time.sleep(10)
            stats = agent.get_statistics()
            logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        agent.stop()


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Example Usage Script for Fog-based AI Network Anomaly Detection

This script demonstrates how to use the system components individually.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fog_node.fog_agent import FogAgent
from fog_node.feature_extraction import FeatureExtractor
from fog_node.anomaly_detection import AnomalyDetector
import numpy as np


def example_anomaly_detection():
    """Example: Train and use anomaly detection model"""
    print("=" * 60)
    print("Example 1: Anomaly Detection Model")
    print("=" * 60)
    
    # Create detector
    detector = AnomalyDetector(model_type='isolation_forest')
    
    # Generate training data
    print("Generating training data...")
    training_data = detector.generate_training_data(n_samples=1000)
    print(f"Generated {len(training_data)} training samples")
    
    # Train model
    print("Training model...")
    detector.train(training_data)
    print("Model trained successfully!")
    
    # Test with sample data
    print("\nTesting with sample data...")
    test_data = np.random.normal(0, 1, (10, 21))
    test_data[0, 0] = 10000  # Anomalous packet count
    test_data[0, 1] = 1000   # Anomalous packet rate
    
    predictions = detector.predict(test_data)
    scores = detector.predict_proba(test_data)
    
    for i, (pred, score) in enumerate(zip(predictions, scores)):
        status = "ANOMALY" if pred == -1 else "NORMAL"
        print(f"Sample {i+1}: {status} (score: {score:.3f})")
    
    print("\n" + "=" * 60 + "\n")


def example_feature_extraction():
    """Example: Extract features from simulated packets"""
    print("=" * 60)
    print("Example 2: Feature Extraction")
    print("=" * 60)
    
    extractor = FeatureExtractor(window_size=60)
    
    # Simulate some packets
    print("Simulating packets...")
    from fog_node.traffic_capture import SimulatedTrafficCapture
    
    capture = SimulatedTrafficCapture()
    capture.start_capture()
    
    # Wait for packets
    time.sleep(2)
    packets = capture.get_packets(timeout=1.0, max_packets=100)
    print(f"Captured {len(packets)} packets")
    
    # Extract features
    extractor.add_packets(packets)
    features = extractor.extract_features()
    
    print("\nExtracted Features:")
    print("-" * 40)
    for key, value in features.items():
        if isinstance(value, float):
            print(f"{key:25s}: {value:10.2f}")
        else:
            print(f"{key:25s}: {value:10}")
    
    capture.stop_capture()
    print("\n" + "=" * 60 + "\n")


def example_fog_agent():
    """Example: Run Fog Agent for a short time"""
    print("=" * 60)
    print("Example 3: Fog Agent")
    print("=" * 60)
    
    print("Starting Fog Agent (will run for 30 seconds)...")
    print("Press Ctrl+C to stop early\n")
    
    agent = FogAgent(
        node_id='example_fog',
        use_simulated_capture=True,
        model_type='isolation_forest'
    )
    
    try:
        agent.start()
        
        # Run for 30 seconds
        for i in range(6):
            time.sleep(5)
            stats = agent.get_statistics()
            print(f"\n[{i*5}s] Statistics:")
            print(f"  Packets in queue: {stats['packet_queue_size']}")
            print(f"  Anomalies detected: {stats['detection_count']}")
            print(f"  Normal traffic: {stats['normal_count']}")
            print(f"  Anomaly rate: {stats['anomaly_rate']:.2%}")
        
        agent.stop()
        print("\nFog Agent stopped")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        agent.stop()
    
    print("\n" + "=" * 60 + "\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Fog-based AI Network Anomaly Detection - Examples")
    print("=" * 60 + "\n")
    
    try:
        # Example 1: Anomaly Detection
        example_anomaly_detection()
        
        # Example 2: Feature Extraction
        example_feature_extraction()
        
        # Example 3: Fog Agent
        response = input("Run Fog Agent example? (y/n): ")
        if response.lower() == 'y':
            example_fog_agent()
        
        print("All examples completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()


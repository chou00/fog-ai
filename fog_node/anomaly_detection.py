#!/usr/bin/env python3
"""
AI Anomaly Detection Module for Fog Nodes

Implements multiple anomaly detection models:
- Isolation Forest (baseline)
- Autoencoder (deep learning)
- LSTM (time series)
"""

import numpy as np
import pickle
import os
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Base class for anomaly detection"""
    
    def __init__(self, model_type='isolation_forest'):
        """
        Initialize anomaly detector
        
        Args:
            model_type: Type of model ('isolation_forest', 'autoencoder', 'lstm')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = f'models/{model_type}_model.pkl'
        self.scaler_path = f'models/{model_type}_scaler.pkl'
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
    
    def train(self, X_train):
        """
        Train the anomaly detection model
        
        Args:
            X_train: Training data (numpy array)
        """
        logger.info(f"Training {self.model_type} model on {len(X_train)} samples")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train model based on type
        if self.model_type == 'isolation_forest':
            self.model = IsolationForest(
                contamination=0.1,  # Expected proportion of anomalies
                random_state=42,
                n_estimators=100
            )
            self.model.fit(X_scaled)
            
        elif self.model_type == 'autoencoder':
            self._train_autoencoder(X_scaled)
            
        elif self.model_type == 'lstm':
            self._train_lstm(X_scaled)
        
        self.is_trained = True
        self._save_model()
        logger.info(f"Model training completed")
    
    def predict(self, X):
        """
        Predict anomalies
        
        Args:
            X: Feature vectors (numpy array)
            
        Returns:
            Predictions: -1 for anomaly, 1 for normal
        """
        if not self.is_trained:
            logger.error("Model not trained yet")
            return np.ones(len(X))
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        if self.model_type == 'isolation_forest':
            predictions = self.model.predict(X_scaled)
        elif self.model_type == 'autoencoder':
            predictions = self._predict_autoencoder(X_scaled)
        elif self.model_type == 'lstm':
            predictions = self._predict_lstm(X_scaled)
        else:
            predictions = np.ones(len(X))
        
        return predictions
    
    def predict_proba(self, X):
        """
        Get anomaly scores (higher = more anomalous)
        
        Args:
            X: Feature vectors (numpy array)
            
        Returns:
            Anomaly scores
        """
        if not self.is_trained:
            return np.zeros(len(X))
        
        X_scaled = self.scaler.transform(X)
        
        if self.model_type == 'isolation_forest':
            scores = -self.model.score_samples(X_scaled)  # Negative because lower score = more anomalous
        elif self.model_type == 'autoencoder':
            scores = self._score_autoencoder(X_scaled)
        elif self.model_type == 'lstm':
            scores = self._score_lstm(X_scaled)
        else:
            scores = np.zeros(len(X))
        
        # Normalize scores to [0, 1]
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
        
        return scores
    
    def _train_autoencoder(self, X_scaled):
        """Train autoencoder model"""
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras import layers
            
            input_dim = X_scaled.shape[1]
            
            # Build autoencoder
            input_layer = keras.Input(shape=(input_dim,))
            encoded = layers.Dense(64, activation='relu')(input_layer)
            encoded = layers.Dense(32, activation='relu')(encoded)
            decoded = layers.Dense(64, activation='relu')(encoded)
            decoded = layers.Dense(input_dim, activation='linear')(decoded)
            
            autoencoder = keras.Model(input_layer, decoded)
            autoencoder.compile(optimizer='adam', loss='mse')
            
            # Train
            autoencoder.fit(
                X_scaled, X_scaled,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            self.model = autoencoder
            logger.info("Autoencoder trained successfully")
            
        except ImportError:
            logger.warning("TensorFlow not available, falling back to Isolation Forest")
            self.model_type = 'isolation_forest'
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.model.fit(X_scaled)
    
    def _train_lstm(self, X_scaled):
        """Train LSTM model"""
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras import layers
            
            # Reshape for LSTM (samples, timesteps, features)
            # For single feature vector, we'll use sequence length of 1
            X_reshaped = X_scaled.reshape(X_scaled.shape[0], 1, X_scaled.shape[1])
            
            # Build LSTM autoencoder
            input_layer = keras.Input(shape=(1, X_scaled.shape[1]))
            lstm1 = layers.LSTM(32, return_sequences=True)(input_layer)
            lstm2 = layers.LSTM(16, return_sequences=False)(lstm1)
            repeat = layers.RepeatVector(1)(lstm2)
            lstm3 = layers.LSTM(16, return_sequences=True)(repeat)
            lstm4 = layers.LSTM(32, return_sequences=True)(lstm3)
            output = layers.TimeDistributed(layers.Dense(X_scaled.shape[1]))(lstm4)
            
            lstm_autoencoder = keras.Model(input_layer, output)
            lstm_autoencoder.compile(optimizer='adam', loss='mse')
            
            # Train
            lstm_autoencoder.fit(
                X_reshaped, X_reshaped,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            self.model = lstm_autoencoder
            logger.info("LSTM model trained successfully")
            
        except ImportError:
            logger.warning("TensorFlow not available, falling back to Isolation Forest")
            self.model_type = 'isolation_forest'
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.model.fit(X_scaled)
    
    def _predict_autoencoder(self, X_scaled):
        """Predict using autoencoder"""
        if self.model is None:
            return np.ones(len(X_scaled))
        
        try:
            reconstructed = self.model.predict(X_scaled, verbose=0)
            mse = np.mean((X_scaled - reconstructed) ** 2, axis=1)
            threshold = np.percentile(mse, 90)  # 90th percentile as threshold
            predictions = np.where(mse > threshold, -1, 1)
            return predictions
        except:
            return np.ones(len(X_scaled))
    
    def _predict_lstm(self, X_scaled):
        """Predict using LSTM"""
        if self.model is None:
            return np.ones(len(X_scaled))
        
        try:
            X_reshaped = X_scaled.reshape(X_scaled.shape[0], 1, X_scaled.shape[1])
            reconstructed = self.model.predict(X_reshaped, verbose=0)
            mse = np.mean((X_reshaped - reconstructed) ** 2, axis=(1, 2))
            threshold = np.percentile(mse, 90)
            predictions = np.where(mse > threshold, -1, 1)
            return predictions
        except:
            return np.ones(len(X_scaled))
    
    def _score_autoencoder(self, X_scaled):
        """Get anomaly scores from autoencoder"""
        if self.model is None:
            return np.zeros(len(X_scaled))
        
        try:
            reconstructed = self.model.predict(X_scaled, verbose=0)
            mse = np.mean((X_scaled - reconstructed) ** 2, axis=1)
            return mse
        except:
            return np.zeros(len(X_scaled))
    
    def _score_lstm(self, X_scaled):
        """Get anomaly scores from LSTM"""
        if self.model is None:
            return np.zeros(len(X_scaled))
        
        try:
            X_reshaped = X_scaled.reshape(X_scaled.shape[0], 1, X_scaled.shape[1])
            reconstructed = self.model.predict(X_reshaped, verbose=0)
            mse = np.mean((X_reshaped - reconstructed) ** 2, axis=(1, 2))
            return mse
        except:
            return np.zeros(len(X_scaled))
    
    def _save_model(self):
        """Save trained model"""
        try:
            if self.model_type == 'isolation_forest':
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.model, f)
                with open(self.scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
            # For TensorFlow models, save differently
            elif self.model is not None:
                try:
                    self.model.save(f'models/{self.model_type}_model.h5')
                    with open(self.scaler_path, 'wb') as f:
                        pickle.dump(self.scaler, f)
                except:
                    pass
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load trained model"""
        try:
            if self.model_type == 'isolation_forest':
                if os.path.exists(self.model_path):
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    with open(self.scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                    self.is_trained = True
                    logger.info("Model loaded successfully")
                    return True
            else:
                # Try loading TensorFlow model
                try:
                    import tensorflow as tf
                    model_path = f'models/{self.model_type}_model.h5'
                    if os.path.exists(model_path):
                        self.model = tf.keras.models.load_model(model_path)
                        with open(self.scaler_path, 'rb') as f:
                            self.scaler = pickle.load(f)
                        self.is_trained = True
                        logger.info("Model loaded successfully")
                        return True
                except:
                    pass
        except Exception as e:
            logger.error(f"Error loading model: {e}")
        
        return False
    
    def generate_training_data(self, n_samples=1000, n_features=21):
        """
        Generate synthetic training data for initial model training
        
        Args:
            n_samples: Number of training samples
            n_features: Number of features
            
        Returns:
            numpy array of training data
        """
        logger.info(f"Generating {n_samples} synthetic training samples")
        
        # Generate normal traffic patterns
        np.random.seed(42)
        
        # Normal traffic characteristics
        data = np.random.normal(0, 1, (n_samples, n_features))
        
        # Add some realistic patterns
        data[:, 0] = np.abs(data[:, 0]) * 100  # packet_count
        data[:, 1] = np.abs(data[:, 1]) * 10   # packet_rate
        data[:, 2] = np.abs(data[:, 2]) * 10000  # total_bytes
        
        return data


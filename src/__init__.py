"""
Stock Price Prediction using LSTM Neural Networks

Modular implementation of LSTM-based stock price forecasting.
Loads AAPL CSV data, trains model, and generates predictions.

Modules:
- config: Centralized hyperparameter configuration
- data_loader: CSV loading and validation
- preprocessor: Data normalization and sequence generation
- model: LSTM architecture definition
- trainer: Model training logic
- evaluator: Metrics computation
- visualizer: Plotting functions
- utils: Utility functions (seeds, environment setup)
"""

__version__ = "1.0.0"

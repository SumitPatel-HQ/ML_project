"""
Configuration for Stock Price Prediction Pipeline

Centralizes all hyperparameters, paths, and settings.
Modify values here to experiment with different configurations.
"""

# ==============================================================================
# DATA PATHS
# ==============================================================================

DATA_PATH = "data/AAPL.csv"
OUTPUT_DIR = "output"

# ==============================================================================
# DATA COLUMNS
# ==============================================================================

DATE_COLUMN = "Date"
TARGET_COLUMN = "Close"

# ==============================================================================
# PREPROCESSING
# ==============================================================================

SEQUENCE_LENGTH = 60  # Days to look back for LSTM input
TRAIN_SPLIT = 0.8  # 80% train, 20% test
NORMALIZE_RANGE = (0, 1)  # MinMaxScaler range

# ==============================================================================
# MODEL ARCHITECTURE
# ==============================================================================

LSTM_UNITS = 64  # Units per LSTM layer
LSTM_LAYERS = 2  # Number of stacked LSTM layers
DROPOUT_RATE = 0.2  # Dropout for regularization
DENSE_UNITS = 32  # Units in Dense layer
LEARNING_RATE = 0.001  # Adam optimizer learning rate

# ==============================================================================
# TRAINING
# ==============================================================================

BATCH_SIZE = 32
EPOCHS = 100
VALIDATION_SPLIT = 0.1  # 10% of training data
EARLY_STOPPING_PATIENCE = 10  # Stop after N epochs without improvement
EARLY_STOPPING_MONITOR = "val_loss"

# ==============================================================================
# VISUALIZATION
# ==============================================================================

RAW_PLOT_FILE = "raw_price.png"
PREDICTION_PLOT_FILE = "AAPL_prediction.png"
PLOT_DPI = 100
PLOT_FIGSIZE = (12, 6)

# ==============================================================================
# MODEL PERSISTENCE
# ==============================================================================

MODEL_FILE = "best_model.h5"

# ==============================================================================
# REPRODUCIBILITY
# ==============================================================================

RANDOM_SEED = 42

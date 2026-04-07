"""
Utility functions for pipeline setup and reproducibility.
"""

import os
import random
import numpy as np

STATUS_PREFIX = "[OK]"

try:
    import tensorflow as tf
except ModuleNotFoundError:
    tf = None

from src.config import RANDOM_SEED, OUTPUT_DIR


def set_random_seeds(seed=RANDOM_SEED):
    """
    Set random seeds for reproducibility across libraries.

    Sets seeds for:
    - Python's built-in random module
    - NumPy
    - TensorFlow

    Args:
        seed (int): Random seed value. Default from config.RANDOM_SEED.

    Note:
        Some GPU operations may still be non-deterministic even with seeds set.
        For full reproducibility, set PYTHONHASHSEED environment variable.
    """
    random.seed(seed)
    np.random.seed(seed)
    if tf is not None:
        tf.random.set_seed(seed)
    print(f"{STATUS_PREFIX} Random seeds set to {seed}")


def setup_environment():
    """
    Initialize environment for pipeline execution.

    Creates output directory if it doesn't exist.
    Sets random seeds for reproducibility.
    """
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"{STATUS_PREFIX} Output directory: {OUTPUT_DIR}/")

    # Set random seeds
    set_random_seeds()

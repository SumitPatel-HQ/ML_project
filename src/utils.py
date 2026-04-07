"""Utility helpers for environment setup and reproducibility."""

from __future__ import annotations

import os
import random

import numpy as np

from src.config import OUTPUT_DIR, RANDOM_SEED

try:
    import tensorflow as tf
except (
    ModuleNotFoundError
):  # pragma: no cover - optional in lightweight test environments
    tf = None


def set_random_seeds(seed=RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    if tf is not None:
        tf.random.set_seed(seed)


def setup_environment():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    set_random_seeds()

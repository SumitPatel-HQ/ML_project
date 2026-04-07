"""Model-building helpers for the Phase 3 stacked LSTM architecture."""

from __future__ import annotations

import importlib
from io import StringIO

from src.config import (
    DENSE_UNITS,
    DROPOUT_RATE,
    LEARNING_RATE,
    LSTM_UNITS,
    SEQUENCE_LENGTH,
)


TF_REQUIRED_ERROR = "TensorFlow is required to build or train the Phase 3 LSTM model."


def _load_keras_runtime():
    try:
        layers = importlib.import_module("tensorflow.keras.layers")
        models = importlib.import_module("tensorflow.keras.models")
        optimizers = importlib.import_module("tensorflow.keras.optimizers")
    except ModuleNotFoundError as exc:
        raise RuntimeError(TF_REQUIRED_ERROR) from exc

    return models.Sequential, layers.LSTM, layers.Dropout, layers.Dense, optimizers.Adam


def _build_config(cfg=None):
    overrides = cfg or {}
    return {
        "sequence_length": overrides.get("sequence_length", SEQUENCE_LENGTH),
        "lstm_units": overrides.get("lstm_units", LSTM_UNITS),
        "dropout_rate": overrides.get("dropout_rate", DROPOUT_RATE),
        "dense_units": overrides.get("dense_units", DENSE_UNITS),
        "learning_rate": overrides.get("learning_rate", LEARNING_RATE),
    }


def build_model(input_shape=None, cfg=None):
    Sequential, LSTM, Dropout, Dense, Adam = _load_keras_runtime()
    config = _build_config(cfg)
    resolved_input_shape = input_shape or (config["sequence_length"], 1)

    model = Sequential(
        [
            LSTM(
                config["lstm_units"],
                return_sequences=True,
                input_shape=resolved_input_shape,
            ),
            Dropout(config["dropout_rate"]),
            LSTM(config["lstm_units"], return_sequences=False),
            Dropout(config["dropout_rate"]),
            Dense(config["dense_units"], activation="relu"),
            Dense(1),
        ]
    )
    model.compile(
        optimizer=Adam(learning_rate=config["learning_rate"]),
        loss="mean_squared_error",
    )
    return model


def format_model_summary(model):
    buffer = StringIO()
    model.summary(print_fn=lambda line: buffer.write(f"{line}\n"))
    return buffer.getvalue().strip()

"""Preprocessing utilities for leakage-safe LSTM sequence generation."""

from __future__ import annotations

import numpy as np
from sklearn.preprocessing import MinMaxScaler

from src.config import NORMALIZE_RANGE, SEQUENCE_LENGTH, TARGET_COLUMN, TRAIN_SPLIT


def _build_config(cfg=None):
    overrides = cfg or {}
    return {
        "feature_col": overrides.get("feature_col", TARGET_COLUMN),
        "train_split": overrides.get("train_split", TRAIN_SPLIT),
        "window_size": overrides.get("window_size", SEQUENCE_LENGTH),
        "normalize_range": overrides.get("normalize_range", NORMALIZE_RANGE),
    }


def _validate_inputs(df, feature_col, train_split, window_size):
    if feature_col not in df.columns:
        raise ValueError(f"Missing required feature column: {feature_col}")
    if df[feature_col].isna().any():
        raise ValueError(f"{feature_col} contains missing values")
    if not 0 < train_split < 1:
        raise ValueError("train_split must be between 0 and 1")
    if window_size < 1:
        raise ValueError("window_size must be at least 1")

    row_count = len(df)
    split_index = int(row_count * train_split)
    train_rows = split_index
    test_rows = row_count - split_index

    if train_rows <= window_size or test_rows < 1:
        raise ValueError("Dataset is too short to create train/test sequences")


def _create_sequences(
    data: np.ndarray, window_size: int
) -> tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for index in range(window_size, len(data)):
        X.append(data[index - window_size : index, 0])
        y.append(data[index, 0])

    if not X or not y:
        raise ValueError("Unable to create enough rows for at least one sequence")

    return np.array(X), np.array(y)


def _coerce_shape(name: str, X: np.ndarray, y: np.ndarray, window_size: int):
    try:
        X = X.reshape(-1, window_size, 1)
    except ValueError as exc:
        raise ValueError(f"Invalid {name} feature tensor shape") from exc

    if y.ndim != 1:
        raise ValueError(f"Invalid {name} target shape")

    if X.shape[0] != y.shape[0]:
        raise ValueError(f"Inconsistent {name} sequence and target counts")

    return X, y


def preprocess(df, cfg=None):
    config = _build_config(cfg)
    feature_col = config["feature_col"]
    train_split = config["train_split"]
    window_size = config["window_size"]
    normalize_range = config["normalize_range"]

    _validate_inputs(df, feature_col, train_split, window_size)

    data = df[[feature_col]].values
    split_index = int(len(data) * train_split)
    train_raw = data[:split_index]
    test_raw = data[split_index:]

    scaler = MinMaxScaler(feature_range=normalize_range)
    train_scaled = scaler.fit_transform(train_raw)
    test_input = np.concatenate([train_raw[-window_size:], test_raw])
    test_scaled = scaler.transform(test_input)

    X_train, y_train = _create_sequences(train_scaled, window_size)
    X_test, y_test = _create_sequences(test_scaled, window_size)

    X_train, y_train = _coerce_shape("train", X_train, y_train, window_size)
    X_test, y_test = _coerce_shape("test", X_test, y_test, window_size)

    metadata = {
        "feature_name": feature_col,
        "window_size": window_size,
        "train_split": train_split,
        "split_index": split_index,
        "train_date_range": (
            df.index[0].strftime("%Y-%m-%d"),
            df.index[split_index - 1].strftime("%Y-%m-%d"),
        ),
        "test_date_range": (
            df.index[split_index].strftime("%Y-%m-%d"),
            df.index[-1].strftime("%Y-%m-%d"),
        ),
        "train_sequence_count": int(X_train.shape[0]),
        "test_sequence_count": int(X_test.shape[0]),
        "X_train_shape": X_train.shape,
        "y_train_shape": y_train.shape,
        "X_test_shape": X_test.shape,
        "y_test_shape": y_test.shape,
        "train_scaled_min": float(np.min(train_scaled)),
        "train_scaled_max": float(np.max(train_scaled)),
        "test_scaled_min": float(np.min(test_scaled)),
        "test_scaled_max": float(np.max(test_scaled)),
        "first_sequence_preview": X_train[0, :, 0].tolist(),
        "first_sequence_target": float(y_train[0]),
    }

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "scaler": scaler,
        "metadata": metadata,
    }


def format_preprocessing_proof(bundle):
    metadata = bundle["metadata"]
    return "\n".join(
        [
            f"Feature: {metadata['feature_name']}",
            f"Window size: {metadata['window_size']}",
            f"X_train shape: {metadata['X_train_shape']}",
            f"y_train shape: {metadata['y_train_shape']}",
            f"X_test shape: {metadata['X_test_shape']}",
            f"y_test shape: {metadata['y_test_shape']}",
            f"Train date range: {metadata['train_date_range'][0]} to {metadata['train_date_range'][1]}",
            f"Test date range: {metadata['test_date_range'][0]} to {metadata['test_date_range'][1]}",
            f"Scaled train range: ({metadata['train_scaled_min']:.6f}, {metadata['train_scaled_max']:.6f})",
            "First normalized sequence preview: "
            + ", ".join(
                f"{value:.6f}" for value in metadata["first_sequence_preview"][:5]
            ),
            f"First target: {metadata['first_sequence_target']:.6f}",
        ]
    )

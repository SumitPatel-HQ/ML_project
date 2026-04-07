"""Data loading and validation utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import DATA_PATH, DATE_COLUMN, TARGET_COLUMN


def _resolve_data_path(filepath):
    candidate = Path(filepath)
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"File not found: {filepath}")


def load_data(filepath=DATA_PATH, date_column=DATE_COLUMN):
    resolved_path = _resolve_data_path(filepath)
    return pd.read_csv(resolved_path, index_col=date_column, parse_dates=True)


def display_statistics(df, column=TARGET_COLUMN):
    print(f"Total rows: {len(df)}")
    print(
        f"Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"
    )
    if column in df.columns:
        print(f"{column} min: ${df[column].min():.2f}")
        print(f"{column} max: ${df[column].max():.2f}")


def check_missing_values(df, column=TARGET_COLUMN):
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")
    missing_count = int(df[column].isna().sum())
    print(f"Missing values in {column}: {missing_count}")
    return missing_count

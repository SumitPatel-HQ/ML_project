"""Plotting helpers for pipeline output."""

from __future__ import annotations

import os

from src.config import OUTPUT_DIR, RAW_PLOT_FILE, TARGET_COLUMN


def plot_price_history(df, column=TARGET_COLUMN, output_filename=RAW_PLOT_FILE):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ModuleNotFoundError:
        return output_path

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df[column], label=column)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()
    ax.set_xlabel("Date")
    ax.set_ylabel(f"{column} Price (USD)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return output_path

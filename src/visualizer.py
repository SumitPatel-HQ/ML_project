"""
Visualization functions for stock price prediction.

Handles time series plotting with proper date formatting
and file saving for analysis and reporting.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from src.config import (
    OUTPUT_DIR,
    RAW_PLOT_FILE,
    PREDICTION_PLOT_FILE,
    TARGET_COLUMN,
    PLOT_DPI,
    PLOT_FIGSIZE,
)

STATUS_OK = "[OK]"


def plot_price_history(df, column=TARGET_COLUMN, output_filename=RAW_PLOT_FILE):
    """
    Plot time series of stock prices and save to file.

    Creates line plot with proper date axis formatting and saves
    as PNG in output directory.

    Args:
        df (pd.DataFrame): Stock data with datetime index.
        column (str): Column to plot. Default from config.TARGET_COLUMN.
        output_filename (str): Output filename. Default from config.RAW_PLOT_FILE.

    Returns:
        str: Path to saved plot file.

    Example:
        >>> df = load_data()
        >>> plot_path = plot_price_history(df)
        >>> print(f"Plot saved to {plot_path}")
    """
    # Create figure
    fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)

    # Plot line
    ax.plot(df.index, df[column], color="#1f77b4", linewidth=1.5, label=column)

    # Configure date axis for readability
    # Use year-month format for multi-year data
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()  # Auto-rotate date labels

    # Labels and title
    ax.set_title(f"{column} Price History (2018-2025)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel(f"{column} Price (USD)", fontsize=12)

    # Grid for readability
    ax.grid(True, alpha=0.3, linestyle="--")

    # Legend
    ax.legend(loc="best", frameon=True, shadow=True)

    # Tight layout to prevent label cutoff
    plt.tight_layout()

    # Save with good DPI
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    fig.savefig(output_path, dpi=PLOT_DPI, bbox_inches="tight")

    # Close figure to free memory
    plt.close(fig)

    print(f"{STATUS_OK} Saved plot to {output_path}")

    return output_path

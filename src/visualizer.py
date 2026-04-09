"""Visualization functions for stock price prediction."""

import importlib
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from src.config import (
    CANDLESTICK_PLOT_FILE,
    CORRELATION_HEATMAP_FILE,
    OUTPUT_DIR,
    PLOT_DPI,
    PLOT_FIGSIZE,
    PREDICTION_BANDS_PLOT_FILE,
    PREDICTION_PLOT_FILE,
    RAW_PLOT_FILE,
    RESIDUAL_PLOT_FILE,
    TARGET_COLUMN,
)

STATUS_OK = "[OK]"
STATUS_WARN = "[WARN]"


def _save_figure(fig, output_filename):
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    fig.savefig(output_path, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"{STATUS_OK} Saved plot to {output_path}")
    return output_path


def _compute_error_sigma(actual_prices, predicted_prices):
    actual_array = np.asarray(actual_prices, dtype=float)
    predicted_array = np.asarray(predicted_prices, dtype=float)
    residuals = actual_array - predicted_array
    sigma = float(np.std(residuals))
    return residuals, sigma


def _load_optional_module(module_name, warning_message):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"{STATUS_WARN} {warning_message}")
        return None


def _build_balanced_close_features(df):
    close_series = df["Close"].astype(float)
    features = {
        "Close": close_series,
        "Return_1D": close_series.pct_change(),
        "Log_Return_1D": np.log(close_series / close_series.shift(1)),
        "SMA_7": close_series.rolling(window=7).mean(),
        "SMA_21": close_series.rolling(window=21).mean(),
        "Volatility_7": close_series.pct_change().rolling(window=7).std(),
        "Volatility_21": close_series.pct_change().rolling(window=21).std(),
        "Momentum_5": close_series - close_series.shift(5),
        "Momentum_10": close_series - close_series.shift(10),
        "EMA_12": close_series.ewm(span=12, adjust=False).mean(),
        "EMA_26": close_series.ewm(span=26, adjust=False).mean(),
    }

    delta = close_series.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)
    avg_gain = gains.rolling(window=14).mean()
    avg_loss = losses.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    features["RSI_14"] = 100.0 - (100.0 / (1.0 + rs))

    return features


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

    return _save_figure(fig, output_filename)


def plot_predictions(
    actual_prices,
    predicted_prices,
    rmse,
    mape,
    output_filename=PREDICTION_PLOT_FILE,
    ticker="AAPL",
):
    """Plot actual vs. predicted closing prices for the test set."""
    fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
    trading_days = range(len(actual_prices))

    ax.plot(
        trading_days,
        actual_prices,
        color="#1f77b4",
        linestyle="-",
        linewidth=1.8,
        label="Actual",
    )
    ax.plot(
        trading_days,
        predicted_prices,
        color="#ff7f0e",
        linestyle="--",
        linewidth=1.8,
        label="Predicted",
    )
    ax.set_title(
        f"{ticker} Predicted vs Actual Close | RMSE: {rmse:.4f} | MAPE: {mape:.4f}%",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Trading Days (Test Set)", fontsize=12)
    ax.set_ylabel("Close Price (USD)", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="best", frameon=True)
    plt.tight_layout()

    return _save_figure(fig, output_filename)


def plot_predictions_with_confidence_bands(
    actual_prices,
    predicted_prices,
    rmse,
    mape,
    output_filename=PREDICTION_BANDS_PLOT_FILE,
    ticker="AAPL",
):
    """Plot actual vs. predicted prices with a +/-1 sigma error band."""
    fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
    trading_days = np.arange(len(actual_prices))
    _, sigma = _compute_error_sigma(actual_prices, predicted_prices)
    predicted_array = np.asarray(predicted_prices, dtype=float)

    ax.plot(trading_days, actual_prices, color="#1f77b4", linewidth=1.8, label="Actual")
    ax.plot(
        trading_days,
        predicted_prices,
        color="#ff7f0e",
        linestyle="--",
        linewidth=1.8,
        label="Predicted",
    )
    ax.fill_between(
        trading_days,
        predicted_array - sigma,
        predicted_array + sigma,
        color="#ff7f0e",
        alpha=0.2,
        label="Predicted +/- 1 sigma",
    )
    ax.set_title(
        f"{ticker} Predicted vs Actual Close with Confidence Band | RMSE: {rmse:.4f} | MAPE: {mape:.4f}%",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Trading Days (Test Set)", fontsize=12)
    ax.set_ylabel("Close Price (USD)", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="best", frameon=True)
    plt.tight_layout()

    return _save_figure(fig, output_filename)


def plot_residuals(
    actual_prices,
    predicted_prices,
    output_filename=RESIDUAL_PLOT_FILE,
    ticker="AAPL",
):
    """Plot residual errors with zero line and +/-1 sigma shading."""
    fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)
    trading_days = np.arange(len(actual_prices))
    residuals, sigma = _compute_error_sigma(actual_prices, predicted_prices)

    ax.plot(trading_days, residuals, color="#2ca02c", linewidth=1.6, label="Residual")
    ax.axhline(0.0, color="#d62728", linestyle="--", linewidth=1.2, label="Zero error")
    ax.fill_between(
        trading_days,
        -sigma,
        sigma,
        color="#2ca02c",
        alpha=0.15,
        label="+/- 1 sigma",
    )
    ax.set_title(
        f"{ticker} Test Residuals (Actual - Predicted)", fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("Trading Days (Test Set)", fontsize=12)
    ax.set_ylabel("Residual (USD)", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="best", frameon=True)
    plt.tight_layout()

    return _save_figure(fig, output_filename)


def plot_candlestick_chart(
    df,
    output_filename=CANDLESTICK_PLOT_FILE,
    ticker="AAPL",
):
    """Plot a full-history OHLC candlestick chart using mplfinance."""
    mplfinance = _load_optional_module(
        "mplfinance", "mplfinance not installed; skipping candlestick plot"
    )
    if mplfinance is None:
        return None

    required_columns = ["Open", "High", "Low", "Close"]
    if not set(required_columns).issubset(df.columns):
        missing = ", ".join(
            column for column in required_columns if column not in df.columns
        )
        print(f"{STATUS_WARN} Missing OHLC columns for candlestick plot: {missing}")
        return None

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    savefig = {"fname": output_path, "dpi": PLOT_DPI, "bbox_inches": "tight"}
    mplfinance.plot(
        df[required_columns],
        type="candle",
        style="yahoo",
        title=f"{ticker} OHLC Candlestick Chart (2018-2025)",
        ylabel="Price (USD)",
        volume=False,
        figsize=PLOT_FIGSIZE,
        savefig=savefig,
    )
    plt.close("all")
    print(f"{STATUS_OK} Saved plot to {output_path}")
    return output_path


def plot_feature_correlation_heatmap(
    df,
    output_filename=CORRELATION_HEATMAP_FILE,
):
    """Plot a correlation heatmap for stock numeric features."""
    seaborn = _load_optional_module(
        "seaborn", "seaborn not installed; skipping correlation heatmap"
    )
    if seaborn is None:
        return None

    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    available_columns = [column for column in numeric_columns if column in df.columns]
    if not available_columns:
        print(
            f"{STATUS_WARN} No numeric feature columns available for correlation heatmap"
        )
        return None

    if available_columns == ["Close"]:
        feature_df = df.assign(**_build_balanced_close_features(df))
        feature_df = feature_df[
            [
                "Close",
                "Return_1D",
                "Log_Return_1D",
                "SMA_7",
                "SMA_21",
                "Volatility_7",
                "Volatility_21",
                "Momentum_5",
                "Momentum_10",
                "EMA_12",
                "EMA_26",
                "RSI_14",
            ]
        ].dropna()
        if len(feature_df) < 2:
            print(
                f"{STATUS_WARN} Close-only dataset does not have enough history for balanced technical-feature correlation heatmap"
            )
            return None
        correlation_matrix = feature_df.corr()
    else:
        correlation_matrix = df[available_columns].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    seaborn.heatmap(
        correlation_matrix,
        annot=True,
        cmap="YlGnBu",
        fmt=".2f",
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
    plt.tight_layout()

    return _save_figure(fig, output_filename)

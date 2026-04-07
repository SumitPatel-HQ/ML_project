"""
Data loading and validation for stock price prediction.

Handles CSV loading with datetime parsing, missing value detection,
and exploratory statistics display.
"""

import pandas as pd
from src.config import DATA_PATH, DATE_COLUMN, TARGET_COLUMN


def load_data(filepath=DATA_PATH, date_column=DATE_COLUMN):
    """
    Load stock data from CSV file with datetime index.

    Parses the date column during read (more efficient than post-conversion)
    and sets it as the DataFrame index.

    Args:
        filepath (str): Path to CSV file. Default from config.DATA_PATH.
        date_column (str): Name of date column. Default from config.DATE_COLUMN.

    Returns:
        pd.DataFrame: Stock data with datetime index.

    Raises:
        FileNotFoundError: If CSV file doesn't exist.
        pd.errors.ParserError: If CSV format is invalid.

    Example:
        >>> df = load_data()
        >>> print(df.head())
    """
    try:
        # Parse dates during read and set as index
        # This is 2-3x faster than reading as string and converting after
        df = pd.read_csv(
            filepath,
            index_col=date_column,
            parse_dates=True,  # Converts to datetime.Timestamp automatically
        )

        print(f"✓ Loaded data from {filepath}")
        print(f"  Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"  Columns: {', '.join(df.columns.tolist())}")

        return df

    except FileNotFoundError:
        print(f"✗ Error: File not found: {filepath}")
        print(f"  Expected location: data/AAPL.csv")
        raise

    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise


def display_statistics(df, column=TARGET_COLUMN):
    """
    Display exploratory statistics for price data.

    Shows row count, date range, and price statistics formatted
    for readability.

    Args:
        df (pd.DataFrame): Stock data with datetime index.
        column (str): Column to analyze. Default from config.TARGET_COLUMN.

    Returns:
        None: Prints statistics to console.

    Example:
        >>> df = load_data()
        >>> display_statistics(df)
        Total rows: 1762
        Date range: 2018-01-02 to 2025-01-01
        Close min: $132.05
        Close max: $182.94
        Close mean: $156.73
    """
    print("\n" + "=" * 60)
    print("DATA STATISTICS")
    print("=" * 60)

    print(f"Total rows: {len(df)}")
    print(
        f"Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"
    )

    # Price statistics
    if column in df.columns:
        print(f"\n{column} price statistics:")
        print(f"  Min:  ${df[column].min():.2f}")
        print(f"  Max:  ${df[column].max():.2f}")
        print(f"  Mean: ${df[column].mean():.2f}")
        print(f"  Std:  ${df[column].std():.2f}")
    else:
        print(f"⚠ Warning: Column '{column}' not found in DataFrame")

    print("=" * 60 + "\n")


def check_missing_values(df, column=TARGET_COLUMN):
    """
    Check and report missing values in target column.

    Uses pandas isna() to detect NaN/NaT values and reports count.

    Args:
        df (pd.DataFrame): Stock data to check.
        column (str): Column to check for missing values. Default from config.TARGET_COLUMN.

    Returns:
        int: Number of missing values found.

    Example:
        >>> df = load_data()
        >>> missing = check_missing_values(df)
        Missing values in Close: 0
    """
    if column not in df.columns:
        print(f"✗ Error: Column '{column}' not found in DataFrame")
        return -1

    missing_count = df[column].isna().sum()

    if missing_count == 0:
        print(f"✓ Missing values in {column}: 0")
    else:
        print(f"⚠ Missing values in {column}: {missing_count}")
        print(f"  This represents {100 * missing_count / len(df):.2f}% of data")

        # Show where missing values occur
        missing_dates = df[df[column].isna()].index.tolist()
        if len(missing_dates) <= 10:
            print(f"  Missing on dates: {missing_dates}")
        else:
            print(f"  First 10 missing dates: {missing_dates[:10]}")

    return missing_count

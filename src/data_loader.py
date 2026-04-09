"""
Data loading and validation for stock price prediction.

Handles CSV loading with datetime parsing, missing value detection,
and exploratory statistics display.
"""

import pandas as pd
from src.config import DATA_PATH, DATE_COLUMN, TARGET_COLUMN

STATUS_OK = "[OK]"
STATUS_ERROR = "[ERROR]"
STATUS_WARN = "[WARN]"


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

        return df

    except FileNotFoundError:
        print(f"{STATUS_ERROR} File not found: {filepath}")
        print(f"  Expected location: {filepath}")
        raise

    except Exception as e:
        print(f"{STATUS_ERROR} Error loading data: {e}")
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
    pass


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
    return df[column].isna().sum()

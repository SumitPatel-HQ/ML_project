import pandas as pd
from src.config import DATA_PATH, DATE_COLUMN, TARGET_COLUMN

STATUS_OK = "[OK]"
STATUS_ERROR = "[ERROR]"
STATUS_WARN = "[WARN]"

def load_data(filepath=DATA_PATH, date_column=DATE_COLUMN):
    try:
        df = pd.read_csv(
            filepath,
            index_col=date_column,
            parse_dates=True,
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
    pass

def check_missing_values(df, column=TARGET_COLUMN):
    return df[column].isna().sum()

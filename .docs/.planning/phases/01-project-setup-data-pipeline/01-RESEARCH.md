# Phase 1 Research: Project Setup & Data Pipeline

**Researched:** April 7, 2026  
**Focus:** Python ML project structure, pandas CSV loading, matplotlib visualization, configuration management

---

## Standard Stack

**Core:**
- **pandas 2.0+** — CSV loading, datetime parsing, statistics
- **matplotlib 3.7+** — Time series visualization
- **numpy 1.24+** — Array operations and random seed setting
- **TensorFlow 2.x** — Random seed setting (for later phases, but set in this phase)

**Why these:**
- pandas is the de facto standard for CSV/tabular data in Python
- matplotlib is the most mature plotting library with excellent date axis support
- numpy provides reproducibility through seed control
- All have high source reputation and are well-maintained

---

## Architecture Patterns

### Project Structure

**Recommended layout for ML projects:**
```
project_root/
├── data/
│   └── AAPL.csv                 # Input data (not committed if large)
├── output/                      # Generated artifacts
│   ├── raw_price.png
│   └── best_model.h5
├── src/                         # Source modules
│   ├── __init__.py
│   ├── config.py               # Centralized hyperparameters
│   ├── data_loader.py          # CSV loading logic
│   └── visualizer.py           # Plotting functions
├── main.py                      # Entry point
└── requirements.txt             # Dependencies
```

**Why this structure:**
- `src/` keeps modules organized and importable
- `output/` separates generated artifacts from source
- `data/` is the canonical location for input datasets
- `main.py` at root provides clear entry point

### Module Organization

**Pattern: Functional separation by responsibility**

Each module has a single concern:
- `data_loader.py` — Load and validate CSV
- `visualizer.py` — Create and save plots
- `config.py` — Store hyperparameters as constants

**Anti-pattern:** Monolithic `main.py` with all logic inline. This makes testing and reuse impossible.

### Configuration Management

**Pattern: config.py with uppercase constants**

```python
# src/config.py
# Hyperparameters for stock price prediction

# Data
DATA_PATH = "data/AAPL.csv"
DATE_COLUMN = "Date"
TARGET_COLUMN = "Close"

# Visualization
OUTPUT_DIR = "output"
RAW_PLOT_FILE = "raw_price.png"
PLOT_DPI = 100

# Reproducibility
RANDOM_SEED = 42
```

**Why config.py over .env:**
- .env is for secrets (API keys, passwords)
- config.py is for hyperparameters that should be version-controlled
- Python module allows type safety and IDE autocomplete

**Why not YAML:**
- Adds dependency (PyYAML)
- Requires parsing logic
- Python files are simpler for this use case

---

## Implementation Guidelines

### CSV Loading (DATA-01, DATA-02, DATA-04)

**Best practice: Parse dates during read, set as index**

```python
import pandas as pd

def load_data(filepath, date_column='Date'):
    """Load CSV with datetime index and validation."""
    # parse_dates during read is more efficient than post-conversion
    df = pd.read_csv(
        filepath,
        index_col=date_column,
        parse_dates=True  # Converts to datetime.Timestamp automatically
    )
    return df
```

**Date parsing options:**
- `parse_dates=True` — Auto-detect and parse date columns in index
- `parse_dates=['Date']` — Explicitly parse specific columns
- `index_col=0, parse_dates=True` — Parse first column as datetime index

**Missing value detection:**
```python
def check_missing_values(df, column='Close'):
    """Check and report missing values in target column."""
    missing_count = df[column].isna().sum()
    print(f"Missing values in {column}: {missing_count}")
    return missing_count
```

**Key pandas method:**
- `df.isna()` — Returns boolean mask for missing values (NaN, NaT)
- `df.isna().sum()` — Counts missing values per column

### Statistics Display (DATA-03)

**Pattern: Use pandas describe() and custom summary**

```python
def display_statistics(df, column='Close'):
    """Display exploratory statistics for price data."""
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(f"{column} min: ${df[column].min():.2f}")
    print(f"{column} max: ${df[column].max():.2f}")
    print(f"{column} mean: ${df[column].mean():.2f}")
```

**Why this over df.describe():**
- More readable for non-technical users
- Includes date range (not in describe())
- Formatted as currency ($)

### Visualization (DATA-05)

**Pattern: matplotlib with date formatting and file save**

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_price_history(df, column='Close', output_path='output/raw_price.png'):
    """Plot time series and save to file."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot line
    ax.plot(df.index, df[column], color='blue', linewidth=1.5)
    
    # Configure date axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()  # Auto-format date labels (rotation)
    
    # Labels
    ax.set_title(f'{column} Price History', fontsize=14)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel(f'{column} Price (USD)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Save with good DPI
    plt.tight_layout()
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)  # Free memory
    print(f"Saved plot to {output_path}")
```

**Key matplotlib patterns:**
- `mdates.DateFormatter('%Y-%m')` — Format date ticks
- `autofmt_xdate()` — Auto-rotate date labels for readability
- `savefig(..., dpi=100, bbox_inches='tight')` — Good quality, tight crop
- `plt.close(fig)` — Prevent memory leak from unclosed figures

**Date formatting options:**
- `'%Y-%m-%d'` — 2023-01-15
- `'%Y-%m'` — 2023-01 (good for multi-year data)
- `'%b %Y'` — Jan 2023

### Configuration Setup (INFRA-01)

**Pattern: Single source of truth for all hyperparameters**

```python
# src/config.py
"""Configuration for stock price prediction pipeline."""

# Data paths
DATA_PATH = "data/AAPL.csv"
OUTPUT_DIR = "output"

# Data columns
DATE_COLUMN = "Date"
TARGET_COLUMN = "Close"

# Preprocessing
SEQUENCE_LENGTH = 60  # Days to look back
TRAIN_SPLIT = 0.8     # 80% train, 20% test

# Model hyperparameters (for later phases)
LSTM_UNITS = 64
DROPOUT_RATE = 0.2
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EPOCHS = 100

# Reproducibility
RANDOM_SEED = 42
```

**Usage in other modules:**
```python
from src.config import DATA_PATH, DATE_COLUMN

df = pd.read_csv(DATA_PATH, index_col=DATE_COLUMN, parse_dates=True)
```

**Benefits:**
- Change once, affects entire pipeline
- Easy to experiment (change SEQUENCE_LENGTH from 60 to 90)
- Version-controlled (unlike runtime arguments)

### Entry Point (INFRA-03)

**Pattern: main.py orchestrates pipeline with phase flags**

```python
# main.py
"""Entry point for stock price prediction pipeline."""

import os
from src.config import OUTPUT_DIR, DATA_PATH, RANDOM_SEED
from src.data_loader import load_data, check_missing_values, display_statistics
from src.visualizer import plot_price_history

def setup_environment():
    """Create output directory and set seeds."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    """Run full pipeline."""
    print("=== Stock Price Prediction Pipeline ===\n")
    
    # Setup
    setup_environment()
    
    # Phase 1: Load and validate data
    print("Phase 1: Loading data...")
    df = load_data(DATA_PATH)
    
    # Statistics
    display_statistics(df)
    
    # Check missing values
    check_missing_values(df)
    
    # Visualize
    plot_price_history(df)
    
    print("\n✓ Phase 1 complete")

if __name__ == "__main__":
    main()
```

**Why this pattern:**
- Clear pipeline stages (easy to add Phase 2, 3, 4 later)
- Imports from src/ modules (not inline code)
- `if __name__ == "__main__"` allows import without execution

### Reproducibility (INFRA-04)

**Pattern: Set all random seeds at pipeline start**

```python
import numpy as np
import tensorflow as tf
import random
from src.config import RANDOM_SEED

def set_random_seeds(seed=RANDOM_SEED):
    """Set seeds for reproducibility across libraries."""
    random.seed(seed)           # Python built-in random
    np.random.seed(seed)        # NumPy
    tf.random.set_seed(seed)    # TensorFlow
    # Note: Some GPU ops are non-deterministic even with seeds
```

**Call in main.py setup:**
```python
def setup_environment():
    set_random_seeds()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
```

**Why this matters:**
- Makes results reproducible across runs
- Critical for debugging ("Did my change help or just random variation?")
- Best practice for academic/research ML projects

---

## Common Pitfalls

### 1. Date Parsing After Read (Inefficient)

**Problem:**
```python
# BAD: Read as string, then convert
df = pd.read_csv("data.csv")
df['Date'] = pd.to_datetime(df['Date'])
```

**Solution:**
```python
# GOOD: Parse during read
df = pd.read_csv("data.csv", index_col='Date', parse_dates=True)
```

**Why:** Parsing during read is 2-3x faster and uses less memory.

### 2. Forgetting to Create Output Directory

**Problem:**
```python
# Crashes if output/ doesn't exist
plt.savefig('output/plot.png')  # FileNotFoundError
```

**Solution:**
```python
import os
os.makedirs('output', exist_ok=True)  # Creates if missing, no error if exists
plt.savefig('output/plot.png')
```

### 3. Not Closing Matplotlib Figures

**Problem:**
```python
# Memory leak in loops
for i in range(100):
    plt.figure()
    plt.plot(data)
    plt.savefig(f'plot_{i}.png')
    # Figure never closed → 100 figures in memory
```

**Solution:**
```python
for i in range(100):
    fig, ax = plt.subplots()
    ax.plot(data)
    fig.savefig(f'plot_{i}.png')
    plt.close(fig)  # Explicitly free memory
```

### 4. Date Axis Overlap (Unreadable Labels)

**Problem:** Date labels overlap on x-axis when time range is large.

**Solution:**
```python
import matplotlib.dates as mdates

# Auto-rotate and format
plt.gcf().autofmt_xdate()

# Or control formatter explicitly
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
```

### 5. Hardcoding File Paths

**Problem:**
```python
df = pd.read_csv("C:/Users/Me/project/data/AAPL.csv")  # Breaks on other machines
```

**Solution:**
```python
import os
from src.config import DATA_PATH

# Use relative paths or config constants
df = pd.read_csv(DATA_PATH)
```

---

## Don't Hand-Roll

**Use libraries for these — don't implement from scratch:**

1. **Date parsing** — Use pandas `parse_dates`, not custom regex
2. **Missing value detection** — Use `df.isna()`, not manual checks
3. **Statistics** — Use pandas built-ins, not manual loops
4. **Plot styling** — Use matplotlib defaults or established themes, not pixel-by-pixel drawing
5. **Directory creation** — Use `os.makedirs(exist_ok=True)`, not subprocess calls

**Why:** These are solved problems with battle-tested implementations. Custom code adds bugs and maintenance burden.

---

## Validation Architecture

**Output validation for Phase 1:**

After execution, verify:
1. **File existence:** `output/raw_price.png` exists and is a valid PNG
2. **Data shape:** DataFrame has >1000 rows (expected for 2018-2025 AAPL data)
3. **Date range:** Index spans 2018-01-01 to ~2025-01-01
4. **No missing values:** `df['Close'].isna().sum() == 0`
5. **Statistics sanity:** Close price min > 0, max < $300 (reasonable for AAPL)

**Automated check pattern:**
```python
def validate_phase1_outputs(df, plot_path='output/raw_price.png'):
    """Validate Phase 1 outputs meet requirements."""
    checks = {
        "Plot exists": os.path.exists(plot_path),
        "Sufficient data": len(df) > 1000,
        "No missing values": df['Close'].isna().sum() == 0,
        "Valid date range": df.index.min().year == 2018,
        "Valid price range": 0 < df['Close'].min() < df['Close'].max() < 300
    }
    
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")
    
    return all(checks.values())
```

**This validation function should be created in a separate task or plan — NOT in Phase 1 execution itself. It's used by verification workflows after Phase 1 completes.**

---

## Additional Context

### CSV Format Expectations

**Expected AAPL.csv structure (Kaggle "15Y Big Tech Stock Data"):**
```
Date,Open,High,Low,Close,Adj Close,Volume
2018-01-02,42.54,43.07,42.31,43.06,41.35,...
2018-01-03,43.13,43.37,42.95,43.06,41.35,...
...
```

**Key assumptions:**
- `Date` column in YYYY-MM-DD format (ISO 8601)
- `Close` column is float (USD price)
- No timezone info (assume market close time, not needed for daily data)
- Volume column exists but not used in Phase 1

### Output Directory Management

**Pattern:** Create `output/` in setup, not per-save.

```python
def setup_environment():
    """One-time setup for pipeline."""
    os.makedirs('output', exist_ok=True)
    set_random_seeds()
```

**Anti-pattern:** Checking `os.path.exists()` before every save — wasteful.

### Future Phase Considerations

**Phase 1 sets foundation for later phases:**
- Phase 2 will import `data_loader.load_data()` — ensure it's reusable
- Phase 3 needs random seeds set in Phase 1 — ensure `set_random_seeds()` is called early
- Phase 4 will add more plots to `output/` — ensure directory exists from start

**Design principle:** Each phase builds on prior phases' modules. Phase 1 modules should be importable and testable independently.

---

## Research Summary

**Key findings:**
1. pandas `parse_dates=True` + `index_col` is the standard pattern for time series CSV loading
2. matplotlib date formatting requires `mdates` module and `autofmt_xdate()` for readability
3. config.py pattern is preferred over .env for ML hyperparameters
4. Modular src/ structure enables reuse in later phases
5. Random seed setting must happen before any numpy/TensorFlow operations

**Recommended approach:**
- Use standard library patterns (don't reinvent)
- Separate concerns (data_loader, visualizer, config)
- Set up reproducibility infrastructure early (seeds, output dir)
- Validate outputs to ensure requirements met

**Confidence level:** HIGH — all patterns are well-established in Python ML community.

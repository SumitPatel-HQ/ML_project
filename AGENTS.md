<!-- GSD:project-start source:PROJECT.md -->
## Project

**Stock Price Prediction using LSTM Neural Networks**

A machine learning application that predicts future stock closing prices using a Long Short-Term Memory (LSTM) neural network trained on a **static Kaggle CSV dataset**. The system preprocesses historical stock data, trains a stacked LSTM model, and outputs predicted vs. actual price visualizations alongside evaluation metrics — all without requiring live internet connectivity.

**Core Value:** **Accurate next-day closing price prediction with MAPE < 5% using a simple, offline LSTM pipeline.**

The ONE thing that must work: Given a CSV file of historical AAPL stock data, the system trains an LSTM model and produces predictions that are within 5% of actual prices, demonstrating the model can learn meaningful temporal patterns from price history.

### Constraints

### Technical
- **Dataset**: Kaggle "15Y Big Tech Stock Data" — AAPL.csv relocated to Dataset/actualdataset/
- **Date range**: 2018-01-01 to 2025-01-01 (~1,762 trading days)
- **Tech stack**: Python 3.10+, TensorFlow 2.x, pandas, scikit-learn, matplotlib
- **Hardware**: Must train in < 10 minutes on CPU (no GPU required)
- **No live data**: Zero API calls — fully offline pipeline

### Scope
- **In scope**: Load CSV → Preprocess → Train LSTM → Evaluate → Visualize
- **Out of scope**: Live data fetching, intraday prediction, multi-stock comparison, trading integration

### Success Metrics
| Metric              | Target                     |
|---------------------|----------------------------|
| MAPE on test set    | < 5%                       |
| RMSE on test set    | < $5 (for AAPL-scale data) |
| Training time       | < 5 minutes on CPU         |
| Visualization       | Clear actual vs. predicted plot |
<!-- GSD:project-end -->

## Technology Stack

- **Languge**: Python 3.10+
- **Deep Learning**: TensorFlow 2.12+, Keras
- **Data Processing**: pandas (2.0.0+), numpy (1.24.0+)
- **Machine Learning**: scikit-learn (1.3.0+) for scaling and preprocessing
- **Visualization**: matplotlib (3.7.0+) for price plots and metrics
- **Hardware**: CPU-optimized training pipeline (no CUDA required)

## Conventions

- **Modular Backend**: Code split into `data_loader`, `preprocessor`, `model`, `trainer`, and `visualizer`.
- **Reproducibility**: Global seeds set for NumPy and TensorFlow via `src/utils.py`.
- **Configuration**: All hyperparameters (window size, units, learning rate) centralized in `src/config.py`.
- **Leakage Prevention**: Scalers (`MinMaxScaler`) fitted ONLY on training data; temporal split for train/test (no shuffling).
- **Docstrings**: Google/Numpy style docstrings for all core functions.
- **Phased Execution**: `main.py` orchestrated by discrete phases (1: Load, 2: Preprocess, 3: Build/Train, 4: Evaluate).

## Architecture

The project follows a modular pipeline architecture designed for offline scalability:

- **src/config.py**: Configuration layer containing file paths and model hyperparameters.
- **src/data_loader.py**: Data ingestion layer for loading and cleaning Kaggle CSV files.
- **src/preprocessor.py**: Transformation layer mapping raw prices to normalized (60, 1) sequences.
- **src/model.py**: Model definition layer implementing a 2-layer stacked LSTM with dropout.
- **src/trainer.py**: execution layer managing the Keras training loop and callbacks.
- **src/visualizer.py**: Presentation layer for generating professional diagnostic plots.
- **src/utils.py**: Utility layer for environment setup and metric calculation.
- **main.py**: Orchestration layer that chains modules into a complete ML lifecycle.

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

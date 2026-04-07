# Stock Price Prediction using LSTM Neural Networks

## What This Is

A machine learning application that predicts future stock closing prices using a Long Short-Term Memory (LSTM) neural network trained on a **static Kaggle CSV dataset**. The system preprocesses historical stock data, trains a stacked LSTM model, and outputs predicted vs. actual price visualizations alongside evaluation metrics — all without requiring live internet connectivity.

## Core Value

**Accurate next-day closing price prediction with MAPE < 5% using a simple, offline LSTM pipeline.**

The ONE thing that must work: Given a CSV file of historical AAPL stock data, the system trains an LSTM model and produces predictions that are within 5% of actual prices, demonstrating the model can learn meaningful temporal patterns from price history.

## Context

### Problem
Stock prices are sequential and time-dependent. Traditional ML models ignore temporal order and cannot capture how today's price influences tomorrow's. This project uses LSTM — a neural network built for sequence learning — to capture price trends across 60-day windows and forecast future closing prices.

### Approach
- **Single stock focus**: AAPL only (keep scope tight)
- **Univariate feature**: Close price ONLY (no Open/High/Low/Volume)
- **Static dataset**: Pre-downloaded Kaggle CSV (no live API dependency)
- **Single-step prediction**: Next-day closing price (not multi-day forecast)
- **Stacked LSTM**: 2-layer architecture with dropout for regularization
- **Offline-first**: Entire pipeline runs without internet after dataset download

### Users
- Data science students learning time-series prediction
- ML practitioners exploring LSTM for financial forecasting
- Developers prototyping offline prediction systems

## Constraints

### Technical
- **Dataset**: Kaggle "15Y Big Tech Stock Data" — AAPL.csv already downloaded
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

## Requirements

### Validated

- **PREP-01**: System extracts Close column as sole input feature (univariate) — Validated in Phase 02: Preprocessing & Sequence Generation
- **PREP-02**: System applies MinMaxScaler fitted only on training data (prevents data leakage) — Validated in Phase 02: Preprocessing & Sequence Generation
- **PREP-03**: System creates input-output sequences using 60-day sliding window — Validated in Phase 02: Preprocessing & Sequence Generation
- **PREP-04**: System splits data 80/20 train/test without shuffling (preserves temporal order) — Validated in Phase 02: Preprocessing & Sequence Generation
- **PREP-05**: System reshapes sequences to (samples, timesteps, 1) for LSTM input — Validated in Phase 02: Preprocessing & Sequence Generation

### Active

#### Data Pipeline
- [ ] **DATA-01**: Load stock data from local CSV file (data/AAPL.csv)
- [ ] **DATA-02**: Parse Date column as datetime index
- [ ] **DATA-03**: Display basic statistics (row count, date range, min/max Close)
- [ ] **DATA-04**: Check for and report missing values in Close column
- [ ] **DATA-05**: Plot raw Close price history before training

#### Preprocessing

#### Model Architecture
- [ ] **MODEL-01**: Implement stacked LSTM with 2 LSTM layers (64 units each)
- [ ] **MODEL-02**: Add dropout layers (0.2) after each LSTM for regularization
- [ ] **MODEL-03**: Add Dense layer (32 units, ReLU) for non-linear combination
- [ ] **MODEL-04**: Output layer (1 unit) for predicted closing price
- [ ] **MODEL-05**: Compile with Adam optimizer (lr=0.001) and MSE loss

#### Training
- [ ] **TRAIN-01**: Train for up to 100 epochs with batch_size=32
- [ ] **TRAIN-02**: Use 10% validation split from training data
- [ ] **TRAIN-03**: Implement EarlyStopping (patience=10, monitor='val_loss')
- [ ] **TRAIN-04**: Save best model weights using ModelCheckpoint
- [ ] **TRAIN-05**: Display training/validation loss per epoch

#### Evaluation & Output
- [ ] **EVAL-01**: Generate predictions on test set using trained model
- [ ] **EVAL-02**: Inverse-transform predictions and actuals to USD prices
- [ ] **EVAL-03**: Compute and display RMSE on test set
- [ ] **EVAL-04**: Compute and display MAPE on test set
- [ ] **EVAL-05**: Generate line plot (Actual vs Predicted) and save as PNG
- [ ] **EVAL-06**: Save trained model as output/best_model.h5 for reuse

#### Configuration & Structure
- [ ] **INFRA-01**: Centralize all hyperparameters in src/config.py
- [ ] **INFRA-02**: Create modular source structure (data_loader, preprocessor, model, trainer, evaluator, visualizer)
- [ ] **INFRA-03**: Implement main.py as entry point for full pipeline
- [ ] **INFRA-04**: Set random seeds for numpy and TensorFlow (reproducibility)

### Out of Scope

- **Live API integration** — Project uses static CSV only, no yfinance/Alpha Vantage
- **Multi-stock comparison** — Focus on AAPL only for v1
- **Intraday prediction** — Daily closing prices only, no minute/hour granularity
- **Technical indicators** — No MA50/RSI/Bollinger Bands in base model
- **Streamlit dashboard** — Command-line execution only for v1
- **Multi-step forecasting** — Single next-day prediction only
- **Confidence intervals** — Point estimates only, no probabilistic output
- **Real-time trading integration** — No brokerage API connectivity

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Stacked LSTM (2 layers) | Captures both short-term and long-range temporal dependencies better than single layer | — Architecture selected |
| 60-day window size | ~3 months of trading days; captures quarterly trends without excessive memory | — Hyperparameter set |
| Univariate (Close only) | Simplifies model, reduces noise from correlated features | — Feature engineering scoped |
| MinMaxScaler [0,1] | LSTM performs better with normalized inputs; prevents vanishing gradients | — Scaling method chosen |
| Static Kaggle dataset | Eliminates API dependencies, makes project fully reproducible offline | — Data source confirmed |
| Adam optimizer | Standard for LSTM; adaptive learning rate handles MSE landscape well | — Optimizer selected |
| Dropout 0.2 | Industry standard for financial time-series LSTM; prevents overfitting | — Regularization configured |
| No shuffling in train/test split | Preserves temporal order; prevents look-ahead bias | — Data split strategy set |

## Project Structure

```
stock-lstm-predictor/
├── data/
│   └── AAPL.csv               ← Kaggle dataset (already downloaded)
├── output/                    ← auto-created by code
│   ├── best_model.h5
│   ├── raw_price.png
│   ├── AAPL_prediction.png
│   └── metrics.json
├── src/
│   ├── config.py              ← Hyperparameters & paths
│   ├── data_loader.py         ← FR: DATA-01 to DATA-05
│   ├── preprocessor.py        ← FR: PREP-01 to PREP-05
│   ├── model.py               ← FR: MODEL-01 to MODEL-05
│   ├── trainer.py             ← FR: TRAIN-01 to TRAIN-05
│   ├── evaluator.py           ← FR: EVAL-01 to EVAL-04
│   └── visualizer.py          ← FR: EVAL-05
├── main.py                    ← Entry point
├── notebook.ipynb             ← Jupyter walkthrough (optional)
├── requirements.txt
└── README.md
```

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
## Current State

Phase 2 complete — the CLI pipeline now produces leakage-safe preprocessing bundles, LSTM-ready tensor shapes, and proof output for chronology and scaler behavior.

---
*Last updated: April 2026 after Phase 2 completion*

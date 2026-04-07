# Technical Design Document (TDD)
## Stock Price Prediction using LSTM Neural Networks

**Version:** 2.0 (Updated — Static Dataset)  
**Author:** Sumit Patel  
**Date:** April 2026  
**Status:** Draft

---

## 1. System Overview

This document describes the detailed technical design for the LSTM-based Stock Price
Prediction system using a **pre-downloaded static Kaggle CSV** as its sole data source.
No live API is used. The pipeline runs fully offline.

---

## 2. Models & Algorithms Used

### 2.1 Core Model — Stacked LSTM (Long Short-Term Memory)

LSTM is a type of Recurrent Neural Network (RNN) that uses gating mechanisms to
selectively remember and forget information across long sequences — ideal for
stock price time series.

**LSTM Cell Gates:**
```
Forget Gate:  f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
Input Gate:   i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
Cell State:   C_t = f_t ⊙ C_{t-1} + i_t ⊙ tanh(W_C · [h_{t-1}, x_t] + b_C)
Output Gate:  o_t = σ(W_o · [h_{t-1}, x_t] + b_o)
Hidden State: h_t = o_t ⊙ tanh(C_t)
```
- σ = Sigmoid (outputs 0–1, acts as a gate controller)
- ⊙ = Element-wise multiplication
- x_t = Current input (today's normalized close price)
- h_{t-1} = Previous hidden state (short-term memory)
- C_{t-1} = Previous cell state (long-term memory)

**Why LSTM over plain RNN?**
Plain RNNs suffer from the vanishing gradient problem — they cannot learn patterns
more than a few steps back. LSTM's cell state acts as a "conveyor belt" that carries
long-range information forward, enabling it to remember patterns from 60+ days ago.

### 2.2 Supporting Algorithms

| Algorithm         | Type              | Library       | Role                                       |
|-------------------|-------------------|---------------|--------------------------------------------|
| MinMaxScaler      | Normalization     | scikit-learn  | Scale Close prices to [0,1]               |
| Sliding Window    | Sequence creation | numpy         | Create (X: 60 days → y: day 61) pairs     |
| Adam Optimizer    | Gradient descent  | TensorFlow    | Update LSTM weights during training        |
| MSE Loss          | Loss function     | TensorFlow    | Measure training error (squared diff)      |
| EarlyStopping     | Regularization    | TensorFlow    | Stop training when val_loss stops improving|
| Dropout (0.2)     | Regularization    | TensorFlow    | Randomly zero 20% neurons to reduce overfit|
| RMSE              | Metric            | numpy         | Evaluate error in USD (square root of MSE) |
| MAPE              | Metric            | numpy         | Evaluate % accuracy of predictions        |

---

## 3. High-Level Architecture

```
[Local CSV File — Kaggle Dataset]
          │
          ▼
[Data Loading Module]        →  raw DataFrame (Date, Close, ...)
          │
          ▼
[EDA Module]                 →  statistics + raw price plot
          │
          ▼
[Preprocessing Module]
  ├── Extract Close column
  ├── MinMaxScaler (fit on train only)
  ├── Sliding Window (size=60)
  └── Train/Test Split (80/20)
          │
     ┌────┴────┐
     ▼         ▼
X_train     X_test
(n,60,1)   (m,60,1)
     │         │
     ▼         │
[LSTM Model]   │
  ├── LSTM Layer 1 (64 units, return_seq=True)
  ├── Dropout (0.2)
  ├── LSTM Layer 2 (64 units)
  ├── Dropout (0.2)
  ├── Dense (32, ReLU)
  └── Dense (1) → predicted normalized price
     │         │
     ▼         ▼
[Training]  [Inference]
Adam+MSE    model.predict(X_test)
EarlyStopping
ModelCheckpoint
     │         │
     ▼         ▼
best_model.h5  Inverse Transform → USD prices
               │
          ┌────┴────┐
          ▼         ▼
    [Evaluation]  [Visualization]
    RMSE, MAPE    Actual vs Predicted PNG
```

---

## 4. Module Design

### 4.1 config.py — Central Configuration

```python
CONFIG = {
    "csv_path":    "data/AAPL.csv",        # Local Kaggle CSV file path
    "ticker":      "AAPL",                  # For plot labels
    "start_date":  "2018-01-01",            # Filter rows from CSV
    "end_date":    "2025-01-01",
    "feature_col": "Close",                 # Column to predict
    "window_size": 60,                      # Sliding window length
    "train_split": 0.80,                    # 80% train, 20% test
    "lstm_units":  64,
    "dropout":     0.2,
    "epochs":      100,
    "batch_size":  32,
    "patience":    10,                      # EarlyStopping patience
    "model_path":  "output/best_model.h5",
    "plot_path":   "output/AAPL_prediction.png",
    "random_seed": 42
}
```

---

### 4.2 data_loader.py — Data Loading & EDA

```python
import pandas as pd

def load_csv(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(cfg["csv_path"], parse_dates=["Date"], index_col="Date")
    df = df.sort_index()
    df = df.loc[cfg["start_date"]: cfg["end_date"]]
    if df.empty:
        raise ValueError(f"No data in range {cfg['start_date']} – {cfg['end_date']}")
    print(f"Loaded {len(df)} rows | Date range: {df.index.min()} → {df.index.max()}")
    print(f"Missing values in Close: {df['Close'].isna().sum()}")
    return df

def plot_raw(df: pd.DataFrame, cfg: dict):
    import matplotlib.pyplot as plt
    df["Close"].plot(figsize=(14, 5), title=f"{cfg['ticker']} Raw Close Price")
    plt.xlabel("Date"); plt.ylabel("Close Price (USD)")
    plt.tight_layout(); plt.savefig("output/raw_price.png"); plt.show()
```

---

### 4.3 preprocessor.py — Scaling + Sequencing

```python
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def preprocess(df, cfg):
    data = df[[cfg["feature_col"]]].values  # shape: (N, 1)

    split_idx = int(len(data) * cfg["train_split"])
    train_raw = data[:split_idx]
    test_raw  = data[split_idx:]

    # Fit scaler ONLY on training data to prevent data leakage
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = scaler.fit_transform(train_raw)

    # Include last `window_size` rows of train in test for continuity
    test_input = np.concatenate([train_raw[-cfg["window_size"]:], test_raw])
    test_scaled = scaler.transform(test_input)

    X_train, y_train = _create_sequences(train_scaled, cfg["window_size"])
    X_test,  y_test  = _create_sequences(test_scaled,  cfg["window_size"])

    # Reshape: (samples, timesteps, features=1)
    X_train = X_train.reshape(-1, cfg["window_size"], 1)
    X_test  = X_test.reshape(-1,  cfg["window_size"], 1)

    return X_train, y_train, X_test, y_test, scaler

def _create_sequences(data, window):
    X, y = [], []
    for i in range(window, len(data)):
        X.append(data[i - window:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)
```

**Key design decision:** The scaler is fitted on training data only, then applied to
test data. This prevents information from the future leaking into the model during
training — a critical correctness requirement.

---

### 4.4 model.py — LSTM Architecture

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import tensorflow as tf

def build_lstm(cfg: dict) -> Sequential:
    tf.random.set_seed(cfg["random_seed"])

    model = Sequential([
        LSTM(cfg["lstm_units"],
             return_sequences=True,
             input_shape=(cfg["window_size"], 1)),   # Input: 60 timesteps, 1 feature
        Dropout(cfg["dropout"]),                      # Drops 20% neurons randomly
        LSTM(cfg["lstm_units"],
             return_sequences=False),                 # Final LSTM layer
        Dropout(cfg["dropout"]),
        Dense(32, activation='relu'),                 # Non-linear combination layer
        Dense(1)                                      # Output: 1 predicted price
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='mean_squared_error'
    )
    model.summary()
    return model
```

**Architecture Rationale:**

| Layer            | Config                     | Reason                                         |
|------------------|----------------------------|------------------------------------------------|
| LSTM Layer 1     | 64 units, return_seq=True  | Extracts short-to-mid range temporal patterns  |
| Dropout 1        | rate = 0.2                 | Randomly disables 20% neurons per batch        |
| LSTM Layer 2     | 64 units                   | Extracts higher-order long-range dependencies  |
| Dropout 2        | rate = 0.2                 | Second regularization layer                    |
| Dense (32, ReLU) | 32 neurons                 | Combines LSTM outputs non-linearly             |
| Dense (1)        | 1 neuron, no activation    | Outputs raw predicted normalized price         |

---

### 4.5 trainer.py — Training Loop

```python
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

def train(model, X_train, y_train, cfg):
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=cfg["patience"],
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=cfg["model_path"],
            save_best_only=True,
            monitor='val_loss',
            verbose=1
        )
    ]
    history = model.fit(
        X_train, y_train,
        epochs=cfg["epochs"],
        batch_size=cfg["batch_size"],
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1
    )
    return history
```

**Hyperparameter Defaults:**

| Parameter    | Default | Notes                                               |
|--------------|---------|-----------------------------------------------------|
| epochs       | 100     | EarlyStopping typically triggers at epoch 30–50     |
| batch_size   | 32      | Stable gradient updates; standard for time-series   |
| window_size  | 60      | ~3 months of trading days; captures quarterly trends|
| lstm_units   | 64      | Balanced capacity; avoids overfit on small dataset  |
| dropout      | 0.2     | Standard for financial LSTM projects                |
| learning_rate| 0.001   | Adam default; well-suited for MSE loss landscape    |
| patience     | 10      | Stops training 10 epochs after val_loss plateaus    |

---

### 4.6 evaluator.py — Metrics

```python
import numpy as np
from sklearn.metrics import mean_squared_error

def evaluate(model, X_test, y_test, scaler):
    predictions_scaled = model.predict(X_test)

    # Inverse transform both to original USD scale
    predictions = scaler.inverse_transform(predictions_scaled)
    actual      = scaler.inverse_transform(y_test.reshape(-1, 1))

    rmse = np.sqrt(mean_squared_error(actual, predictions))
    mape = np.mean(np.abs((actual - predictions) / actual)) * 100

    print(f"\n{'='*35}")
    print(f" RMSE : ${rmse:.4f}")
    print(f" MAPE : {mape:.2f}%")
    print(f"{'='*35}\n")

    return predictions, actual, rmse, mape
```

---

### 4.7 visualizer.py — Output Plot

```python
import matplotlib.pyplot as plt

def plot_predictions(actual, predictions, cfg, rmse, mape):
    plt.figure(figsize=(14, 6))
    plt.plot(actual,      label='Actual Price',    color='steelblue',  linewidth=2)
    plt.plot(predictions, label='Predicted Price', color='darkorange', linewidth=2, linestyle='--')
    plt.title(f"{cfg['ticker']} Stock Price Prediction (LSTM)\nRMSE: ${rmse:.2f} | MAPE: {mape:.2f}%")
    plt.xlabel("Trading Days (Test Set)")
    plt.ylabel("Close Price (USD)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(cfg["plot_path"], dpi=150)
    plt.show()
    print(f"Plot saved to {cfg['plot_path']}")
```

---

## 5. Data Flow with Tensor Shapes

```
CSV file loaded → DataFrame (1762 rows × 7 cols)
                         ↓
             Extract Close → (1762, 1) float array
                         ↓
             Train/Test split at 80%
             train_raw: (1409, 1)   test_raw: (353, 1)
                         ↓
             MinMaxScaler.fit_transform(train_raw)
             train_scaled: (1409, 1) in [0,1]
             test_scaled:  (413, 1)  in [0,1]  ← includes 60-row overlap
                         ↓
             Sliding Window (size=60)
             X_train: (1349, 60, 1)   y_train: (1349,)
             X_test:  (353,  60, 1)   y_test:  (353,)
                         ↓
             LSTM Model forward pass
             Output: (353, 1) predicted normalized prices
                         ↓
             inverse_transform → (353, 1) USD prices
                         ↓
             RMSE + MAPE computed → printed
             Actual vs Predicted → saved as PNG
```

---

## 6. Project Directory Structure

```
stock-lstm-predictor/
│
├── data/
│   └── AAPL.csv                  ← Downloaded from Kaggle (not tracked in git)
│
├── output/
│   ├── best_model.h5             ← Saved Keras model (best val_loss)
│   ├── raw_price.png             ← EDA plot: raw Close price history
│   ├── AAPL_prediction.png       ← Final output: Actual vs Predicted
│   └── metrics.json              ← RMSE + MAPE results
│
├── src/
│   ├── config.py                 ← All hyperparameters & file paths
│   ├── data_loader.py            ← FR-01, FR-02: Load CSV + EDA
│   ├── preprocessor.py           ← FR-03: Scaling + Sequencing
│   ├── model.py                  ← FR-04: LSTM architecture
│   ├── trainer.py                ← FR-05: Training + Callbacks
│   ├── evaluator.py              ← FR-07: RMSE + MAPE
│   └── visualizer.py             ← FR-08: Output plot
│
├── main.py                       ← Entry point — runs full pipeline
├── notebook.ipynb                ← Jupyter walkthrough version
├── requirements.txt
└── README.md
```

---

## 7. requirements.txt

```
numpy==1.26.4
pandas==2.2.1
scikit-learn==1.4.2
tensorflow==2.15.0
matplotlib==3.8.3
plotly==5.20.0
streamlit==1.32.0   # optional for F8
```

---

## 8. Risk & Mitigation

| Risk                        | Impact | Mitigation                                       |
|-----------------------------|--------|--------------------------------------------------|
| Overfitting on training data| High   | Dropout (0.2) + EarlyStopping (patience=10)      |
| Data leakage via scaler     | High   | Fit MinMaxScaler on train set only               |
| Look-ahead bias             | High   | No shuffling — strict temporal train/test split  |
| CSV format mismatch         | Medium | Validate column names in data_loader.py          |
| Non-stationarity of prices  | Medium | MinMaxScaler partially mitigates; use returns later|

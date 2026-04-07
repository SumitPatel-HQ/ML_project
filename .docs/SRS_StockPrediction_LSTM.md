# Software Requirements Specification (SRS)
## Stock Price Prediction using LSTM Neural Networks

**Version:** 2.0 (Updated — Static Dataset)  
**Author:** Sumit Patel  
**Date:** April 2026  
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose
This document defines all functional and non-functional requirements for the LSTM-based
Stock Price Prediction system using a **static Kaggle CSV dataset** as its data source.

### 1.2 Scope
The system SHALL read a local CSV file, preprocess it into time-series sequences,
train a stacked LSTM neural network, evaluate predictions using RMSE and MAPE,
and output a visual plot of actual vs. predicted closing prices.

### 1.3 Definitions

| Term           | Definition                                                                 |
|----------------|----------------------------------------------------------------------------|
| LSTM           | Long Short-Term Memory — a Recurrent Neural Network variant with gating    |
| OHLCV          | Open, High, Low, Close, Volume — standard daily stock data fields          |
| Sliding Window | Fixed-length sequence created by rolling over the time-series              |
| MinMaxScaler   | Scales data to range [0,1] using (x - min)/(max - min)                    |
| MAPE           | Mean Absolute Percentage Error — model accuracy expressed as %             |
| RMSE           | Root Mean Squared Error — model error in original price units (USD)        |
| Static Dataset | A pre-downloaded CSV file; no live internet fetch during model execution   |

---

## 2. System Description

### 2.1 System Context
The system is a fully offline ML pipeline. Input is a CSV file from Kaggle.
There is no external API dependency during training or inference.
All preprocessing, training, and evaluation happen locally in Python.

### 2.2 Assumptions & Dependencies
- User has pre-downloaded the Kaggle CSV dataset to their local machine
- Python 3.10+ runtime with required libraries installed
- TensorFlow >= 2.10 or PyTorch >= 2.0
- Minimum 2 years of trading data in the CSV for meaningful training

---

## 3. Functional Requirements

### FR-01: Data Loading
- The system SHALL read stock data from a local CSV file path specified in `config.py`.
- The system SHALL parse the `Date` column as a datetime index.
- The system SHALL support any CSV with at minimum `Date` and `Close` columns.
- The system SHALL validate the CSV exists and contains required columns; raise
  a descriptive error if not.

### FR-02: Exploratory Data Analysis (EDA)
- The system SHALL display basic statistics: row count, date range, min/max Close price.
- The system SHALL plot the raw Close price history before training.
- The system SHALL check for and report any missing values in the Close column.

### FR-03: Data Preprocessing
- The system SHALL extract the `Close` column as the sole input feature (univariate).
- The system SHALL apply MinMaxScaler (scikit-learn) fitted only on training data.
- The system SHALL create input-output sequences using a configurable sliding window
  (default: 60 days → predict day 61).
- The system SHALL split data into train (80%) and test (20%) without shuffling,
  preserving temporal order.
- The system SHALL reshape sequences to (samples, timesteps, 1) for LSTM input.

### FR-04: Model Definition — LSTM Neural Network
- The system SHALL implement a Stacked LSTM architecture using TensorFlow/Keras:
    - Layer 1: LSTM(64 units, return_sequences=True)
    - Layer 2: Dropout(0.2)
    - Layer 3: LSTM(64 units, return_sequences=False)
    - Layer 4: Dropout(0.2)
    - Layer 5: Dense(32, activation='relu')
    - Layer 6: Dense(1)  → predicted next Close price
- The system SHALL compile with Adam optimizer and MSE loss.

### FR-05: Model Training
- The system SHALL train the model for up to 100 epochs with EarlyStopping
  (patience=10, monitor='val_loss').
- The system SHALL use batch_size=32 and 10% validation split from training data.
- The system SHALL save the best model weights during training (ModelCheckpoint).
- The system SHALL display training loss and validation loss per epoch.

### FR-06: Prediction & Inverse Transform
- The system SHALL generate predictions on the test set using the trained model.
- The system SHALL inverse-transform both predictions and actual values
  from [0,1] back to USD prices using the fitted scaler.

### FR-07: Evaluation
- The system SHALL compute RMSE on the inverse-transformed test predictions.
- The system SHALL compute MAPE on the inverse-transformed test predictions.
- The system SHALL print a formatted metrics report.

### FR-08: Visualization Output
- The system SHALL generate a line plot:
    - Blue line: Actual closing prices (test set)
    - Orange dashed line: LSTM predicted prices
- The system SHALL label axes: X = "Trading Day", Y = "Close Price (USD)"
- The system SHALL save the plot as `output/<ticker>_prediction.png`.

### FR-09: Model Persistence
- The system SHALL save the trained model as `output/best_model.h5` (Keras).
- The system SHALL support loading and re-running inference without retraining.

---

## 4. Non-Functional Requirements

### NFR-01: Performance
- Training on 15 years of daily data (~3770 rows) SHALL complete in < 10 minutes on CPU.
- Inference (single test set pass) SHALL complete in < 2 seconds.

### NFR-02: Accuracy
- The system SHOULD achieve MAPE < 5% on AAPL data (2010–2025).

### NFR-03: Offline Operation
- The system SHALL NOT make any network calls during training or inference.
- All data SHALL be loaded from local CSV only.

### NFR-04: Reproducibility
- The system SHALL set random seeds for numpy and TensorFlow at startup.

### NFR-05: Usability
- Configuration (file path, ticker, window size, hyperparameters) SHALL be centralized in `config.py`.
- The system SHALL be runnable as a single Jupyter Notebook or `python main.py` command.

### NFR-06: Portability
- The system SHALL run on Windows, macOS, Linux, and Google Colab.

---

## 5. Dataset Specification

### Primary: 15Y Big Tech Stock Data (Kaggle)
| Field     | Type     | Description                          | Used?      |
|-----------|----------|--------------------------------------|------------|
| Date      | datetime | Trading date (YYYY-MM-DD)            | Index only |
| Open      | float    | Opening price                        | No         |
| High      | float    | Daily high price                     | No         |
| Low       | float    | Daily low price                      | No         |
| Close     | float    | **Closing price — primary feature**  | ✅ Yes      |
| Adj Close | float    | Dividend-adjusted close              | No         |
| Volume    | int      | Shares traded                        | No (base)  |

**Ticker used for base project:** AAPL  
**Date range used:** 2018-01-01 to 2025-01-01 (filtered from CSV)  
**Rows after filter:** ~1,762 trading days

---

## 6. Model & Algorithm Summary

| Component         | Algorithm / Method            | Purpose                              |
|-------------------|-------------------------------|--------------------------------------|
| Scaling           | MinMaxScaler                  | Normalize Close to [0,1]             |
| Sequencing        | Sliding Window (60 days)      | Create LSTM input sequences          |
| Primary Model     | Stacked LSTM (2 layers)       | Learn temporal price patterns        |
| Regularization    | Dropout (0.2)                 | Prevent overfitting                  |
| Optimization      | Adam Optimizer (lr=0.001)     | Gradient descent for weight update   |
| Loss              | Mean Squared Error (MSE)      | Training objective                   |
| Early Stopping    | EarlyStopping (patience=10)   | Avoid overtraining                   |
| Metric 1          | RMSE                          | Error in USD terms                   |
| Metric 2          | MAPE                          | Error as percentage                  |

---

## 7. Constraints
- Base model uses only the `Close` column (univariate) to keep complexity low.
- No intraday or tick data is used.
- LSTM cannot account for unexpected external events (earnings, news shocks).
- Predictions are point estimates; no confidence intervals in base version.

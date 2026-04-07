# Product Requirements Document (PRD)
## Stock Price Prediction using LSTM Neural Networks

**Version:** 2.0 (Updated — Static Dataset)  
**Author:** Sumit Patel  
**Date:** April 2026  
**Status:** Draft

---

## 1. Overview

### 1.1 Product Summary
A machine learning application that predicts future stock closing prices using a
Long Short-Term Memory (LSTM) neural network trained on a **static Kaggle CSV dataset**.
The system preprocesses the data, trains the LSTM model, and outputs predicted vs. actual
price visualizations alongside evaluation metrics.

### 1.2 Problem Statement
Stock prices are sequential and time-dependent. Traditional ML models ignore temporal order.
This project uses LSTM — a neural network built for sequence learning — to capture price
trends across 60-day windows and forecast future closing prices without relying on live APIs.

### 1.3 Goals
- Train an LSTM on a static, offline CSV dataset (no internet dependency during runtime)
- Predict next-day stock closing prices with MAPE < 5%
- Produce clear actual vs. predicted price visualizations
- Keep the pipeline simple: single stock (AAPL), single feature (Close price)

---

## 2. Dataset

### 2.1 Primary Dataset
| Property      | Details                                                           |
|---------------|-------------------------------------------------------------------|
| Name          | 15Y Big Tech Stock Data (NVDA, AAPL, MSFT, GOOGL, AMZN)         |
| Source        | Kaggle — marianadeem755                                           |
| Link          | kaggle.com/datasets/marianadeem755/stock-market-data             |
| Format        | CSV (one file per ticker or combined)                             |
| Date Range    | 2010-01-01 to 2025-01-01 (15 years, ~3,770 trading days)         |
| Columns       | Date, Open, High, Low, Close, Adj Close, Volume                   |
| Size          | ~lightweight, <5 MB total                                         |
| Downloaded    |  D:\LearningHub\CollegeProjects\ML_Project\Dataset\15 Years Stock Data of NVDA AAPL MSFT GOOGL and AMZN.csv                                  |

### 2.2 Alternative Dataset (AAPL Only)
| Property      | Details                                                           |
|---------------|-------------------------------------------------------------------|
| Name          | Apple (AAPL) Historical Stock Data                               |
| Source        | Kaggle — tarunpaparaju                                            |
| Link          | kaggle.com/datasets/tarunpaparaju/apple-aapl-historical-stock-data|
| Date Range    | 2010–2020 (~2,518 trading days)                                   |
| Format        | CSV                                                               |

### 2.3 Column Used
- **Input feature:** `Close` price only (univariate — keeps complexity low)
- **Date column:** Used as the time index for visualization only

---

## 3. Models & Algorithms

### 3.1 Core Algorithm — LSTM Neural Network
| Property           | Detail                                                        |
|--------------------|---------------------------------------------------------------|
| Algorithm Family   | Recurrent Neural Network (RNN)                               |
| Variant            | Long Short-Term Memory (LSTM)                                |
| Framework          | TensorFlow 2.x / Keras                                       |
| Architecture       | Stacked LSTM (2 layers) + Dropout + Dense output             |
| Input              | Sequences of 60 consecutive normalized closing prices        |
| Output             | Single predicted next-day closing price                      |
| Loss Function      | Mean Squared Error (MSE)                                     |
| Optimizer          | Adam (lr = 0.001)                                            |

### 3.2 Supporting Algorithms
| Step              | Algorithm / Method              | Library            |
|-------------------|---------------------------------|--------------------|
| Normalization     | MinMaxScaler                    | scikit-learn       |
| Sequence creation | Sliding Window (size = 60)      | numpy              |
| Evaluation        | RMSE, MAPE                      | numpy, scikit-learn|
| Visualization     | Line Plot (Actual vs Predicted) | matplotlib/plotly  |

---

## 4. Features

### 4.1 Core Features (Must Have)
- **F1** — Load stock CSV from local file system (no API call)
- **F2** — Preprocess: extract Close, normalize, create 60-day sequences
- **F3** — Train stacked LSTM model using TensorFlow/Keras
- **F4** — Evaluate model with RMSE and MAPE on test split
- **F5** — Plot Actual vs. Predicted prices and save as PNG
- **F6** — Save trained model as `.h5` file for reuse

### 4.2 Extended Features (Nice to Have)
- **F7** — Add technical indicators (MA50, RSI) as extra input features
- **F8** — Streamlit dashboard: upload CSV → get predictions
- **F9** — Multi-stock comparison (AAPL vs MSFT from same dataset)

### 4.3 Out of Scope
- Live data fetching or API integration
- Real-time trading or brokerage connectivity
- Intraday price prediction

---

## 5. Success Metrics

| Metric              | Target                     |
|---------------------|----------------------------|
| MAPE on test set    | < 5%                       |
| RMSE on test set    | < $5 (for AAPL-scale data) |
| Training time       | < 5 minutes on CPU         |
| Visualization       | Clear actual vs. predicted |

---

## 6. Tech Stack

| Component       | Technology                             |
|-----------------|----------------------------------------|
| Dataset         | Static CSV from Kaggle                 |
| Preprocessing   | pandas, numpy, scikit-learn            |
| Model           | TensorFlow 2.x / Keras (LSTM)          |
| Evaluation      | scikit-learn (RMSE), numpy (MAPE)      |
| Visualization   | matplotlib / plotly                    |
| Environment     | Python 3.10+, Jupyter Notebook / VS Code |
| Optional Deploy | Streamlit                              |

---

## 7. Timeline

| Phase                        | Duration  |
|------------------------------|-----------|
| Dataset download & EDA       | Day 1     |
| Preprocessing & sequencing   | Day 1–2   |
| Model build & training       | Day 2–3   |
| Evaluation & visualization   | Day 3     |
| Optional enhancements (F7/F8)| Day 4–5   |

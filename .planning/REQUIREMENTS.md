# Requirements
## Stock Price Prediction using LSTM Neural Networks

**Version:** 1.1  
**Last updated:** April 2026

---

## v1 Requirements

### Data Pipeline

- [ ] **DATA-01**: System loads stock data from local CSV file (data/AAPL.csv)
- [ ] **DATA-02**: System parses Date column as datetime index
- [ ] **DATA-03**: System displays basic statistics (row count, date range, min/max Close)
- [ ] **DATA-04**: System checks for and reports missing values in Close column
- [ ] **DATA-05**: System plots raw Close price history before training

### Preprocessing

- [x] **PREP-01**: System extracts Close column as sole input feature (univariate)
- [x] **PREP-02**: System applies MinMaxScaler fitted only on training data (prevents data leakage)
- [x] **PREP-03**: System creates input-output sequences using 60-day sliding window
- [x] **PREP-04**: System splits data 80/20 train/test without shuffling (preserves temporal order)
- [x] **PREP-05**: System reshapes sequences to (samples, timesteps, 1) for LSTM input

### Model Architecture

- [ ] **MODEL-01**: System implements stacked LSTM with 2 LSTM layers (64 units each)
- [ ] **MODEL-02**: System adds dropout layers (0.2) after each LSTM for regularization
- [ ] **MODEL-03**: System adds Dense layer (32 units, ReLU) for non-linear combination
- [ ] **MODEL-04**: System includes output layer (1 unit) for predicted closing price
- [ ] **MODEL-05**: System compiles model with Adam optimizer (lr=0.001) and MSE loss

### Training

- [ ] **TRAIN-01**: System trains for up to 100 epochs with batch_size=32
- [ ] **TRAIN-02**: System uses 10% validation split from training data
- [ ] **TRAIN-03**: System implements EarlyStopping (patience=10, monitor='val_loss')
- [ ] **TRAIN-04**: System saves best model weights using ModelCheckpoint
- [ ] **TRAIN-05**: System displays training/validation loss per epoch

### Evaluation & Output

- [ ] **EVAL-01**: System generates predictions on test set using trained model
- [ ] **EVAL-02**: System inverse-transforms predictions and actuals to USD prices
- [ ] **EVAL-03**: System computes and displays RMSE on test set
- [ ] **EVAL-04**: System computes and displays MAPE on test set
- [ ] **EVAL-05**: System generates line plot (Actual vs Predicted) and saves as PNG
- [ ] **EVAL-06**: System saves trained model as output/best_model.h5 for reuse

### Infrastructure & Configuration

- [ ] **INFRA-01**: System centralizes all hyperparameters in src/config.py
- [ ] **INFRA-02**: System uses modular structure (data_loader, preprocessor, model, trainer, evaluator, visualizer)
- [ ] **INFRA-03**: System provides main.py as entry point for full pipeline
- [ ] **INFRA-04**: System sets random seeds for numpy and TensorFlow (reproducibility)

### Autonomous Agent Capabilities

- [ ] **AUTO-01**: AI agent autonomously runs E2E pipeline verification and continuously monitors outputs (MAPE, RMSE, script stability)
- [ ] **AUTO-02**: AI agent autonomously diagnoses performance degradation (MAPE ≥ 5% or script failures) by analyzing logs and identifying bottlenecks
- [ ] **AUTO-03**: AI agent autonomously applies fixes (hyperparameter adjustments, data scaling corrections) and re-runs verification without human intervention
- [ ] **AUTO-04**: AI agent generates REPAIR-LOG.md documenting each autonomous change, rationale, and performance improvement results

---

## v2 Requirements (Deferred)

### Extended Features
- **EXTEND-01**: Add technical indicators (MA50, RSI) as extra input features
- **EXTEND-02**: Create Streamlit dashboard for CSV upload → predictions workflow
- **EXTEND-03**: Implement multi-stock comparison (AAPL vs MSFT from same dataset)
- **EXTEND-04**: Add multi-step forecasting (predict 5-day or 30-day ahead)
- **EXTEND-05**: Implement confidence intervals for predictions (probabilistic output)

### Advanced Model Features
- **MODEL-06**: Add Volume as secondary feature (multivariate LSTM)
- **MODEL-07**: Experiment with GRU as alternative to LSTM
- **MODEL-08**: Implement bidirectional LSTM
- **MODEL-09**: Add attention mechanism to LSTM architecture

### Deployment & Monitoring
- **DEPLOY-01**: Containerize application with Docker
- **DEPLOY-02**: Add model performance monitoring dashboard
- **DEPLOY-03**: Create API endpoint for prediction serving
- **DEPLOY-04**: Implement model versioning and rollback capability

---

## Out of Scope

- **Live API integration** — Reason: Project uses static CSV only; no yfinance/Alpha Vantage dependency
- **Intraday prediction** — Reason: Daily closing prices only; minute/hour granularity requires different architecture
- **Real-time trading integration** — Reason: No brokerage API connectivity; academic project focus
- **Automated retraining pipeline** — Reason: Static dataset means no new data arrives; manual retrain is sufficient
- **Cross-market prediction** — Reason: Single stock focus (AAPL); expanding to multiple markets adds complexity
- **Sentiment analysis integration** — Reason: Text processing out of scope; price-only focus
- **High-frequency trading** — Reason: Daily predictions only; HFT requires sub-second latency

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 1 | Pending |
| INFRA-01 | Phase 1 | Pending |
| INFRA-02 | Phase 1 | Pending |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| PREP-01 | Phase 2 | Complete |
| PREP-02 | Phase 2 | Complete |
| PREP-03 | Phase 2 | Complete |
| PREP-04 | Phase 2 | Complete |
| PREP-05 | Phase 2 | Complete |
| MODEL-01 | Phase 3 | Pending |
| MODEL-02 | Phase 3 | Pending |
| MODEL-03 | Phase 3 | Pending |
| MODEL-04 | Phase 3 | Pending |
| MODEL-05 | Phase 3 | Pending |
| TRAIN-01 | Phase 3 | Pending |
| TRAIN-02 | Phase 3 | Pending |
| TRAIN-03 | Phase 3 | Pending |
| TRAIN-04 | Phase 3 | Pending |
| TRAIN-05 | Phase 3 | Pending |
| EVAL-01 | Phase 4 | Pending |
| EVAL-02 | Phase 4 | Pending |
| EVAL-03 | Phase 4 | Pending |
| EVAL-04 | Phase 4 | Pending |
| EVAL-05 | Phase 4 | Pending |
| EVAL-06 | Phase 4 | Pending |
| AUTO-01 | Phase 5 | Pending |
| AUTO-02 | Phase 5 | Pending |
| AUTO-03 | Phase 5 | Pending |
| AUTO-04 | Phase 5 | Pending |

---

## Success Criteria

### Core Value Delivery
✓ **MAPE < 5%** on test set  
✓ **RMSE < $5** on AAPL data  
✓ **Training time < 5 minutes** on CPU  
✓ **Clear visualization** of actual vs predicted prices

### Technical Completeness
✓ All 33 v1 requirements implemented and tested (29 base + 4 AUTO)  
✓ Modular code structure with separation of concerns  
✓ Reproducible results (random seed set)  
✓ Model persistence (saved .h5 file)  
✓ Autonomous agent self-correction capabilities

### Documentation
✓ README with usage instructions  
✓ requirements.txt for dependency management  
✓ Code comments explaining key decisions  
✓ Output plots clearly labeled

---

## Notes

**Data Leakage Prevention:**
The scaler MUST be fitted on training data only and then applied to test data. This is critical for correctness — fitting on the entire dataset would leak future information into the model.

**Temporal Order Preservation:**
Train/test split must NOT shuffle data. Shuffling breaks temporal dependencies and creates look-ahead bias where the model learns from future data.

**Window Size Rationale:**
60 trading days ≈ 3 months. This captures quarterly trends without requiring excessive memory or training time. Too small (e.g., 10 days) misses long-term patterns; too large (e.g., 250 days) reduces training samples.

**Architecture Choices:**
- **Stacked LSTM**: Two layers capture both short-term and long-range dependencies
- **Dropout 0.2**: Industry standard for financial time-series; prevents overfitting
- **Adam optimizer**: Adaptive learning rate handles MSE loss landscape well
- **MSE loss**: Standard for regression; penalizes large errors more than small ones

**Success Metrics:**
- **MAPE < 5%**: Indicates strong predictive accuracy for next-day forecasts
- **RMSE < $5**: Absolute error threshold appropriate for AAPL price scale (~$150-180)

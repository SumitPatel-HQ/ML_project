# Roadmap
## Stock Price Prediction using LSTM Neural Networks

**Granularity:** Coarse  
**Total Requirements:** 29  
**Coverage:** 29/29 (100%)

---

## Phases

- [ ] **Phase 1: Project Setup & Data Pipeline** - Initialize structure, load and validate CSV data
- [ ] **Phase 2: Preprocessing & Sequence Generation** - Transform raw data into LSTM-ready sequences
- [ ] **Phase 3: Model Architecture & Training** - Build stacked LSTM and train with regularization
- [ ] **Phase 4: Evaluation & Visualization** - Generate predictions, compute metrics, and create plots

---

## Phase Details

### Phase 1: Project Setup & Data Pipeline

**Goal**: User can load AAPL CSV data and view exploratory statistics and raw price visualization

**Depends on**: Nothing (first phase)

**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, INFRA-01, INFRA-02, INFRA-03, INFRA-04

**Success Criteria** (what must be TRUE):
1. User runs main.py and sees printed statistics (row count, date range, price min/max)
2. User sees "Missing values: 0" confirmation in console output
3. User sees saved PNG file (output/raw_price.png) showing 2018-2025 AAPL closing prices
4. User can modify hyperparameters in src/config.py and see changes take effect
5. Code structure matches specified layout (src/ folder with config.py, data_loader.py, etc.)

**Plans**: TBD

---

### Phase 2: Preprocessing & Sequence Generation

**Goal**: User can transform raw CSV data into normalized 60-day sequences ready for LSTM training

**Depends on**: Phase 1

**Requirements**: PREP-01, PREP-02, PREP-03, PREP-04, PREP-05

**Success Criteria** (what must be TRUE):
1. User sees printed shapes: X_train (samples, 60, 1), X_test (samples, 60, 1)
2. User confirms scaler was fit on training data only (no data leakage)
3. User verifies 80/20 split without shuffling (temporal order preserved)
4. User sees confirmation that Close column was extracted and normalized to [0,1]
5. User can inspect first sequence and verify it contains 60 consecutive normalized prices

**Plans**: TBD

---

### Phase 3: Model Architecture & Training

**Goal**: User can train a stacked LSTM model that learns temporal patterns and saves best weights

**Depends on**: Phase 2

**Requirements**: MODEL-01, MODEL-02, MODEL-03, MODEL-04, MODEL-05, TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04, TRAIN-05

**Success Criteria** (what must be TRUE):
1. User sees model summary showing 2 LSTM layers (64 units) + Dropout + Dense architecture
2. User sees training progress with loss and val_loss printed each epoch
3. User confirms EarlyStopping triggered before 100 epochs (e.g., stopped at epoch 35)
4. User sees "Model saved to output/best_model.h5" confirmation message
5. Training completes in < 5 minutes on CPU without errors

**Plans**: TBD

---

### Phase 4: Evaluation & Visualization

**Goal**: User can generate predictions, see MAPE < 5%, and view actual vs predicted price plot

**Depends on**: Phase 3

**Requirements**: EVAL-01, EVAL-02, EVAL-03, EVAL-04, EVAL-05, EVAL-06

**Success Criteria** (what must be TRUE):
1. User sees printed metrics showing MAPE < 5% and RMSE < $5
2. User sees saved PNG file (output/AAPL_prediction.png) with actual (blue) vs predicted (orange dashed) lines
3. User confirms predictions were inverse-transformed back to USD prices
4. User can reload saved model from output/best_model.h5 and re-run inference without retraining
5. Plot axes are labeled correctly: X = "Trading Days (Test Set)", Y = "Close Price (USD)"

**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Setup & Data Pipeline | 0/? | Not started | - |
| 2. Preprocessing & Sequence Generation | 0/? | Not started | - |
| 3. Model Architecture & Training | 0/? | Not started | - |
| 4. Evaluation & Visualization | 0/? | Not started | - |

---

## Notes

**Phase Derivation:**
Phases follow the natural ML pipeline flow: Setup → Prepare Data → Train Model → Evaluate Results. Each phase delivers a complete, verifiable capability.

**Coarse Granularity:**
With 4 phases for 29 requirements, each phase contains 5-10 requirements. This keeps planning lightweight while maintaining clear delivery boundaries.

**Dependencies:**
Strict linear dependency chain (1 → 2 → 3 → 4) reflects the sequential nature of ML pipelines — you cannot train without preprocessed data, and you cannot evaluate without a trained model.

**Success Criteria Format:**
All criteria are user-observable behaviors (what the user can see, verify, or inspect), not implementation details. This makes phase completion unambiguous.

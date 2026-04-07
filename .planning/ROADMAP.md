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
- [ ] **Phase 5: Autonomous Correction & Performance Optimization Loop** - Enable AI agent to manage Test → Diagnose → Fix → Re-verify loop

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

**Plans**: 3 plans in 3 waves

Plans:
- [x] 01-01-PLAN.md — Project structure, configuration, and utilities (Wave 1)
- [x] 01-02-PLAN.md — Data loading with validation and statistics (Wave 2)
- [ ] 01-03-PLAN.md — Visualization and main entry point (Wave 3)

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

**Plans**: 2 plans in 2 waves

Plans:
- [x] 02-01-PLAN.md — TDD preprocessing contract, metadata, and proof formatter (Wave 1)
- [x] 02-02-PLAN.md — Wire preprocessing proof output into main pipeline (Wave 2)

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

**Plans**: 3 plans in 3 waves

Plans:
- [ ] 03-01-PLAN.md — TDD model architecture contract and lazy TensorFlow loading (Wave 1)
- [ ] 03-02-PLAN.md — TDD trainer bundle, callbacks, sidecar, and training summary (Wave 2)
- [ ] 03-03-PLAN.md — Wire Phase 3 model/trainer output into the CLI pipeline (Wave 3)

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

### Phase 5: Autonomous Correction & Performance Optimization Loop

**Goal**: Enable the AI agent to autonomously manage a "Test → Diagnose → Fix → Re-verify" loop to guarantee the project's core performance metrics

**Depends on**: Phase 4

**Requirements**: AUTO-01, AUTO-02, AUTO-03, AUTO-04

**Success Criteria** (what must be TRUE):
1. The AI agent successfully identifies a simulated "performance drop" (e.g., forced MAPE ≥ 5% failure) and restores MAPE to < 5% autonomously
2. A REPAIR-LOG.md is generated, documenting every autonomous change, its rationale, and the resulting performance improvement
3. The agent autonomously runs E2E pipeline verification and monitors outputs (MAPE, RMSE, script stability)
4. If any metric fails, the agent autonomously analyzes logs, identifies bottlenecks (e.g., hyperparameters, data scaling), and applies fixes without human intervention
5. The loop continues until the project consistently meets all Success Criteria across multiple consecutive runs, achieving a "Self-Correcting" state

**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Setup & Data Pipeline | 0/? | Not started | - |
| 2. Preprocessing & Sequence Generation | 0/? | Not started | - |
| 3. Model Architecture & Training | 0/? | Not started | - |
| 4. Evaluation & Visualization | 0/? | Not started | - |
| 5. Autonomous Correction & Performance Optimization Loop | 0/? | Not started | - |

---

## Notes

**Phase Derivation:**
Phases follow the natural ML pipeline flow: Setup → Prepare Data → Train Model → Evaluate Results → Autonomous Optimization. Phase 5 adds a self-healing layer where the AI agent autonomously maintains model quality through continuous verification and correction loops.

**Coarse Granularity:**
With 5 phases for 29+ requirements, each phase contains 4-10 requirements. This keeps planning lightweight while maintaining clear delivery boundaries. Phase 5 focuses specifically on autonomous agent capabilities.

**Dependencies:**
Linear dependency chain (1 → 2 → 3 → 4 → 5) reflects both the sequential nature of ML pipelines and the requirement that autonomous optimization can only occur after the complete pipeline is functional.

**Success Criteria Format:**
All criteria are user-observable behaviors (what the user can see, verify, or inspect), not implementation details. This makes phase completion unambiguous.

# Phase 3: Model Architecture & Training - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the stacked LSTM model and training stage on top of the existing preprocessing pipeline, train it with regularization and callbacks, and save the best model artifact for downstream evaluation. Prediction generation, metrics, and comparison plots remain in Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Training UX
- **D-01:** Training should show live per-epoch `loss` and `val_loss` output during fit, then end with a concise custom summary instead of relying on raw Keras output alone.
- **D-02:** The final summary should emphasize the best epoch, whether EarlyStopping triggered, and the saved model path so Phase 3 success is easy to verify from the CLI.

### Saved Artifacts
- **D-03:** Phase 3 must save the required best model artifact at `output/best_model.h5`.
- **D-04:** Phase 3 should also save a lightweight training sidecar focused on training history and metadata, not a large diagnostics bundle.
- **D-05:** The sidecar should capture training metadata such as epochs run, best validation loss, best epoch, stopped epoch, config values used, and checkpoint path.

### TensorFlow Dependency Behavior
- **D-06:** TensorFlow imports should stay localized to model and trainer code so non-training modules and lightweight tests can still import without TensorFlow installed.
- **D-07:** Missing TensorFlow should raise a clear error when model build or training is invoked, not at general module import time.

### Phase 4 Handoff
- **D-08:** Phase 3 should expose a structured training-result bundle rather than loose tuple returns or a saved-model-only handoff.
- **D-09:** That bundle should include the trained model handle, training history, checkpoint path, and training metadata needed by Phase 4 and verification.
- **D-10:** The Phase 3 handoff should mirror the structured-bundle style already established by `src.preprocessor.preprocess()`.

### the agent's Discretion
- Exact helper/function names in `src/model.py` and `src/trainer.py`
- Internal formatting details of the training sidecar file
- Exact wording/layout of the final CLI summary as long as it highlights the locked proof points above

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and locked requirements
- `.planning/ROADMAP.md` — Phase 3 goal, dependency on Phase 2, and user-visible success criteria for model training
- `.planning/PROJECT.md` — project constraints, offline-only rule, locked model/training defaults, and target outputs
- `.planning/REQUIREMENTS.md` — `MODEL-01` through `MODEL-05` and `TRAIN-01` through `TRAIN-05` define the required architecture and training behavior

### Detailed model and training specs
- `.docs/SRS_StockPrediction_LSTM.md` — FR-04 and FR-05 define the stacked LSTM layers, dropout, Dense/output layers, callbacks, and training-output expectations
- `.docs/TDD_StockPrediction_LSTM.md` — section 4.4 (`model.py`) and section 4.5 (`trainer.py`) describe the intended builder/trainer split, callback setup, and recommended hyperparameter wiring
- `.docs/PRD_StockPrediction_LSTM.md` — product-level rationale for stacked LSTM, offline execution, and CPU-time constraints

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/config.py` — already centralizes all Phase 3 hyperparameters and artifact paths, so model/trainer code should read from one config source
- `src.preprocessor.py` — already returns a structured preprocessing bundle; this is the established contract style to mirror for training outputs
- `src/utils.py` — already sets random seeds and uses an optional TensorFlow import pattern that supports lightweight test environments
- `main.py` — already orchestrates the pipeline in phase order with concise banners and proof-style console output

### Established Patterns
- `src/config.py` keeps project constants centralized rather than scattering literals across modules
- `src.preprocessor.py` uses small helpers plus a single public orchestration function that returns both payload data and metadata
- `main.py` presents each phase with clear CLI banners and short proof output instead of dumping raw objects
- `src.utils.py` keeps heavy ML dependencies optional until needed, which is relevant for Phase 3 import/error behavior

### Integration Points
- `main.py` should extend the existing Phase 1/2 flow by invoking Phase 3 immediately after preprocessing completes
- Phase 3 should consume the preprocessing bundle (`X_train`, `y_train`, `X_test`, `y_test`, scaler metadata) produced by `src.preprocessor.preprocess()`
- Saved training artifacts should live under `output/`, matching current output handling in `src.utils.py` and `src.visualizer.py`
- Phase 4 evaluation should consume the structured training-result bundle and/or its saved sidecar instead of reconstructing training context from scratch

</code_context>

<specifics>
## Specific Ideas

- Keep the existing phase-banner CLI style from `main.py`, but add live epoch logs during model fitting.
- End training with a short proof-style summary focused on best epoch, EarlyStopping result, and saved checkpoint path.
- Mirror the structured return shape of `src.preprocessor.preprocess()` when designing the Phase 3 training result contract.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-model-architecture-training*
*Context gathered: 2026-04-08*

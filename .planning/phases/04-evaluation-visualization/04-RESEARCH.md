# Phase 04 Research: Evaluation & Visualization

**Date:** 2026-04-08
**Status:** Complete

## Objective

Research the implementation shape for Phase 4 so planning can be concrete, low-risk, and aligned with the existing Phase 2/3 bundle contracts.

## Inputs Reviewed

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/04-evaluation-visualization/04-CONTEXT.md`
- `.planning/phases/02-preprocessing-sequence-generation/02-CONTEXT.md`
- `.planning/phases/03-model-architecture-training/03-CONTEXT.md`
- `.planning/phases/02-preprocessing-sequence-generation/*-SUMMARY.md`
- `.planning/phases/03-model-architecture-training/*-SUMMARY.md`
- `.docs/SRS_StockPrediction_LSTM.md`
- `.docs/TDD_StockPrediction_LSTM.md`
- `.docs/PRD_StockPrediction_LSTM.md`
- `.docs/prompt.md`
- `main.py`, `src/config.py`, `src/preprocessor.py`, `src/model.py`, `src/trainer.py`, `src/visualizer.py`

## Locked Decisions To Preserve

- Use the structured Phase 3 training-result bundle as the primary evaluation path when available (D-01).
- Reload `output/best_model.h5` and run a smoke-test inference to prove reuse without retraining (D-02).
- Print a concise CLI metrics summary, not arrays or verbose diagnostics (D-03).
- Save a lightweight `output/metrics.json` containing RMSE, MAPE, thresholds, and pass/fail state (D-04, D-05).
- Save exactly one comparison chart at `output/AAPL_prediction.png` with metrics in the title and locked axis labels (D-06, D-07, D-08).
- Treat missing artifacts/inference/transform/write failures as hard errors, but threshold misses as non-blocking failures recorded in outputs (D-09, D-10).

## Existing Code Contracts

### Preprocessing bundle

`src.preprocessor.preprocess()` already returns:

- `X_train`, `y_train`, `X_test`, `y_test`
- `scaler`
- `metadata` with shape/date/split proof fields

This is the Phase 4 source of truth for test tensors, scaled targets, and inverse transformation.

### Training bundle

`src.trainer.train_model()` already returns:

- `model`
- `history`
- `checkpoint_path`
- `sidecar_path`
- `metadata`

This makes the in-memory trained model the correct primary inference path, while `checkpoint_path` is the correct saved-model reuse proof path.

### CLI pattern

`main.py` already prints phase banners plus concise proof blocks. Phase 4 should extend that pattern rather than inventing a separate reporting style.

## Implementation Recommendations

### 1. Add a dedicated evaluator module

Create `src/evaluator.py` with a small public API that:

- consumes the Phase 3 training bundle plus Phase 2 preprocessing bundle
- runs `model.predict(X_test, verbose=0)` on the in-memory trained model
- inverse-transforms predictions and `y_test` back to USD with the fitted scaler
- computes RMSE and MAPE on USD prices
- writes `output/metrics.json`
- returns a structured evaluation bundle for CLI and plotting

Recommended bundle fields:

- `predictions_usd`
- `actual_usd`
- `predictions_scaled`
- `metrics`
- `metrics_path`
- `checkpoint_path`
- `model_reuse`

### 2. Keep TensorFlow loading lazy for reload proof

Follow the Phase 3 pattern: isolate `tensorflow.keras.models.load_model` inside a helper so tests and non-runtime imports stay lightweight.

Recommended helper:

- `reload_model_for_inference(model_path, X_test)` or equivalent

It should:

- raise a clear runtime error if TensorFlow is unavailable
- load the `.h5` model from `checkpoint_path`
- run a small inference call (prefer `X_test[:1]` for the smoke test)
- return minimal proof data such as prediction shape and path used

### 3. Add explicit evaluation config constants

`src/config.py` should expose stable constants for:

- `METRICS_FILE = "metrics.json"`
- `RMSE_TARGET = 5.0`
- `MAPE_TARGET = 5.0`
- optionally `TICKER = "AAPL"` if plotting/title code needs a central label

This matches the established “config-first” repo pattern.

### 4. Extend visualizer instead of creating a second plotting module

`src/visualizer.py` already handles save-to-file matplotlib output and explicit `plt.close(fig)`. Extend it with a Phase 4 helper instead of creating a new plotting file.

Recommended behavior:

- actual line: blue solid
- predicted line: orange dashed
- x-axis: simple test-set trading-day index
- y-axis: `Close Price (USD)`
- title includes ticker, RMSE, MAPE
- save to `output/AAPL_prediction.png`
- no `plt.show()` requirement for pipeline execution

### 5. Wire Phase 4 in `main.py` after training

Recommended sequence:

1. Run Phase 1
2. Run Phase 2
3. Run Phase 3
4. Call evaluator on the training + preprocessing bundles
5. Print concise evaluation summary
6. Save prediction plot using actual/predicted USD arrays
7. Print final output block including metrics artifact and prediction plot

If Phase 3 is skipped because only metadata stubs are present, Phase 4 should also skip or fail deterministically based on missing model inputs. For real runtime, missing Phase 3 model artifacts should be treated as a hard error per D-09.

## Metrics Notes

- Context7 confirms standard scikit-learn RMSE usage via `mean_squared_error(..., squared=False)` or `root_mean_squared_error(...)` when available.
- For compatibility with the current lightweight test setup, `numpy.sqrt(mean_squared_error(...))` is the safest implementation.
- MAPE can be computed with NumPy directly. Since stock close prices should not be zero, zero-valued actuals should be guarded and treated as invalid evaluation input instead of silently dividing by zero.

## Testing Strategy

### Contract-first tests

Use fake runtime objects, matching the existing Phase 3 style:

- fake model with `predict()`
- fake scaler with `inverse_transform()`
- monkeypatched TensorFlow `load_model`
- temp directory for metrics file creation

### Recommended test files

- `tests/test_evaluator.py`
  - validates primary inference path
  - validates inverse-transform behavior
  - validates RMSE/MAPE values and metrics artifact shape
  - validates saved-model reload smoke test
  - validates hard-error paths
- `tests/test_main_phase4.py`
  - validates CLI Phase 4 banner/output and wiring
- optionally `tests/test_visualizer_predictions.py`
  - validates plot helper labels/title/output path without relying on manual inspection

## Risks / Pitfalls

1. **Shape mismatch during inverse transform**
   - `MinMaxScaler.inverse_transform()` expects 2D arrays.
   - Always reshape predictions and targets to `(n, 1)` before inverse transform.

2. **Threshold failure accidentally aborting the phase**
   - D-10 explicitly forbids this.
   - Threshold status belongs in metrics output, not exception control flow.

3. **Heavy TensorFlow import breaking lightweight tests**
   - Keep load-model imports inside call sites, mirroring Phase 3.

4. **Plot helper drifting from locked labels**
   - Hard-code the exact axis strings in tests: `Trading Days (Test Set)` and `Close Price (USD)`.

5. **Windows console compatibility regressions**
   - Reuse ASCII-safe console output style from recent Phase 3 fixes.

## Recommended Planning Split

### Plan 04-01

Build the evaluation contract and artifact writer:

- `src/evaluator.py`
- `tests/test_evaluator.py`
- `src/config.py` constants if needed

### Plan 04-02

Build plotting + CLI wiring:

- extend `src/visualizer.py`
- add Phase 4 main-pipeline tests/wiring
- connect evaluator bundle to CLI output and saved plot

## Research Outcome

No new dependency is needed. Phase 4 should be implemented by extending the current config-first, structured-bundle, proof-oriented CLI architecture.

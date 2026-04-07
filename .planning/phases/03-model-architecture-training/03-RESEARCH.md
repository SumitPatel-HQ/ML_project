# Phase 03 Research — Model Architecture & Training

**Date:** 2026-04-08
**Scope:** TensorFlow/Keras model construction, callback-driven training, artifact persistence, and lightweight testability for Phase 3.

## Key Findings

1. **Keras Sequential is a good fit for the locked architecture.**
   - A `Sequential` model cleanly matches the required stack: `LSTM(64, return_sequences=True)` → `Dropout(0.2)` → `LSTM(64)` → `Dropout(0.2)` → `Dense(32, activation="relu")` → `Dense(1)`.
   - Compile with Adam and MSE exactly as required by `MODEL-05`.

2. **Per-epoch `loss` and `val_loss` can come from `model.fit(..., verbose=2)`.**
   - This keeps output concise while still printing one line per epoch.
   - A separate formatter should print the final proof summary required by `D-01` and `D-02`.

3. **Training control should use standard Keras callbacks.**
   - `EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True, verbose=1)` satisfies `TRAIN-03`.
   - `ModelCheckpoint(filepath="output/best_model.h5", monitor="val_loss", save_best_only=True, verbose=1)` satisfies `TRAIN-04` and `D-03`.

4. **Structured handoff should mirror the Phase 2 preprocessing bundle.**
   - Return a dictionary bundle from training with stable keys for the trained model, raw history, checkpoint path, and metadata.
   - Include metadata needed by Phase 4: epochs requested, epochs run, best epoch, best validation loss, stopped epoch, callback config, and sidecar path.

5. **TensorFlow imports should stay inside model/trainer runtime helpers.**
   - Do not import TensorFlow at module top level in modules that need to remain lightweight.
   - Raise a targeted runtime error only when model build or training is invoked, matching `D-06` and `D-07`.

6. **The training sidecar should be JSON, not a heavy diagnostics artifact.**
   - JSON keeps it readable, small, and Phase-4-friendly.
   - Recommended contents: `history.loss`, `history.val_loss`, `epochs_run`, `best_epoch`, `best_val_loss`, `early_stopped`, `stopped_epoch`, `checkpoint_path`, and config values used.

## Recommended Implementation Shape

### `src/model.py`
- `build_model(input_shape=None, cfg=None)`
- `format_model_summary(model)` or equivalent helper that captures `model.summary()` into text lines for CLI output
- internal runtime helper that imports TensorFlow/Keras only when called

### `src/trainer.py`
- `train_model(model, preprocessing_bundle, cfg=None)`
- `format_training_summary(training_bundle)`
- internal helpers for callback creation, training metadata extraction, and sidecar writing

### `main.py`
- Extend pipeline after Phase 2
- Print Phase 3 banner
- Print model summary
- Run training
- Print concise proof summary with best epoch, EarlyStopping status, model path, and sidecar path

## Testing Strategy

1. **Model contract tests** should verify layer types/configuration, optimizer learning rate, MSE loss, and missing-TensorFlow runtime failure.
2. **Trainer contract tests** should use stubs/mocks for model fit and callback classes so tests stay fast and do not require a full TensorFlow install.
3. **Main integration test** should monkeypatch model/trainer functions and assert Phase 3 banners plus proof strings appear in CLI output.

## Risks / Pitfalls

- `ModelCheckpoint` with `.h5` requires full-model save semantics compatible with installed TensorFlow/Keras version; keep the exact path `output/best_model.h5` because it is a locked requirement.
- Top-level TensorFlow imports would break lightweight test environments; keep imports localized.
- Relying only on raw Keras fit output would miss the proof-style summary required by the user decisions.
- Training metadata should be derived from `History.history["val_loss"]` rather than guessed from callback messages.

## Recommendation for Planning

Split Phase 3 into three waves:

1. **Wave 1:** TDD model contract and localized TensorFlow loading.
2. **Wave 2:** TDD trainer bundle, callbacks, sidecar, and training summary.
3. **Wave 3:** Main-pipeline wiring and CLI proof output.

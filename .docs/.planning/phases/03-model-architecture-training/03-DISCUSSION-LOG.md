# Phase 3: Model Architecture & Training - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 03-model-architecture-training
**Areas discussed:** Training UX, Saved Artifacts, TensorFlow/Test Strategy, Phase 4 Handoff

---

## Training UX

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid | Show the Keras per-epoch loss/val_loss stream during training, then print a short final summary in the existing `main.py` style. | ✓ |
| Verbose only | Leave output entirely to Keras epoch logs with no custom summary. | |
| Compact only | Hide most epoch-by-epoch output and print only milestone summaries. | |

**User's choice:** Hybrid
**Notes:** Final summary should emphasize the best epoch, EarlyStopping outcome, and saved model path.

---

## Saved Artifacts

| Option | Description | Selected |
|--------|-------------|----------|
| History JSON | Save the best model plus a lightweight training history/metadata file for later inspection. | ✓ |
| Model only | Save only `best_model.h5`. | |
| Many artifacts | Save model, history, per-epoch CSV, plots, and diagnostics now. | |

**User's choice:** History JSON
**Notes:** The sidecar should focus on training metadata: epochs run, best validation loss, stopped epoch, config values used, and checkpoint path.

---

## TensorFlow/Test Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Import guard + clear error | Keep TensorFlow imports localized to model/training code and raise a direct error only when training/model build is invoked. | ✓ |
| Hard fail on import | Import TensorFlow at module load everywhere and fail immediately if missing. | |
| Mock training fallback | Provide fake model/training behavior without TensorFlow. | |

**User's choice:** Import guard + clear error
**Notes:** Failure should surface at build/train call time, not during general module import or early pipeline setup.

---

## Phase 4 Handoff

| Option | Description | Selected |
|--------|-------------|----------|
| Structured bundle | Return a training result bundle with model handle, history, checkpoint path, and training metadata. | ✓ |
| Saved model only | Phase 4 reloads everything from disk and ignores in-memory training details. | |
| Loose tuple values | Return several separate values from training functions. | |

**User's choice:** Structured bundle
**Notes:** Bundle should include model, history, checkpoint path, and metadata like best epoch / best val_loss / epochs_run, and should mirror the structured style already used by preprocessing.

---

## the agent's Discretion

- Helper and function names inside `src/model.py` and `src/trainer.py`
- Exact sidecar filename and serialization layout
- Exact CLI wording beyond the required proof points

## Deferred Ideas

None.

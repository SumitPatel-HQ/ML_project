# Phase 4: Evaluation & Visualization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 04-evaluation-visualization
**Areas discussed:** Inference path, Metrics output, Prediction plot, Failure policy

---

## Inference path

### Primary evaluation path

| Option | Description | Selected |
|--------|-------------|----------|
| Use both paths | Run evaluation from the training-result bundle when available, then perform a saved-model reload check from `output/best_model.h5`. | ✓ |
| Reload model first | Always load `output/best_model.h5` and use that model for evaluation. | |
| In-memory only | Evaluate only the just-trained model and skip explicit reload verification. | |

**User's choice:** Use both paths
**Notes:** Keep the structured handoff as the main evaluation route, but explicitly prove saved-model reuse too.

### Saved-model proof depth

| Option | Description | Selected |
|--------|-------------|----------|
| Smoke test reload | Load `output/best_model.h5`, run inference on `X_test`, and confirm predictions can be generated without retraining. | ✓ |
| Parity check too | Reload the model and compare predictions/metrics against the primary path. | |
| Reload only message | Only confirm the file loads successfully. | |

**User's choice:** Smoke test reload
**Notes:** Persistence proof should be real inference, but not a heavier parity-analysis workflow.

---

## Metrics output

### Reporting style

| Option | Description | Selected |
|--------|-------------|----------|
| Console + JSON | Print concise CLI metrics and save `output/metrics.json`. | ✓ |
| Console only | Human-facing output only. | |
| Rich evaluation bundle | Save a larger evaluation artifact with extra payload data. | |

**User's choice:** Console + JSON
**Notes:** Keep the CLI readable while also creating a machine-readable artifact for later verification and automation.

### JSON scope

| Option | Description | Selected |
|--------|-------------|----------|
| Metrics + pass/fail | Save RMSE, MAPE, thresholds, and pass/fail status. | ✓ |
| Raw metrics only | Save just RMSE and MAPE values. | |
| Full run snapshot | Save metrics plus broader metadata and artifact details. | |

**User's choice:** Metrics + pass/fail
**Notes:** The artifact should stay lightweight and focused rather than becoming another bulky sidecar.

---

## Prediction plot

### Plot content

| Option | Description | Selected |
|--------|-------------|----------|
| Comparison + metrics title | One actual-vs-predicted chart with RMSE and MAPE in the title. | ✓ |
| Plain comparison only | Only the two lines, with metrics elsewhere. | |
| Expanded diagnostics | Add extra panels or overlays. | |

**User's choice:** Comparison + metrics title
**Notes:** The plot should stay simple and readable, but visibly communicate the evaluation result.

### X-axis choice

| Option | Description | Selected |
|--------|-------------|----------|
| Trading-day index | Use test-set trading-day order on the x-axis. | ✓ |
| Actual dates | Use real calendar dates. | |
| Show both | Combine date information with test-set position. | |

**User's choice:** Trading-day index
**Notes:** This matches the Phase 4 roadmap success criteria directly.

---

## Failure policy

### Artifact and evaluation errors

| Option | Description | Selected |
|--------|-------------|----------|
| Fail fast | Stop immediately for missing model artifacts, failed inference, inverse-transform issues, or plot/metrics write failures. | ✓ |
| Warn and continue | Keep going where possible. | |
| Mixed handling | Separate core failures from optional artifact warnings. | |

**User's choice:** Fail fast
**Notes:** Phase 4 should preserve the project's strict correctness posture for broken evaluation flows.

### Threshold miss behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Report miss clearly | Finish evaluation, save artifacts, and mark target failures in CLI and JSON. | ✓ |
| Raise hard failure | Treat target misses as immediate pipeline failure. | |
| Soft warning only | Mention misses without explicit pass/fail tracking. | |

**User's choice:** Report miss clearly
**Notes:** Preserve evidence for later optimization loops instead of throwing it away.

# Phase 4: Evaluation & Visualization - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate test-set predictions from the trained LSTM pipeline, inverse-transform predictions and actual values back to USD prices, compute RMSE and MAPE, prove saved-model reuse, and save the final actual-vs-predicted visualization. Model architecture, training behavior, and autonomous repair logic remain outside this phase.

</domain>

<decisions>
## Implementation Decisions

### Inference path
- **D-01:** Phase 4 should use the structured Phase 3 training-result handoff as the primary evaluation path when it is available.
- **D-02:** Phase 4 must also reload `output/best_model.h5` and run a smoke-test inference on the test inputs to prove saved-model reuse without retraining.

### Metrics output
- **D-03:** Phase 4 should print a concise CLI metrics summary instead of verbose raw arrays or diagnostics output.
- **D-04:** Phase 4 must save a lightweight metrics artifact at `output/metrics.json`.
- **D-05:** `output/metrics.json` should contain RMSE, MAPE, the locked target thresholds, and pass/fail status for each target, not a large diagnostics bundle.

### Prediction plot
- **D-06:** Phase 4 should save one clear actual-vs-predicted comparison chart at `output/AAPL_prediction.png`.
- **D-07:** The plot title should include RMSE and MAPE so the evaluation result is visible directly on the artifact.
- **D-08:** The plot x-axis should use test-set trading-day index, and the y-axis should remain `Close Price (USD)`.

### Failure policy
- **D-09:** Missing model artifacts, failed inference, inverse-transform problems, and metrics/plot write failures are hard errors that should stop the pipeline immediately.
- **D-10:** Missing the performance targets (`MAPE < 5%`, `RMSE < $5`) should not block artifact generation; Phase 4 should still finish evaluation and mark the failures clearly in both CLI output and `output/metrics.json`.

### the agent's Discretion
- Exact helper/function names and internal evaluator bundle shape, as long as the locked outputs above are preserved.
- Exact CLI wording/layout for the concise evaluation summary.
- Exact plot styling details beyond the locked line-comparison content, title metrics, and axis labels.
- Exact key names inside `output/metrics.json`, as long as raw metrics, thresholds, and pass/fail statuses are all present.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and locked requirements
- `.planning/ROADMAP.md` - Phase 4 goal, dependency on Phase 3, and user-visible success criteria for evaluation, persistence proof, and plotting.
- `.planning/REQUIREMENTS.md` - `EVAL-01` through `EVAL-06`, project success thresholds, and evaluation/output traceability.
- `.planning/PROJECT.md` - offline-only constraint, AAPL-only scope, output expectations, and locked success metrics.

### Prior-phase contracts that Phase 4 depends on
- `.planning/phases/03-model-architecture-training/03-CONTEXT.md` - locked Phase 3 decisions for `output/best_model.h5`, structured training-result handoff, and concise proof-style CLI output.
- `.planning/phases/02-preprocessing-sequence-generation/02-CONTEXT.md` - locked preprocessing bundle contract, scaler handoff, test-sequence continuity, and proof-oriented metadata.

### Functional and technical specs
- `.docs/SRS_StockPrediction_LSTM.md` - FR-06 through FR-09 define prediction generation, inverse transform, RMSE/MAPE reporting, plot requirements, and model persistence expectations.
- `.docs/TDD_StockPrediction_LSTM.md` - section 4.6 (`evaluator.py`) and section 4.7 (`visualizer.py`) describe the intended metric computation, inverse transform flow, and actual-vs-predicted plot structure.
- `.docs/PRD_StockPrediction_LSTM.md` - features F4 through F6 and success metrics confirm evaluation, visualization, and saved-model outcomes.
- `.docs/prompt.md` - implementation rules lock the model path, prediction plot path, metrics targets, and expected evaluation output.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/config.py` - already centralizes the output paths, thresholds-related defaults, and plotting filenames that Phase 4 should reuse.
- `src/preprocessor.py` - already provides `X_test`, `y_test`, scaler, and metadata in a structured bundle that evaluation can consume directly.
- `src/visualizer.py` - already establishes the repo's lightweight matplotlib save-to-file pattern for plot helpers.
- `main.py` - already uses phase banners and concise proof-style console output, which Phase 4 should extend instead of replacing.
- `src/utils.py` - already prepares the output directory and follows the project's lightweight helper style.

### Established Patterns
- The project prefers centralized config values in `src/config.py` instead of scattering literals through modules.
- Earlier phases established structured bundle handoffs rather than loose tuple-only contracts.
- CLI output is kept concise and proof-oriented rather than dumping raw tensors or verbose internals.
- Optional heavy dependencies are isolated where possible, which matters for TensorFlow-backed inference and matplotlib-backed plotting behavior.

### Integration Points
- Phase 4 should plug into `main.py` immediately after the Phase 3 training flow is wired in.
- Phase 4 should consume the Phase 3 training-result bundle plus the saved model artifact at `output/best_model.h5`.
- Phase 4 should consume Phase 2 preprocessing outputs (`X_test`, `y_test`, scaler, metadata) for inference and inverse transform.
- Phase 4 should produce `output/metrics.json` and `output/AAPL_prediction.png` in a form that Phase 5 can inspect during autonomous verification and repair loops.

</code_context>

<specifics>
## Specific Ideas

- Keep evaluation aligned with the existing proof-style CLI flow: short summary in console, lightweight artifact on disk.
- Treat saved-model reuse as explicit proof work, not an implicit assumption.
- Keep the final visualization simple: one comparison chart, readable axes, and metrics in the title rather than a more diagnostic multi-panel analysis.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 04-evaluation-visualization*
*Context gathered: 2026-04-08*

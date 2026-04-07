# Phase 2: Preprocessing & Sequence Generation - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Transform the cleaned AAPL closing-price series from Phase 1 into normalized chronological sequences ready for LSTM training. This phase covers Close-only extraction, train-only-fitted scaling, 80/20 temporal splitting, 60-day sliding-window sequence generation, and LSTM-ready reshaping. Model construction, training, evaluation, and artifact-heavy output handling stay in later phases.

</domain>

<decisions>
## Implementation Decisions

### Preprocessor Contract
- **D-01:** `preprocess(...)` should return training and test tensors/targets, the fitted scaler, and lightweight preprocessing metadata rather than tensors alone.
- **D-02:** Required metadata includes the train/test split boundary with date-range context so downstream phases can verify chronological separation and leakage prevention.
- **D-03:** Required metadata includes window-construction details: feature name and window size used to build each sequence set.
- **D-04:** Required metadata includes sequence counts and tensor shapes for train and test outputs.

### Verification Output
- **D-05:** Phase 2 should emit a concise proof set rather than minimal or verbose diagnostics.
- **D-06:** The proof set must show `X_train`, `y_train`, `X_test`, and `y_test` shapes.
- **D-07:** The proof set must show the chronological split boundary or train/test date ranges.
- **D-08:** The proof set must show one first normalized input sequence preview plus its target value so the 60-step sequencing logic is inspectable.
- **D-09:** The proof set must confirm the training-fitted scaler normalized values into the expected `[0,1]` range.

### Failure Policy
- **D-10:** Preprocessing should fail fast with explicit, descriptive errors instead of warning-and-continue or silent auto-fixes.
- **D-11:** Phase 2 must raise explicit errors for missing `Close` data, including absent feature column or unresolved missing values.
- **D-12:** Phase 2 must raise explicit errors when the dataset is too short to produce at least one 60-day sequence after chronological splitting.
- **D-13:** Phase 2 must raise explicit errors for invalid preprocessing configuration such as unsafe window size or invalid train/test split settings.
- **D-14:** Phase 2 must raise explicit errors for scaling or sequencing mismatches that produce inconsistent shapes or invalid transformed output.

### Carried Forward Constraints
- **D-15:** Keep `Close` as the sole input feature for this phase.
- **D-16:** Use `MinMaxScaler` fitted on training data only, then apply it to downstream data.
- **D-17:** Preserve chronological order with an 80/20 train/test split and no shuffling.
- **D-18:** Keep the sliding window configurable with a default of 60 trading days.
- **D-19:** Preserve test-sequence continuity by seeding test preprocessing with the last training window before test rows.

### the agent's Discretion
- Exact metadata container shape (`dict`, dataclass, or equivalent) as long as the required fields above are present.
- Exact console formatting for the concise proof set.
- Exact wording of validation errors, as long as they clearly identify the violated preprocessing assumption.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and acceptance criteria
- `.planning/ROADMAP.md` — Phase 2 goal, dependency, and success criteria for preprocessing and sequence generation.
- `.planning/REQUIREMENTS.md` — `PREP-01` through `PREP-05`, traceability, and leakage-prevention notes.
- `.planning/PROJECT.md` — Project-wide constraints: offline execution, AAPL-only scope, univariate Close-price approach, and success targets.

### Functional and design specs
- `.docs/SRS_StockPrediction_LSTM.md` — FR-03 defines preprocessing behavior: Close-only extraction, train-only scaler fitting, chronological split, 60-day windowing, and LSTM input reshaping.
- `.docs/TDD_StockPrediction_LSTM.md` — Section 4.3 defines the intended preprocessing flow, return shape baseline, and continuity handling using the final training window before test rows.
- `.docs/PRD_StockPrediction_LSTM.md` — Feature F2 confirms Phase 2 scope: extract Close, normalize, and create 60-day sequences.
- `.docs/prompt.md` — Implementation rules reinforce train-only scaler fitting, test-sequence continuity, centralized config, and expected build order.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No existing `src/` implementation files were found yet, so there are no reusable runtime preprocessing assets in the codebase.
- `.docs/TDD_StockPrediction_LSTM.md` provides a reusable baseline function shape for `preprocess(df, cfg)` and `_create_sequences(...)` that planning can treat as the preferred starting contract.

### Established Patterns
- The documented architecture centers configuration in `src/config.py` and keeps logic modular by file (`data_loader`, `preprocessor`, `model`, `trainer`, `evaluator`, `visualizer`).
- The project consistently treats ML correctness constraints as explicit invariants: no data leakage, no temporal shuffling, and reproducible deterministic configuration.
- The docs favor function-based module APIs over framework-heavy abstractions.

### Integration Points
- Phase 2 consumes the cleaned dataframe produced by the Phase 1 data-loading pipeline.
- Phase 2 hands off normalized train/test tensors, targets, scaler, and metadata to the later model/training flow in Phase 3.
- Phase 2 verification output should appear in the same CLI-oriented execution path later driven by `main.py`.

</code_context>

<specifics>
## Specific Ideas

- Keep preprocessing inspectable without turning it into a noisy debugging phase.
- Prefer a lightweight metadata handoff that makes leakage checks and split validation obvious to downstream phases.
- Keep preprocessing strict: correctness beats convenience for this ML pipeline.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-preprocessing-sequence-generation*
*Context gathered: 2026-04-08*

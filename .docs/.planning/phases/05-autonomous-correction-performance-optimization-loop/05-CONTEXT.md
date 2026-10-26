# Phase 5: Autonomous Correction & Performance Optimization Loop - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Add an autonomous maintenance layer on top of the completed offline LSTM pipeline so the agent can run the full workflow, detect failures or metric regressions, diagnose likely causes, apply repairs, and re-verify until the system is stable. This phase does not change the project's core product scope: it must remain offline-only, AAPL-only, Close-only, and based on the stacked LSTM pipeline.

</domain>

<decisions>
## Implementation Decisions

### Repair boundaries
- **D-01:** The agent may make broad autonomous code edits during repair cycles, not just config-only tuning.
- **D-02:** Even with broad edit authority, these project constraints remain locked during repair: offline-only execution, AAPL-only scope, Close-only feature input, and stacked-LSTM base architecture.

### Verification protocol
- **D-03:** The repair system must support both deterministic failure injection and natural runtime regression detection.
- **D-04:** A verification run only counts as passing when the full pipeline exits cleanly, `MAPE < 5%`, `RMSE < $5`, and expected artifacts are generated.

### Rollback policy
- **D-05:** If an autonomous fix degrades performance or breaks the pipeline, the system must automatically revert.
- **D-06:** The rollback baseline is the last fully passing state that satisfied all verification checks, not merely the best single metric.

### Repair logging
- **D-07:** `REPAIR-LOG.md` should use a hybrid format: concise per-attempt entries plus a final summary of the winning or terminal outcome.
- **D-08:** Every repair entry must include before/after metrics and the agent's change rationale.

### Stop conditions
- **D-09:** The autonomous loop declares success only after 3 consecutive passing runs.
- **D-10:** The default unresolved budget is 2 repair attempts or 10 minutes elapsed, whichever comes first.

### the agent's Discretion
- The exact diagnosis heuristics, ranking logic for candidate fixes, and internal implementation of the repair controller are open to standard approaches as long as they obey the locked boundaries above.
- The exact structure of non-mandatory evidence in `REPAIR-LOG.md` (for example, whether to include changed-file lists, artifact paths, or command transcripts) is left to the agent unless later planning requires stricter audit detail.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project constraints and phase scope
- `.planning/PROJECT.md` — Core value, offline constraint, AAPL-only scope, Close-only feature, and success metrics that Phase 5 must preserve.
- `.planning/REQUIREMENTS.md` — `AUTO-01` through `AUTO-04` define the required autonomous verification, diagnosis, repair, and repair-log behavior.
- `.planning/ROADMAP.md` — Phase 5 goal, dependency on Phase 4, and user-observable success criteria.
- `.planning/STATE.md` — Current project status confirms the codebase is still in planning and that Phase 5 is additive to the original roadmap.
- `CLAUDE.md` — Current project constraints and GSD workflow expectations.

### Phase-specific docs
- `.planning/phases/5-autonomous-correction-performance-optimization-loop/PHASE.md` — Phase 5 objective, test scenarios, and the 3+ consecutive pass note that informed the stop condition.
- `.planning/phases/05-autonomous-correction-performance-optimization-loop/05-DISCUSSION-LOG.md` — Audit trail of alternatives considered during context capture.

### System design baseline
- `.docs/PRD_StockPrediction_LSTM.md` — Product goals, metric targets, and the baseline feature scope that autonomous repair must not expand.
- `.docs/TDD_StockPrediction_LSTM.md` — Intended module boundaries, pipeline flow, artifact outputs, and training/evaluation surfaces that Phase 5 should monitor and repair against.
- `.docs/SRS_StockPrediction_LSTM.md` — Functional and non-functional requirements for full-pipeline execution, metrics, offline operation, and reproducibility.
- `.docs/prompt.md` — Original build order and implementation rules for the baseline offline LSTM pipeline.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Planning artifacts in `.planning/` already define the target Phase 5 behavior, locked constraints, and success thresholds.
- Design artifacts in `.docs/` define the intended pipeline surfaces the autonomous loop will eventually observe: `main.py`, `src/config.py`, `src/trainer.py`, `src/evaluator.py`, and output artifacts such as `output/best_model.h5`, `output/AAPL_prediction.png`, and `output/metrics.json`.

### Established Patterns
- The only established pattern today is documentation-first planning; there is no implemented `src/` tree yet.
- Centralized configuration is an intended pattern from the design docs, so autonomous tuning should assume `src/config.py` is the primary future control surface.
- Metric-driven validation is already established in docs: clean execution, `MAPE`, `RMSE`, and output artifact checks are the baseline verification surfaces.

### Integration Points
- The future E2E execution entrypoint is `main.py`.
- The future evaluation hook is `src/evaluator.py`, where RMSE and MAPE are defined in the technical design.
- The future training hook is `src/trainer.py`, where callbacks and training behavior are defined.
- The future artifact verification surface is the `output/` directory, especially `output/best_model.h5`, `output/AAPL_prediction.png`, and `output/metrics.json`.
- `REPAIR-LOG.md` does not exist yet and must be introduced by this phase.

</code_context>

<specifics>
## Specific Ideas

- The self-healing loop should prove both deliberate failure recovery and real regression handling; it is not limited to one mode.
- The user explicitly wants broad autonomous repair authority, but without changing the project's foundational contract.
- Stability should mean repeated success, not a single lucky run.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-autonomous-correction-performance-optimization-loop*
*Context gathered: 2026-04-07*

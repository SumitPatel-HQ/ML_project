# Phase 5: Autonomous Correction & Performance Optimization Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `05-CONTEXT.md`.

**Date:** 2026-04-07
**Phase:** 05-autonomous-correction-performance-optimization-loop
**Areas discussed:** Repair boundaries, Verification protocol, Rollback policy, Repair logging, Stop conditions

---

## Repair boundaries

| Option | Description | Selected |
|--------|-------------|----------|
| Config-first only | Only tune values in config and retry runs; safest and easiest to audit. | |
| Config + pipeline internals | Allow targeted edits in preprocessing, training, and evaluation code, but keep core architecture and scope unchanged. | |
| Any project code | Allow broad autonomous code edits anywhere if they improve metrics. | ✓ |

**User's choice:** Any project code
**Notes:** Follow-up constraint question locked offline-only, AAPL-only, Close-only feature input, and stacked LSTM base architecture as non-negotiable.

---

## Locked project constraints during repair

| Option | Description | Selected |
|--------|-------------|----------|
| Keep offline-only | No network calls or live data sources may be introduced. | ✓ |
| Keep AAPL only | No multi-stock expansion as part of repair. | ✓ |
| Keep Close-only feature | Do not add Open/High/Low/Volume or indicators during repair. | ✓ |
| Keep stacked LSTM base | Do not replace the core model family with GRU, XGBoost, transformers, etc. | ✓ |
| Allow strategy changes | Agent may change feature set or model family if that helps performance. | |

**User's choice:** Keep offline-only, Keep AAPL only, Keep Close-only feature, Keep stacked LSTM base
**Notes:** Broad implementation edits are acceptable only inside the locked base product contract.

---

## Verification protocol

| Option | Description | Selected |
|--------|-------------|----------|
| Deterministic failure harness | Use explicit, reproducible failure modes like a bad config, broken threshold, or forced script error so the loop can prove recovery. | |
| Natural failures only | Only react to real failures encountered during normal runs; no deliberate failure injection. | |
| Both modes | Support a deliberate failure test plus normal runtime detection of genuine regressions. | ✓ |

**User's choice:** Both modes
**Notes:** The autonomous system must prove recovery under simulation and handle organic regressions too.

---

## Verification pass criteria

| Option | Description | Selected |
|--------|-------------|----------|
| Pipeline exits cleanly | The full run completes without script or runtime errors. | ✓ |
| MAPE under 5% | Primary performance target must pass. | ✓ |
| RMSE under 5 | Absolute-error target must pass. | ✓ |
| Artifacts generated | Expected outputs like model file, plot, and metrics/log files must exist. | ✓ |
| Repeatability check | A pass only counts if results remain acceptable across repeated runs. | |

**User's choice:** Pipeline exits cleanly, MAPE under 5%, RMSE under 5, Artifacts generated
**Notes:** Repeatability was not made part of a single-pass definition because stability is handled separately through consecutive successful runs.

---

## Rollback policy

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-revert to best | Restore the last known good state and continue from there. | ✓ |
| Keep best candidate | Compare all attempts and keep the best result so far, even if the latest change regressed. | |
| No automatic rollback | Leave the changed state in place and just log the failure. | |

**User's choice:** Auto-revert to best
**Notes:** A degrading or breaking repair should not remain active.

---

## Rollback baseline

| Option | Description | Selected |
|--------|-------------|----------|
| Last fully passing state | Rollback to the most recent run that satisfied all success checks. | ✓ |
| Original Phase 4 state | Always return to the baseline produced before autonomous repair starts. | |
| Best MAPE only | Use the lowest-MAPE state even if other checks were weaker. | |

**User's choice:** Last fully passing state
**Notes:** Rollback should honor the full verification contract, not a single metric.

---

## Repair logging

| Option | Description | Selected |
|--------|-------------|----------|
| Per-attempt audit log | Every attempt gets before/after metrics, change summary, diagnosis, outcome, and rollback note if applicable. | |
| Final summary only | Only document the winning repair and final metrics. | |
| Hybrid | Keep a concise per-attempt log plus a stronger final summary section. | ✓ |

**User's choice:** Hybrid
**Notes:** The log should remain readable while preserving enough detail for auditability.

---

## Mandatory repair evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Before/after metrics | Include MAPE, RMSE, and pass/fail status before and after the change. | ✓ |
| Change rationale | Why the agent believed this fix addressed the diagnosis. | ✓ |
| Files/settings changed | Exact files, config keys, or commands affected. | |
| Rollback outcome | Whether the fix stuck or was reverted. | |
| Run artifact links | Reference generated outputs such as model, plot, metrics, or logs. | |

**User's choice:** Before/after metrics, Change rationale
**Notes:** These are the mandatory minimums; other evidence can be added later at planner discretion.

---

## Stop conditions

| Option | Description | Selected |
|--------|-------------|----------|
| 3 consecutive passes | Matches the Phase 5 notes and proves the fix is stable, not lucky. | ✓ |
| 2 consecutive passes | Faster, but weaker confidence in stability. | |
| 1 passing run | Stop as soon as everything passes once. | |

**User's choice:** 3 consecutive passes
**Notes:** Stability is defined as repeated success, not a single passing run.

---

## Failure containment budget

| Option | Description | Selected |
|--------|-------------|----------|
| Bounded attempts + timeout | Stop after a fixed number of repair tries or elapsed time to avoid infinite churn. | ✓ |
| Attempts only | Stop after a fixed number of tries, regardless of time. | |
| No hard stop | Keep repairing indefinitely until success. | |

**User's choice:** Bounded attempts + timeout
**Notes:** Prevents runaway autonomous loops.

---

## Default repair budget

| Option | Description | Selected |
|--------|-------------|----------|
| 5 attempts / 30 min | Enough room for meaningful tuning without letting the loop run too long. | |
| 3 attempts / 15 min | Tighter budget, faster failure handoff. | |
| 10 attempts / 60 min | More exhaustive search, but much slower and riskier on CPU. | |
| 2 attempts / 10 min | User-provided custom budget. | ✓ |

**User's choice:** 2 attempts / 10 min
**Notes:** The user chose a stricter custom budget than the suggested defaults.

---

## the agent's Discretion

- Diagnosis heuristics and fix-ranking logic.
- Optional extra evidence in `REPAIR-LOG.md` beyond mandatory metrics and rationale.

## Deferred Ideas

None.

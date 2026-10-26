# Phase 2: Preprocessing & Sequence Generation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 02-preprocessing-sequence-generation
**Areas discussed:** Preprocessor contract, Verification output, Failure policy

---

## Preprocessor Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Tensors + scaler + metadata | Return train/test tensors, targets, fitted scaler, and lightweight metadata like split index/date range/window size. | ✓ |
| Tensors + scaler only | Keep the API minimal and closest to the TDD baseline. | |
| Also save artifacts to disk | Write processed arrays/scaler files during preprocessing. | |

**User's choice:** Tensors + scaler + metadata
**Notes:** Required metadata includes split boundary/date ranges, window details, and sequence counts/shapes.

---

## Verification Output

| Option | Description | Selected |
|--------|-------------|----------|
| Concise proof set | Print feature used, train/test shapes, date split boundary, scaled range check, and one first-sequence preview. | ✓ |
| Minimal output | Print only tensor shapes and a scaler-fit confirmation. | |
| Verbose diagnostics | Show richer previews and extra intermediate values. | |

**User's choice:** Concise proof set
**Notes:** Must include tensor shapes, split dates, one first normalized sequence preview with its target, and scaled-range confirmation.

---

## Failure Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Fail fast with clear errors | Raise descriptive errors for invalid input or unsafe preprocessing conditions. | ✓ |
| Warn and skip what it can | Continue after soft problems where possible. | |
| Auto-fix when possible | Silently coerce or patch issues. | |

**User's choice:** Fail fast with clear errors
**Notes:** Explicit errors are required for missing `Close` data, too few rows, invalid preprocessing config, and scaling/sequencing mismatches.

---

## the agent's Discretion

- Exact metadata container shape.
- Exact console formatting of the concise proof set.
- Exact wording of validation errors.

## Deferred Ideas

None.

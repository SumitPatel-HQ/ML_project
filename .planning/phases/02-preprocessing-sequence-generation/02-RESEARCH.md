# Phase 2 Research: Preprocessing & Sequence Generation

**Researched:** April 8, 2026  
**Focus:** Univariate stock-series preprocessing, leakage-safe scaling, chronological train/test splitting, sliding-window sequence generation, and CLI-visible proof output

---

## Discovery Level

**Level 1 — Quick Verification**

This phase stays inside the existing project stack (`pandas`, `numpy`, `scikit-learn`) and follows requirements already fixed in project docs. No new dependency selection is needed. Research focuses on confirming the safest implementation shape for:

- train-only `MinMaxScaler` fitting
- 80/20 chronological split with no shuffling
- 60-step sliding-window sequence creation
- test continuity using the final training window
- concise proof output that makes leakage prevention inspectable

---

## Standard Stack

- **pandas** — dataframe input from Phase 1 loader
- **numpy** — sequence assembly and tensor reshaping
- **scikit-learn / MinMaxScaler** — `[0,1]` normalization fitted on training data only

**Why this stack stays correct for Phase 2:**
- It matches the locked project scope and existing docs
- It keeps preprocessing offline and deterministic
- It avoids hand-rolled scaling or sequence utilities

---

## Architecture Patterns

### 1. Single preprocessor module with explicit contract

Use `src/preprocessor.py` as the sole owner of preprocessing logic for this phase.

Recommended public API:

```python
def preprocess(df, cfg=None):
    ...
    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "scaler": scaler,
        "metadata": metadata,
    }
```

**Why:** Phase 2 context locks a richer return contract (D-01 to D-04). A structured return value is easier for Phase 3 training code and for CLI proof output in `main.py`.

### 2. Validate before transforming

Run explicit checks before scaling or windowing:

- `feature_col` exists
- no unresolved missing values in `Close`
- `0 < train_split < 1`
- `window_size >= 1`
- train side has at least `window_size + 1` rows
- test side has at least 1 row and continuity window can be built

**Why:** Context decisions D-10 to D-14 require fail-fast behavior with descriptive errors, not warnings or auto-fixes.

### 3. Split raw series before scaling

Correct order:

1. Extract raw `Close` values
2. Split raw series chronologically at 80/20
3. Fit scaler on `train_raw` only
4. Transform `train_raw`
5. Build `test_input = last_train_window + test_raw`
6. Transform `test_input` with the already-fitted scaler
7. Build sequences

**Why:** This is the core leakage-prevention pattern from requirements, SRS, and TDD.

### 4. Keep proof output separate from core transformation math

Implement proof/report formatting as a helper in `src/preprocessor.py`, then call it from `main.py`.

**Why:**
- preprocessing math stays reusable for Phase 3
- CLI formatting can evolve without risking tensor logic
- tests can verify the proof set independently

---

## Required Metadata Contract

`metadata` must include at least these fields:

```python
{
    "feature_name": "Close",
    "window_size": 60,
    "train_split": 0.8,
    "split_index": int,
    "train_date_range": ("YYYY-MM-DD", "YYYY-MM-DD"),
    "test_date_range": ("YYYY-MM-DD", "YYYY-MM-DD"),
    "train_sequence_count": int,
    "test_sequence_count": int,
    "X_train_shape": tuple,
    "y_train_shape": tuple,
    "X_test_shape": tuple,
    "y_test_shape": tuple,
    "train_scaled_min": float,
    "train_scaled_max": float,
    "test_scaled_min": float,
    "test_scaled_max": float,
    "first_sequence_preview": list,
    "first_sequence_target": float,
}
```

This directly supports D-02, D-03, D-04, D-06, D-07, D-08, and D-09.

---

## Implementation Guidelines

### Leakage-safe scaling

Use:

```python
scaler = MinMaxScaler(feature_range=(0, 1))
train_scaled = scaler.fit_transform(train_raw)
test_scaled = scaler.transform(test_input)
```

**Never do:**

```python
scaler.fit_transform(full_series)
```

### Sliding-window helper

Preferred helper shape:

```python
def _create_sequences(data: np.ndarray, window_size: int) -> tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for i in range(window_size, len(data)):
        X.append(data[i - window_size:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)
```

Then reshape with:

```python
X_train = X_train.reshape(-1, window_size, 1)
X_test = X_test.reshape(-1, window_size, 1)
```

### Proof output contents

The proof set should print exactly these categories:

1. tensor shapes for `X_train`, `y_train`, `X_test`, `y_test`
2. train/test date ranges or split boundary
3. feature name and window size
4. scaler range confirmation showing values in or compatible with `[0,1]`
5. first normalized sequence preview plus target

Keep it concise: one block, no verbose dumps.

---

## Common Pitfalls

### 1. Fitting scaler on full data

This leaks future information into the train distribution and invalidates the experiment.

### 2. Creating test windows from test rows only

If test sequences start only inside the test partition, the first test predictions lose the last 60 training days of context. Use the final train window for continuity.

### 3. Using silent coercion for bad configuration

Do not auto-clamp `train_split`, auto-reduce `window_size`, or silently drop NaNs. Raise explicit errors per D-10 to D-14.

### 4. Returning raw arrays without metadata

That would satisfy tensor creation but fail the user’s proof and downstream verification needs.

### 5. Printing full sequences

Dumping all values makes output noisy. Print only a first-sequence preview plus the paired target.

---

## Don’t Hand-Roll

- **Scaling** — use `sklearn.preprocessing.MinMaxScaler`
- **Datetime slicing/ranges** — use pandas index operations
- **Array reshaping** — use NumPy reshape, not nested manual loops for tensor shape conversion

---

## Validation Architecture

After implementation, verify Phase 2 with automated checks that prove:

1. `preprocess(...)` returns `X_train`, `y_train`, `X_test`, `y_test`, `scaler`, and `metadata`
2. `X_train.shape[1:] == (60, 1)` and `X_test.shape[1:] == (60, 1)`
3. scaler was fitted on training data only
4. split is chronological and unshuffled
5. first test sequence uses the final train window for continuity
6. proof output includes shapes, split/date ranges, normalized preview, and target
7. invalid input cases raise descriptive `ValueError`s

Recommended automated coverage:

- `pytest tests/test_preprocessor.py -x`
- `pytest tests/test_main_phase2.py -x`

---

## Research Summary

**Recommended implementation approach:**

1. Build and test `src/preprocessor.py` first
2. Return a structured preprocessing bundle with required metadata
3. Add a dedicated proof formatter helper
4. Wire that helper into `main.py` after Phase 1 loading
5. Prefer focused tests over ad hoc manual inspection

**Confidence level:** HIGH — requirements and docs are aligned, and the preprocessing patterns are standard for offline LSTM time-series pipelines.

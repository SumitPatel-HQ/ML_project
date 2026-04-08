"""Autonomous Repair Controller - Standalone CLI for model optimization."""

import os
import sys
from pathlib import Path

from src.config import (
    AUTONOMOUS_FAILURE_ENV,
    OUTPUT_DIR,
    METRICS_FILE,
    MODEL_FILE,
    PREDICTION_PLOT_FILE,
)
from src.autonomous_verifier import (
    build_autonomous_verification_report,
    diagnose_verification_failure,
)
from src.repair_loop import (
    format_repair_outcome,
    run_autonomous_repair_loop,
    run_pipeline_subprocess,
)


class RepairState:
    """State tracker to pass hyperparameter overrides between loop callbacks."""
    def __init__(self):
        self.current_overrides = {}


def _rerun_pipeline_for_repair(state: RepairState):
    """Rerun the pipeline skipping Phase 5 and forcing training with overrides."""
    child_env = {
        **os.environ,
        "LSTM_SKIP_PHASE5": "1",
        "LSTM_REUSE_MODEL": "0",
        **state.current_overrides,
    }
    return run_pipeline_subprocess([sys.executable, "main.py"], env=child_env)


def _verify_repair_run(run_result):
    """Callback to verify a repair rerun with artifact path injection."""
    # Inject default paths so build_autonomous_verification_report can find artifacts
    run_result["metrics_path"] = os.path.join(OUTPUT_DIR, METRICS_FILE)
    run_result["checkpoint_path"] = os.path.join(OUTPUT_DIR, MODEL_FILE)
    run_result["prediction_plot_path"] = os.path.join(OUTPUT_DIR, PREDICTION_PLOT_FILE)
    return build_autonomous_verification_report(run_result)


def _apply_autonomous_repair(diagnosis, report, attempt_number, state: RepairState):
    """
    Apply a repair strategy based on the failure diagnosis.
    Injects hyperparameter overrides into the state for the next rerun.
    """
    env_overrides = {}

    if attempt_number == 1:
        # Strategy 1: Increase training capacity
        env_overrides["LSTM_EPOCHS"] = "150"
        rationale = "Increasing EPOCHS from 100 to 150 to allow for deeper convergence."
    elif attempt_number == 2:
        # Strategy 2: Refine learning rate
        env_overrides["LSTM_LEARNING_RATE"] = "0.0005"
        rationale = "Reducing LEARNING_RATE from 0.001 to 0.0005 for finer weight updates."
    else:
        # Strategy 3: Experimental - increase historical lookback
        env_overrides["LSTM_SEQUENCE_LENGTH"] = "90"
        rationale = "Extended SEQUENCE_LENGTH to 90 days to capture longer temporal trends."

    state.current_overrides = env_overrides
    return {
        "name": f"attempt-{attempt_number}-{diagnosis['category']}",
        "rationale": rationale,
        "env_overrides": env_overrides,
        "changed_files": [],
    }


def main():
    """Execute the standalone repair cycle."""
    print("\n" + "=" * 70)
    print(" " * 15 + "AUTONOMOUS REPAIR CONTROLLER")
    print("=" * 70 + "\n")

    metrics_path = os.path.join(OUTPUT_DIR, METRICS_FILE)
    if not os.path.exists(metrics_path):
        print(f"Error: No metrics found at {metrics_path}. Please run main.py first.")
        return

    # Initialize shared state
    state = RepairState()

    # Build initial report from existing artifacts
    initial_run_result = {
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0.0,
        "metrics_path": metrics_path,
        "checkpoint_path": os.path.join(OUTPUT_DIR, MODEL_FILE),
        "prediction_plot_path": os.path.join(OUTPUT_DIR, PREDICTION_PLOT_FILE),
        "failure_injection": os.getenv(AUTONOMOUS_FAILURE_ENV, ""),
    }
    initial_report = build_autonomous_verification_report(initial_run_result)

    if initial_report["passed"]:
        print("Model is already meeting all performance targets. Nothing to repair!")
        print(f"Current metrics: RMSE={initial_report['metrics']['rmse']:.4f}, MAPE={initial_report['metrics']['mape']:.4f}")
        return

    print(f"Target mismatch detected: RMSE={initial_report['metrics']['rmse']:.4f} (Target < 5.0)")
    print("Starting autonomous repair loop...\n")

    repair_result = run_autonomous_repair_loop(
        initial_report=initial_report,
        rerun_pipeline=lambda: _rerun_pipeline_for_repair(state),
        verify_run=_verify_repair_run,
        diagnose_failure=diagnose_verification_failure,
        apply_repair=lambda diag, rep, att: _apply_autonomous_repair(diag, rep, att, state),
    )

    print("\n" + "=" * 70)
    print("REPAIR COMPLETE")
    print("=" * 70)
    print(f"Final Status: {repair_result['status']}")
    print(f"Repair log: {REPAIR_LOG_FILE}")
    print(format_repair_outcome(repair_result))
    print()


if __name__ == "__main__":
    main()

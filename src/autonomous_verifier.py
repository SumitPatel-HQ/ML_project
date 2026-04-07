"""Lightweight Phase 5 verification helpers for autonomous repair cycles."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import (
    AUTONOMOUS_ALLOWED_REPAIR_SCOPE,
    AUTONOMOUS_REQUIRED_ARTIFACTS,
    MAPE_TARGET,
    METRICS_FILE,
    MODEL_FILE,
    OUTPUT_DIR,
    PREDICTION_PLOT_FILE,
    RMSE_TARGET,
)


def _build_config(cfg=None):
    overrides = cfg or {}
    return {
        "output_dir": overrides.get("output_dir", OUTPUT_DIR),
        "metrics_file": overrides.get("metrics_file", METRICS_FILE),
        "model_file": overrides.get("model_file", MODEL_FILE),
        "prediction_plot_file": overrides.get(
            "prediction_plot_file", PREDICTION_PLOT_FILE
        ),
        "rmse_target": float(overrides.get("rmse_target", RMSE_TARGET)),
        "mape_target": float(overrides.get("mape_target", MAPE_TARGET)),
        "required_artifacts": tuple(
            overrides.get("required_artifacts", AUTONOMOUS_REQUIRED_ARTIFACTS)
        ),
        "allowed_repair_scope": list(
            overrides.get("allowed_repair_scope", AUTONOMOUS_ALLOWED_REPAIR_SCOPE)
        ),
    }


def _normalize_display_path(path_value):
    path = Path(path_value)
    if not path.is_absolute():
        return path.as_posix()

    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_metrics(metrics_path):
    path = Path(metrics_path)
    if not path.exists():
        return None

    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_paths(run_result, config):
    return {
        config["model_file"]: run_result["checkpoint_path"],
        config["metrics_file"]: run_result["metrics_path"],
        config["prediction_plot_file"]: run_result["prediction_plot_path"],
    }


def _missing_artifacts(artifact_paths):
    missing = []
    for artifact_name, artifact_path in artifact_paths.items():
        if not Path(artifact_path).exists():
            missing.append(_normalize_display_path(artifact_path))
    return missing


def build_autonomous_verification_report(run_result, cfg=None):
    """Build a structured verification report from process output and artifacts.

    Args:
        run_result: Mapping with process result fields and artifact paths.
        cfg: Optional configuration overrides.

    Returns:
        Dict containing metrics, artifact checks, and overall pass/fail state.
    """

    config = _build_config(cfg)
    metrics_payload = _load_metrics(run_result["metrics_path"])
    artifact_paths = _artifact_paths(run_result, config)
    missing_artifacts = _missing_artifacts(artifact_paths)

    metrics = {
        "rmse": None if metrics_payload is None else metrics_payload.get("rmse"),
        "mape": None if metrics_payload is None else metrics_payload.get("mape"),
    }
    thresholds = {
        "rmse_target": config["rmse_target"],
        "mape_target": config["mape_target"],
    }
    passes = {
        "rmse_pass": bool(metrics_payload and metrics_payload.get("rmse_pass") is True),
        "mape_pass": bool(metrics_payload and metrics_payload.get("mape_pass") is True),
    }

    injected_failure = run_result.get("failure_injection") in {"metrics", "runtime"}
    runtime_ok = run_result["exit_code"] == 0
    artifacts_ok = not missing_artifacts
    metrics_ok = passes["rmse_pass"] and passes["mape_pass"]

    return {
        "passed": runtime_ok and artifacts_ok and metrics_ok and not injected_failure,
        "exit_code": run_result["exit_code"],
        "stdout": run_result.get("stdout", ""),
        "stderr": run_result.get("stderr", ""),
        "duration_seconds": run_result.get("duration_seconds"),
        "failure_injection": run_result.get("failure_injection"),
        "metrics": metrics,
        "thresholds": thresholds,
        "passes": passes,
        "metrics_path": _normalize_display_path(run_result["metrics_path"]),
        "checkpoint_path": _normalize_display_path(run_result["checkpoint_path"]),
        "prediction_plot_path": _normalize_display_path(
            run_result["prediction_plot_path"]
        ),
        "missing_artifacts": missing_artifacts,
        "artifact_paths": {
            name: _normalize_display_path(path) for name, path in artifact_paths.items()
        },
        "locked_scope": list(config["allowed_repair_scope"]),
    }


def diagnose_verification_failure(report, cfg=None):
    """Classify verification failures and suggest bounded repair targets.

    Args:
        report: Output from build_autonomous_verification_report.
        cfg: Optional configuration overrides.

    Returns:
        Dict with failure category, ranked hints, and allowed repair boundaries.
    """

    config = _build_config(cfg)
    locked_scope = list(config["allowed_repair_scope"])
    locked_scope_clause = ", ".join(locked_scope)

    if report["failure_injection"] in {"metrics", "runtime"}:
        category = "injected_failure"
        target_surfaces = ["main.py", "src/autonomous_verifier.py"]
        hints = [
            "Confirm the deterministic failure injection path is wired intentionally in main.py while keeping offline-only, AAPL-only, Close-only, stacked-LSTM boundaries unchanged.",
            "Clear the forced failure flag after the test cycle and rerun verification without expanding beyond offline-only, AAPL-only, Close-only, stacked-LSTM constraints.",
        ]
    elif report["missing_artifacts"]:
        category = "artifact_missing"
        target_surfaces = ["main.py", "src/evaluator.py", "src/visualizer.py"]
        hints = [
            f"Regenerate the missing artifacts {report['missing_artifacts']} through the normal offline-only, AAPL-only, Close-only, stacked-LSTM pipeline path.",
            "Inspect plotting and metrics-writing steps in src/evaluator.py or src/visualizer.py without changing the offline-only, AAPL-only, Close-only, stacked-LSTM baseline.",
        ]
    elif report["exit_code"] != 0:
        stderr = str(report.get("stderr", "")).lower()
        stdout = str(report.get("stdout", "")).lower()
        if (
            "no module named" in stderr
            or "python 3.14" in stderr
            or "python 3.14" in stdout
        ):
            category = "environment_blocker"
            target_surfaces = ["requirements.txt", "README.md", "environment setup"]
            hints = [
                "Provision a TensorFlow-supported Python environment, then rerun the same offline-only, AAPL-only, Close-only, stacked-LSTM workflow.",
                "Treat this as an environment blocker before broad code edits; repairs may be broad later, but the offline-only, AAPL-only, Close-only, stacked-LSTM contract stays locked.",
            ]
        else:
            category = "runtime_failure"
            target_surfaces = ["main.py", "src/trainer.py", "src/evaluator.py"]
            hints = [
                "Inspect stderr and the failing pipeline stage, then fix the runtime issue while preserving the offline-only, AAPL-only, Close-only, stacked-LSTM contract.",
                "Broad code edits are allowed for repair, but keep the locked scope unchanged: offline-only, AAPL-only, Close-only, stacked-LSTM.",
            ]
    elif not (report["passes"]["rmse_pass"] and report["passes"]["mape_pass"]):
        category = "metric_regression"
        target_surfaces = ["src/config.py", "src/trainer.py", "src/evaluator.py"]
        hints = [
            f"Tune hyperparameters in src/config.py and retrain, but stay within the locked repair scope: {locked_scope_clause}.",
            f"Inspect training dynamics in src/trainer.py and evaluation assumptions in src/evaluator.py; broad code edits are allowed, yet the project must remain {locked_scope_clause}.",
        ]
    else:
        category = "runtime_failure"
        target_surfaces = ["main.py", "src/autonomous_verifier.py"]
        hints = [
            "Review the verification handshake and rerun the pipeline while preserving offline-only, AAPL-only, Close-only, stacked-LSTM boundaries.",
        ]

    return {
        "category": category,
        "locked_scope": locked_scope,
        "target_surfaces": target_surfaces,
        "hints": hints,
    }


def format_autonomous_verification_summary(report):
    """Format a concise autonomous verification summary for CLI output."""

    return "\n".join(
        [
            f"Autonomous verification passed: {report['passed']}",
            f"Exit code: {report['exit_code']}",
            f"RMSE: {report['metrics']['rmse']} (target < {report['thresholds']['rmse_target']}) [{report['passes']['rmse_pass']}]",
            f"MAPE: {report['metrics']['mape']} (target < {report['thresholds']['mape_target']}) [{report['passes']['mape_pass']}]",
            f"Missing artifacts: {', '.join(report['missing_artifacts']) or 'none'}",
        ]
    )

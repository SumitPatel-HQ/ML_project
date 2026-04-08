"""Autonomous repair controller and repair-log helpers for Phase 5."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from src.config import (
    AUTONOMOUS_MAX_REPAIR_ATTEMPTS,
    AUTONOMOUS_MAX_REPAIR_MINUTES,
    AUTONOMOUS_PASS_STREAK,
    REPAIR_LOG_FILE,
)


def _build_config(cfg=None):
    overrides = cfg or {}
    return {
        "pass_streak": int(overrides.get("pass_streak", AUTONOMOUS_PASS_STREAK)),
        "max_attempts": int(
            overrides.get("max_attempts", AUTONOMOUS_MAX_REPAIR_ATTEMPTS)
        ),
        "max_minutes": float(
            overrides.get("max_minutes", AUTONOMOUS_MAX_REPAIR_MINUTES)
        ),
        "repair_log_file": overrides.get("repair_log_file", REPAIR_LOG_FILE),
    }


def _normalize_path(path_value):
    path = Path(path_value)
    if not path.is_absolute():
        return path.as_posix()

    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _snapshot_files(changed_files):
    snapshots = {}
    for file_path in changed_files:
        path = Path(file_path)
        snapshots[path] = path.read_bytes() if path.exists() else None
        normalized_path = Path(_normalize_path(path))
        snapshots[normalized_path] = snapshots[path]
    return snapshots


def _restore_snapshots(snapshots):
    for path, content in snapshots.items():
        if content is None:
            if path.exists():
                path.unlink()
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def _report_is_worse(candidate_report, baseline_report):
    if baseline_report is None:
        return candidate_report["passed"] is False or candidate_report["exit_code"] != 0

    if candidate_report["exit_code"] != 0:
        return True
    if candidate_report["passed"] is False and baseline_report["passed"] is True:
        return True

    baseline_metrics = baseline_report.get("metrics", {})
    candidate_metrics = candidate_report.get("metrics", {})
    if baseline_metrics.get("rmse") is None or candidate_metrics.get("rmse") is None:
        return False

    return (candidate_metrics["rmse"] > baseline_metrics["rmse"]) or (
        candidate_metrics["mape"] > baseline_metrics["mape"]
    )


def _format_metrics(report):
    metrics = report.get("metrics", {})
    return f"RMSE={metrics.get('rmse')}, MAPE={metrics.get('mape')}"


def run_pipeline_subprocess(command, env=None, cwd=None, timeout=None):
    """Run the pipeline in a child process and return normalized process results."""

    started = time.time()
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=timeout,
        check=False,
    )
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "duration_seconds": round(time.time() - started, 6),
    }


def write_repair_log(log_path, attempts, final_summary):
    """Persist hybrid repair-loop evidence as markdown."""

    path = Path(log_path)
    lines = ["# Autonomous Repair Log", ""]

    for index, attempt in enumerate(attempts, start=1):
        lines.extend(
            [
                f"## Attempt {index}",
                f"Diagnosis: {attempt['diagnosis_category']}",
                f"Rationale: {attempt['rationale']}",
                f"Changed files: {', '.join(attempt['changed_files']) or 'none'}",
                f"Before metrics: {_format_metrics(attempt['before_report'])}",
                f"After metrics: {_format_metrics(attempt['after_report'])}",
                f"Rolled back: {attempt['rolled_back']}",
            ]
        )
        if attempt["rolled_back"]:
            lines.append(f"Rollback reason: {attempt['rollback_reason']}")
        lines.append("")

    lines.extend(
        [
            "## Final Outcome",
            f"Status: {final_summary['status']}",
            f"Consecutive passes: {final_summary['consecutive_passes']}",
            f"Repair attempts: {final_summary['repair_attempts']}",
            f"Stop reason: {final_summary['stop_reason']}",
            f"Final metrics: {_format_metrics(final_summary['final_report'])}",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path.as_posix()


def run_autonomous_repair_loop(
    initial_report,
    rerun_pipeline,
    verify_run,
    diagnose_failure,
    apply_repair,
    cfg=None,
    now_fn=None,
):
    """Retry failed runs, revert bad repairs, and capture repair evidence."""

    config = _build_config(cfg)
    now = now_fn or time.time
    log_path = config["repair_log_file"]
    attempts = []
    start_time = now()
    current_report = initial_report
    final_diagnosis = None
    baseline_report = initial_report if initial_report["passed"] else None
    consecutive_passes = 1 if initial_report["passed"] else 0
    repair_attempts = 0
    stop_reason = (
        "pass_streak_reached"
        if consecutive_passes >= config["pass_streak"]
        else "in_progress"
    )

    while True:
        if current_report["passed"]:
            if current_report["passed"] and baseline_report is None:
                baseline_report = current_report
            if consecutive_passes >= config["pass_streak"]:
                status = "passed"
                break
            run_result = rerun_pipeline()
            current_report = verify_run(run_result)
            consecutive_passes = (
                consecutive_passes + 1 if current_report["passed"] else 0
            )
            if current_report["passed"]:
                baseline_report = current_report
                stop_reason = "pass_streak_reached"
                continue

        elapsed_minutes = (now() - start_time) / 60.0
        if elapsed_minutes > config["max_minutes"]:
            status = "unresolved"
            stop_reason = "time_budget_exceeded"
            break
        if repair_attempts >= config["max_attempts"]:
            status = "unresolved"
            stop_reason = "attempt_budget_exceeded"
            break

        final_diagnosis = diagnose_failure(current_report)
        pre_repair_snapshots = _snapshot_files(
            final_diagnosis.get("target_surfaces", [])
        )
        repair_attempts += 1
        repair_action = apply_repair(final_diagnosis, current_report, repair_attempts)
        changed_files = [
            _normalize_path(path) for path in repair_action.get("changed_files", [])
        ]
        snapshots = {}
        for path in repair_action.get("changed_files", []):
            candidate_path = Path(path)
            snapshots[candidate_path] = pre_repair_snapshots.get(
                candidate_path,
                pre_repair_snapshots.get(Path(_normalize_path(candidate_path))),
            )
        before_report = current_report

        run_result = rerun_pipeline()
        current_report = verify_run(run_result)
        consecutive_passes = 1 if current_report["passed"] else 0
        comparison_report = baseline_report or before_report
        rolled_back = bool(changed_files) and _report_is_worse(
            current_report, comparison_report
        )
        rollback_reason = None
        if rolled_back:
            _restore_snapshots(snapshots)
            rollback_reason = "degraded_from_baseline"
            if baseline_report is not None:
                current_report = baseline_report
                consecutive_passes = 1

        attempts.append(
            {
                "attempt_number": repair_attempts,
                "name": repair_action["name"],
                "diagnosis_category": final_diagnosis["category"],
                "rationale": repair_action["rationale"],
                "changed_files": changed_files,
                "before_report": before_report,
                "after_report": current_report
                if rolled_back and baseline_report is not None
                else verify_run(run_result)
                if False
                else current_report,
                "rolled_back": rolled_back,
                "rollback_reason": rollback_reason,
            }
        )

        if rolled_back and baseline_report is None:
            status = "unresolved"
            stop_reason = rollback_reason
            break

    final_summary = {
        "status": status,
        "consecutive_passes": consecutive_passes,
        "repair_attempts": repair_attempts,
        "stop_reason": stop_reason,
        "final_report": current_report,
    }
    write_repair_log(log_path, attempts, final_summary)
    return {
        "status": status,
        "consecutive_passes": consecutive_passes,
        "repair_attempts": repair_attempts,
        "repair_log_path": log_path,
        "final_report": current_report,
        "final_diagnosis": final_diagnosis,
        "attempts": attempts,
        "stop_reason": stop_reason,
    }


def format_repair_outcome(result):
    """Format a concise repair outcome summary for CLI output."""

    final_report = result["final_report"]
    return "\n".join(
        [
            f"Autonomous status: {result['status']}",
            f"Consecutive passes: {result['consecutive_passes']}",
            f"Repair attempts: {result['repair_attempts']}",
            f"Final RMSE: {final_report['metrics']['rmse']}",
            f"Final MAPE: {final_report['metrics']['mape']}",
        ]
    )

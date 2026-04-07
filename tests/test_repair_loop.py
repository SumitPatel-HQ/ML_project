import importlib
from pathlib import Path

import pytest


def _load_repair_loop_module():
    try:
        module = importlib.import_module("src.repair_loop")
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.repair_loop module not implemented: {exc}")

    missing = [
        name
        for name in (
            "run_autonomous_repair_loop",
            "run_pipeline_subprocess",
            "write_repair_log",
            "format_repair_outcome",
        )
        if not hasattr(module, name)
    ]
    if missing:
        pytest.fail(f"src.repair_loop missing public API: {missing}")

    return importlib.reload(module)


def _report(*, passed, rmse=3.0, mape=2.0, exit_code=0, category="metric_regression"):
    return {
        "passed": passed,
        "exit_code": exit_code,
        "duration_seconds": 1.0,
        "failure_injection": "",
        "metrics": {"rmse": rmse, "mape": mape},
        "thresholds": {"rmse_target": 5.0, "mape_target": 5.0},
        "passes": {"rmse_pass": rmse < 5.0, "mape_pass": mape < 5.0},
        "metrics_path": "output/metrics.json",
        "checkpoint_path": "output/best_model.h5",
        "prediction_plot_path": "output/AAPL_prediction.png",
        "missing_artifacts": [],
        "artifact_paths": {},
        "locked_scope": ["offline-only", "AAPL-only", "Close-only", "stacked-LSTM"],
        "diagnosis_category": category,
    }


def test_run_autonomous_repair_loop_requires_three_consecutive_passes(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    repair_loop = _load_repair_loop_module()
    reports = [
        _report(passed=False, rmse=6.2, mape=5.8),
        _report(passed=True, rmse=4.0, mape=3.9),
        _report(passed=True, rmse=3.8, mape=3.4),
        _report(passed=True, rmse=3.6, mape=3.1),
    ]
    rerun_calls = []
    repair_calls = []
    diagnosis_calls = []

    def rerun_pipeline():
        rerun_calls.append("rerun")
        return {"attempt": len(rerun_calls)}

    def verify_run(_run_result):
        return reports.pop(0)

    def diagnose_failure(report):
        diagnosis_calls.append(report)
        return {
            "category": "metric_regression",
            "hints": ["Tune src/config.py while preserving locked scope."],
            "target_surfaces": ["src/config.py"],
            "locked_scope": report["locked_scope"],
        }

    def apply_repair(diagnosis, report, attempt_number):
        repair_calls.append((diagnosis, report, attempt_number))
        return {
            "name": "attempt-1-lower-learning-rate",
            "rationale": "Reduce overshoot after metric regression.",
            "changed_files": [],
        }

    result = repair_loop.run_autonomous_repair_loop(
        initial_report=reports.pop(0),
        rerun_pipeline=rerun_pipeline,
        verify_run=verify_run,
        diagnose_failure=diagnose_failure,
        apply_repair=apply_repair,
    )

    assert result["status"] == "passed"
    assert result["consecutive_passes"] == 3
    assert result["repair_attempts"] == 1
    assert len(rerun_calls) == 3
    assert len(diagnosis_calls) == 1
    assert repair_calls[0][2] == 1


def test_run_autonomous_repair_loop_stops_after_attempt_or_time_budget(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    repair_loop = _load_repair_loop_module()
    rerun_calls = []
    repair_calls = []
    now_values = iter([0, 60, 120, 721, 722])

    def rerun_pipeline():
        rerun_calls.append("rerun")
        return {"attempt": len(rerun_calls)}

    def verify_run(_run_result):
        return _report(passed=False, rmse=6.5, mape=5.5, category="runtime_failure")

    def diagnose_failure(_report_value):
        return {
            "category": "runtime_failure",
            "hints": ["Inspect stderr before broad edits."],
            "target_surfaces": ["main.py"],
            "locked_scope": ["offline-only", "AAPL-only", "Close-only", "stacked-LSTM"],
        }

    def apply_repair(_diagnosis, _report_value, attempt_number):
        repair_calls.append(attempt_number)
        return {
            "name": f"attempt-{attempt_number}-fix-runtime",
            "rationale": "Address runtime failure.",
            "changed_files": [],
        }

    result = repair_loop.run_autonomous_repair_loop(
        initial_report=_report(
            passed=False, rmse=7.0, mape=6.0, category="runtime_failure"
        ),
        rerun_pipeline=rerun_pipeline,
        verify_run=verify_run,
        diagnose_failure=diagnose_failure,
        apply_repair=apply_repair,
        now_fn=lambda: next(now_values),
    )

    assert result["status"] == "unresolved"
    assert result["repair_attempts"] == 2
    assert repair_calls == [1, 2]
    assert len(rerun_calls) == 2
    assert result["stop_reason"] == "time_budget_exceeded"


def test_run_autonomous_repair_loop_restores_changed_files_when_repair_degrades_baseline(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    repair_loop = _load_repair_loop_module()
    protected_file = tmp_path / "src" / "config.py"
    protected_file.parent.mkdir(parents=True, exist_ok=True)
    protected_file.write_text("learning_rate = 0.001\n", encoding="utf-8")
    rerun_calls = []
    current_report = {
        "value": _report(passed=True, rmse=4.0, mape=3.0),
    }

    def rerun_pipeline():
        rerun_calls.append("rerun")
        return {"attempt": len(rerun_calls)}

    def verify_run(_run_result):
        return current_report["value"]

    def diagnose_failure(_report_value):
        return {
            "category": "metric_regression",
            "hints": ["Tune config."],
            "target_surfaces": ["src/config.py"],
            "locked_scope": ["offline-only", "AAPL-only", "Close-only", "stacked-LSTM"],
        }

    def apply_repair(_diagnosis, _report_value, attempt_number):
        protected_file.write_text("learning_rate = 0.01\n", encoding="utf-8")
        current_report["value"] = _report(passed=False, rmse=8.5, mape=7.1)
        return {
            "name": f"attempt-{attempt_number}-raise-learning-rate",
            "rationale": "Try a more aggressive optimizer step.",
            "changed_files": [protected_file.as_posix()],
        }

    result = repair_loop.run_autonomous_repair_loop(
        initial_report=_report(passed=False, rmse=6.0, mape=5.2),
        rerun_pipeline=rerun_pipeline,
        verify_run=verify_run,
        diagnose_failure=diagnose_failure,
        apply_repair=apply_repair,
    )

    assert result["status"] == "unresolved"
    assert protected_file.read_text(encoding="utf-8") == "learning_rate = 0.001\n"
    assert result["attempts"][0]["rolled_back"] is True
    assert result["attempts"][0]["rollback_reason"] == "degraded_from_baseline"


def test_run_autonomous_repair_loop_writes_repair_log_with_attempt_entries_and_final_summary(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    repair_loop = _load_repair_loop_module()
    reports = [
        _report(passed=False, rmse=6.4, mape=5.9),
        _report(passed=False, rmse=4.8, mape=4.2),
        _report(passed=True, rmse=4.4, mape=3.9),
        _report(passed=True, rmse=4.2, mape=3.7),
        _report(passed=True, rmse=4.1, mape=3.5),
    ]
    workspace_file = tmp_path / "src" / "config.py"
    workspace_file.parent.mkdir(parents=True, exist_ok=True)
    workspace_file.write_text("learning_rate = 0.001\n", encoding="utf-8")

    def rerun_pipeline():
        return {"ok": True}

    def verify_run(_run_result):
        return reports.pop(0)

    def diagnose_failure(report):
        return {
            "category": report["diagnosis_category"],
            "hints": ["Adjust learning rate."],
            "target_surfaces": ["src/config.py"],
            "locked_scope": report["locked_scope"],
        }

    def apply_repair(_diagnosis, _report_value, attempt_number):
        workspace_file.write_text(
            f"learning_rate = 0.000{attempt_number}\n", encoding="utf-8"
        )
        return {
            "name": f"attempt-{attempt_number}-lower-learning-rate",
            "rationale": "Reduce overshoot after metric regression.",
            "changed_files": [workspace_file.as_posix()],
        }

    result = repair_loop.run_autonomous_repair_loop(
        initial_report=reports.pop(0),
        rerun_pipeline=rerun_pipeline,
        verify_run=verify_run,
        diagnose_failure=diagnose_failure,
        apply_repair=apply_repair,
    )

    log_path = Path(result["repair_log_path"])
    assert log_path.as_posix() == "REPAIR-LOG.md"
    log_text = log_path.read_text(encoding="utf-8")
    assert "## Attempt 1" in log_text
    assert "Diagnosis: metric_regression" in log_text
    assert "Rationale: Reduce overshoot after metric regression." in log_text
    assert "Changed files: src/config.py" in log_text
    assert "Before metrics: RMSE=6.4, MAPE=5.9" in log_text
    assert "After metrics: RMSE=4.8, MAPE=4.2" in log_text
    assert "## Final Outcome" in log_text
    assert "Status: passed" in log_text
    assert "Consecutive passes: 3" in log_text

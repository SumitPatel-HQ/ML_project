import importlib
import json
from pathlib import Path

import pytest


ALLOWED_CATEGORIES = {
    "metric_regression",
    "runtime_failure",
    "artifact_missing",
    "environment_blocker",
    "injected_failure",
}


def _load_autonomous_verifier_module():
    try:
        module = importlib.import_module("src.autonomous_verifier")
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.autonomous_verifier module not implemented: {exc}")

    missing = [
        name
        for name in (
            "build_autonomous_verification_report",
            "diagnose_verification_failure",
            "format_autonomous_verification_summary",
        )
        if not hasattr(module, name)
    ]
    if missing:
        pytest.fail(f"src.autonomous_verifier missing public API: {missing}")

    return importlib.reload(module)


def _write_artifacts(tmp_path, metrics_payload=None):
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(
            metrics_payload
            or {
                "rmse": 3.25,
                "mape": 2.4,
                "rmse_target": 5.0,
                "mape_target": 5.0,
                "rmse_pass": True,
                "mape_pass": True,
                "checkpoint_path": "output/best_model.h5",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    checkpoint_path = output_dir / "best_model.h5"
    checkpoint_path.write_text("fake checkpoint", encoding="utf-8")

    prediction_plot_path = output_dir / "AAPL_prediction.png"
    prediction_plot_path.write_text("fake plot", encoding="utf-8")

    return {
        "metrics_path": metrics_path.as_posix(),
        "checkpoint_path": checkpoint_path.as_posix(),
        "prediction_plot_path": prediction_plot_path.as_posix(),
    }


def _build_run_result(tmp_path, **overrides):
    artifact_paths = _write_artifacts(tmp_path, overrides.pop("metrics_payload", None))
    run_result = {
        "exit_code": 0,
        "stdout": "pipeline complete",
        "stderr": "",
        "duration_seconds": 32.5,
        "failure_injection": None,
        **artifact_paths,
    }
    run_result.update(overrides)
    return run_result


def test_build_autonomous_verification_report_marks_clean_run_as_pass(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    verifier_module = _load_autonomous_verifier_module()

    report = verifier_module.build_autonomous_verification_report(
        _build_run_result(tmp_path)
    )

    assert report["passed"] is True
    assert report["exit_code"] == 0
    assert report["duration_seconds"] == pytest.approx(32.5)
    assert report["metrics"] == {"rmse": 3.25, "mape": 2.4}
    assert report["thresholds"] == {"rmse_target": 5.0, "mape_target": 5.0}
    assert report["passes"] == {"rmse_pass": True, "mape_pass": True}
    assert report["missing_artifacts"] == []


@pytest.mark.parametrize("failure_injection", ["metrics", "runtime"])
def test_build_autonomous_verification_report_forces_failure_for_injected_regressions(
    monkeypatch, tmp_path, failure_injection
):
    monkeypatch.chdir(tmp_path)
    verifier_module = _load_autonomous_verifier_module()

    report = verifier_module.build_autonomous_verification_report(
        _build_run_result(tmp_path, failure_injection=failure_injection)
    )
    diagnosis = verifier_module.diagnose_verification_failure(report)

    assert report["passed"] is False
    assert report["failure_injection"] == failure_injection
    assert diagnosis["category"] == "injected_failure"
    assert diagnosis["category"] in ALLOWED_CATEGORIES


def test_build_autonomous_verification_report_diagnoses_runtime_failure_explicitly(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    verifier_module = _load_autonomous_verifier_module()

    report = verifier_module.build_autonomous_verification_report(
        _build_run_result(
            tmp_path,
            exit_code=1,
            stderr="TensorFlow is required to reload the saved Phase 3 model for Phase 4 evaluation.",
        )
    )
    diagnosis = verifier_module.diagnose_verification_failure(report)

    assert report["passed"] is False
    assert diagnosis["category"] == "runtime_failure"
    assert diagnosis["category"] in ALLOWED_CATEGORIES


def test_build_autonomous_verification_report_diagnoses_missing_artifacts_explicitly(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    verifier_module = _load_autonomous_verifier_module()
    run_result = _build_run_result(tmp_path)
    Path(run_result["prediction_plot_path"]).unlink()

    report = verifier_module.build_autonomous_verification_report(run_result)
    diagnosis = verifier_module.diagnose_verification_failure(report)

    assert report["passed"] is False
    assert report["missing_artifacts"] == ["output/AAPL_prediction.png"]
    assert diagnosis["category"] == "artifact_missing"
    assert diagnosis["category"] in ALLOWED_CATEGORIES


def test_diagnose_verification_failure_returns_metric_regression_and_locked_scope_hints(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    verifier_module = _load_autonomous_verifier_module()
    report = verifier_module.build_autonomous_verification_report(
        _build_run_result(
            tmp_path,
            metrics_payload={
                "rmse": 6.4,
                "mape": 5.6,
                "rmse_target": 5.0,
                "mape_target": 5.0,
                "rmse_pass": False,
                "mape_pass": False,
                "checkpoint_path": "output/best_model.h5",
            },
        )
    )

    diagnosis = verifier_module.diagnose_verification_failure(report)

    assert report["passed"] is False
    assert diagnosis["category"] == "metric_regression"
    assert diagnosis["category"] in ALLOWED_CATEGORIES
    assert diagnosis["locked_scope"] == [
        "offline-only",
        "AAPL-only",
        "Close-only",
        "stacked-LSTM",
    ]
    assert diagnosis["target_surfaces"] == [
        "src/config.py",
        "src/trainer.py",
        "src/evaluator.py",
    ]
    assert any("src/config.py" in hint for hint in diagnosis["hints"])
    forbidden_terms = ["live data", "MSFT", "Open price", "transformer"]
    for hint in diagnosis["hints"]:
        lowered = hint.lower()
        assert "offline-only" in lowered
        assert "aapl-only" in lowered
        assert "close-only" in lowered
        assert "stacked-lstm" in lowered
        assert not any(term.lower() in lowered for term in forbidden_terms)

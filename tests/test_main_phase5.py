import importlib

import pandas as pd
import pytest


def _load_main_module():
    try:
        return importlib.import_module("main")
    except ModuleNotFoundError as exc:
        pytest.fail(f"main.py not implemented: {exc}")


def test_main_prints_phase5_autonomous_summary_and_repair_log_path(monkeypatch, capsys):
    main_module = _load_main_module()
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2020-01-01", periods=3, freq="B"),
    )
    bundle = {
        "X_train": type("FakeTensor", (), {"shape": (16, 60, 1)})(),
        "X_test": ["fake-test-tensor"],
        "metadata": {
            "X_train_shape": (16, 60, 1),
            "X_test_shape": (4, 60, 1),
        },
    }
    training_result = {
        "model": object(),
        "checkpoint_path": "output/best_model.h5",
        "sidecar_path": "output/training_history.json",
        "metadata": {"best_epoch": 7},
    }
    evaluation_result = {
        "actual_usd": [105.0, 106.0],
        "predictions_usd": [104.5, 106.5],
        "metrics": {"rmse": 4.25, "mape": 3.75},
        "thresholds": {"rmse_target": 5.0, "mape_target": 5.0},
        "passes": {"rmse_pass": True, "mape_pass": True},
        "metrics_path": "output/metrics.json",
        "checkpoint_path": "output/best_model.h5",
    }
    generated_paths = {
        "prediction": "output/AAPL_prediction.png",
        "bands": "output/AAPL_prediction_with_bands.png",
        "residuals": "output/residuals.png",
        "candlestick": "output/candlestick.png",
        "heatmap": "output/correlation_heatmap.png",
    }
    calls = {}

    monkeypatch.setenv("LSTM_FORCE_AUTONOMOUS_FAILURE", "metrics")
    monkeypatch.delenv("LSTM_SKIP_PHASE5", raising=False)

    monkeypatch.setattr(main_module, "setup_environment", lambda: None)
    monkeypatch.setattr(main_module, "load_data", lambda path: df)
    monkeypatch.setattr(main_module, "display_statistics", lambda loaded_df: None)
    monkeypatch.setattr(main_module, "check_missing_values", lambda loaded_df: 0)
    monkeypatch.setattr(
        main_module, "plot_price_history", lambda loaded_df: "output/raw_price.png"
    )
    monkeypatch.setattr(main_module, "preprocess", lambda loaded_df: bundle)
    monkeypatch.setattr(
        main_module,
        "format_preprocessing_proof",
        lambda received_bundle: "X_train shape: (16, 60, 1)",
    )
    monkeypatch.setattr(main_module, "build_model", lambda input_shape: object())
    monkeypatch.setattr(main_module, "format_model_summary", lambda model: "LSTM")
    monkeypatch.setattr(
        main_module, "train_model", lambda model, received_bundle: training_result
    )
    monkeypatch.setattr(
        main_module,
        "format_training_summary",
        lambda received_bundle: "Model: output/best_model.h5",
    )
    monkeypatch.setattr(
        main_module,
        "evaluate_model",
        lambda received_training_result, received_bundle: evaluation_result,
    )
    monkeypatch.setattr(
        main_module,
        "reload_saved_model_smoke_test",
        lambda received_bundle, received_training_result: {"sample_count": 1},
    )
    monkeypatch.setattr(
        main_module,
        "format_evaluation_summary",
        lambda received_result: "RMSE: 4.250000\nMAPE: 3.750000%\nTargets hit",
    )
    monkeypatch.setattr(
        main_module,
        "plot_predictions",
        lambda actual_prices, predicted_prices, rmse, mape: generated_paths[
            "prediction"
        ],
    )
    monkeypatch.setattr(
        main_module,
        "plot_predictions_with_confidence_bands",
        lambda actual_prices, predicted_prices, rmse, mape: generated_paths["bands"],
    )
    monkeypatch.setattr(
        main_module,
        "plot_residuals",
        lambda actual_prices, predicted_prices: generated_paths["residuals"],
    )
    monkeypatch.setattr(
        main_module,
        "plot_candlestick_chart",
        lambda loaded_df: generated_paths["candlestick"],
    )
    monkeypatch.setattr(
        main_module,
        "plot_feature_correlation_heatmap",
        lambda loaded_df: generated_paths["heatmap"],
    )

    def fake_build_autonomous_verification_report(run_result, cfg=None):
        calls["verification_run_result"] = run_result
        return {
            "passed": False,
            "exit_code": run_result["exit_code"],
            "metrics": {"rmse": 4.25, "mape": 3.75},
            "thresholds": {"rmse_target": 5.0, "mape_target": 5.0},
            "passes": {"rmse_pass": True, "mape_pass": True},
            "missing_artifacts": [],
            "failure_injection": run_result["failure_injection"],
            "locked_scope": ["offline-only", "AAPL-only", "Close-only", "stacked-LSTM"],
        }

    def fake_run_pipeline_subprocess(command, env=None, cwd=None, timeout=None):
        calls["subprocess"] = {
            "command": command,
            "env": env,
            "cwd": cwd,
            "timeout": timeout,
        }
        return {
            "exit_code": 0,
            "stdout": "child run ok",
            "stderr": "",
            "duration_seconds": 1.0,
        }

    def fake_run_autonomous_repair_loop(
        initial_report,
        rerun_pipeline,
        verify_run,
        diagnose_failure,
        apply_repair,
        cfg=None,
        now_fn=None,
    ):
        calls["initial_report"] = initial_report
        child_run_result = rerun_pipeline()
        calls["child_run_result"] = child_run_result
        return {
            "status": "passed",
            "consecutive_passes": 3,
            "repair_attempts": 1,
            "repair_log_path": "REPAIR-LOG.md",
            "final_report": initial_report,
            "final_diagnosis": {"category": "injected_failure"},
        }

    monkeypatch.setattr(
        main_module,
        "build_autonomous_verification_report",
        fake_build_autonomous_verification_report,
    )
    monkeypatch.setattr(
        main_module,
        "format_autonomous_verification_summary",
        lambda report: "Autonomous verification passed: False\nExit code: 0",
    )
    monkeypatch.setattr(
        main_module,
        "diagnose_verification_failure",
        lambda report: {"category": "injected_failure"},
    )
    monkeypatch.setattr(
        main_module,
        "run_pipeline_subprocess",
        fake_run_pipeline_subprocess,
    )
    monkeypatch.setattr(
        main_module,
        "run_autonomous_repair_loop",
        fake_run_autonomous_repair_loop,
    )
    monkeypatch.setattr(
        main_module,
        "format_repair_outcome",
        lambda result: "Autonomous status: passed\nRepair attempts: 1",
    )

    main_module.main()

    output = capsys.readouterr().out
    assert "PHASE 5: Autonomous Correction & Performance Optimization Loop" in output
    assert "Autonomous status:" in output
    assert "Repair log: REPAIR-LOG.md" in output
    assert calls["verification_run_result"] == {
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0.0,
        "metrics_path": evaluation_result["metrics_path"],
        "checkpoint_path": training_result["checkpoint_path"],
        "prediction_plot_path": generated_paths["prediction"],
        "failure_injection": "metrics",
    }
    assert calls["subprocess"]["env"]["LSTM_SKIP_PHASE5"] == "1"
    assert calls["subprocess"]["command"][1] == "main.py"

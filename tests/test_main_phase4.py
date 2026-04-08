import importlib

import pandas as pd
import pytest


def _load_main_module():
    try:
        return importlib.import_module("main")
    except ModuleNotFoundError as exc:
        pytest.fail(f"main.py not implemented: {exc}")


def test_main_prints_phase4_evaluation_proof_and_artifact_paths(monkeypatch, capsys):
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
        "metrics": {"rmse": 6.25, "mape": 5.75},
        "thresholds": {"rmse_target": 5.0, "mape_target": 5.0},
        "passes": {"rmse_pass": False, "mape_pass": False},
        "metrics_path": "output/metrics.json",
        "checkpoint_path": "output/best_model.h5",
    }
    calls = {}
    generated_paths = {
        "prediction": "output/AAPL_prediction.png",
        "bands": "output/AAPL_prediction_with_bands.png",
        "residuals": "output/residuals.png",
        "candlestick": "output/candlestick.png",
        "heatmap": "output/correlation_heatmap.png",
    }

    monkeypatch.setenv("LSTM_SKIP_PHASE5", "1")

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

    def fake_evaluate_model(received_training_result, received_bundle):
        calls["evaluate_model"] = (received_training_result, received_bundle)
        return evaluation_result

    def fake_reload_smoke_test(received_bundle, received_training_result):
        calls["reload_saved_model_smoke_test"] = (
            received_bundle,
            received_training_result,
        )
        return {"sample_count": 1}

    def fake_format_evaluation_summary(received_result):
        calls["format_evaluation_summary"] = received_result
        return "RMSE: 6.250000\nMAPE: 5.750000%\nTargets missed but artifacts saved"

    def fake_plot_predictions(actual_prices, predicted_prices, rmse, mape):
        calls["plot_predictions"] = {
            "actual_prices": actual_prices,
            "predicted_prices": predicted_prices,
            "rmse": rmse,
            "mape": mape,
        }
        return generated_paths["prediction"]

    def fake_plot_predictions_with_confidence_bands(
        actual_prices, predicted_prices, rmse, mape
    ):
        calls["plot_predictions_with_confidence_bands"] = {
            "actual_prices": actual_prices,
            "predicted_prices": predicted_prices,
            "rmse": rmse,
            "mape": mape,
        }
        return generated_paths["bands"]

    def fake_plot_residuals(actual_prices, predicted_prices):
        calls["plot_residuals"] = {
            "actual_prices": actual_prices,
            "predicted_prices": predicted_prices,
        }
        return generated_paths["residuals"]

    def fake_plot_candlestick_chart(loaded_df):
        calls["plot_candlestick_chart"] = loaded_df
        return generated_paths["candlestick"]

    def fake_plot_feature_correlation_heatmap(loaded_df):
        calls["plot_feature_correlation_heatmap"] = loaded_df
        return generated_paths["heatmap"]

    monkeypatch.setattr(main_module, "evaluate_model", fake_evaluate_model)
    monkeypatch.setattr(
        main_module,
        "reload_saved_model_smoke_test",
        fake_reload_smoke_test,
    )
    monkeypatch.setattr(
        main_module,
        "format_evaluation_summary",
        fake_format_evaluation_summary,
    )
    monkeypatch.setattr(main_module, "plot_predictions", fake_plot_predictions)
    monkeypatch.setattr(
        main_module,
        "plot_predictions_with_confidence_bands",
        fake_plot_predictions_with_confidence_bands,
    )
    monkeypatch.setattr(main_module, "plot_residuals", fake_plot_residuals)
    monkeypatch.setattr(
        main_module, "plot_candlestick_chart", fake_plot_candlestick_chart
    )
    monkeypatch.setattr(
        main_module,
        "plot_feature_correlation_heatmap",
        fake_plot_feature_correlation_heatmap,
    )

    main_module.main()

    output = capsys.readouterr().out
    assert "PHASE 4: Evaluation & Visualization" in output
    assert "RMSE: 6.250000" in output
    assert "MAPE: 5.750000%" in output
    assert "Targets missed but artifacts saved" in output
    assert "Prediction plot: output/AAPL_prediction.png" in output
    assert "Prediction bands plot: output/AAPL_prediction_with_bands.png" in output
    assert "Residual plot: output/residuals.png" in output
    assert "Candlestick plot: output/candlestick.png" in output
    assert "Correlation heatmap: output/correlation_heatmap.png" in output
    assert "Metrics artifact: output/metrics.json" in output
    assert calls["evaluate_model"] == (training_result, bundle)
    assert calls["reload_saved_model_smoke_test"] == (bundle, training_result)
    assert calls["format_evaluation_summary"] is evaluation_result
    assert calls["plot_predictions"] == {
        "actual_prices": evaluation_result["actual_usd"],
        "predicted_prices": evaluation_result["predictions_usd"],
        "rmse": evaluation_result["metrics"]["rmse"],
        "mape": evaluation_result["metrics"]["mape"],
    }
    assert calls["plot_predictions_with_confidence_bands"] == {
        "actual_prices": evaluation_result["actual_usd"],
        "predicted_prices": evaluation_result["predictions_usd"],
        "rmse": evaluation_result["metrics"]["rmse"],
        "mape": evaluation_result["metrics"]["mape"],
    }
    assert calls["plot_residuals"] == {
        "actual_prices": evaluation_result["actual_usd"],
        "predicted_prices": evaluation_result["predictions_usd"],
    }
    assert calls["plot_candlestick_chart"] is df
    assert calls["plot_feature_correlation_heatmap"] is df

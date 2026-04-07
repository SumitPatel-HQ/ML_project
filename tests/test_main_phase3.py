import importlib

import pandas as pd
import pytest


def _load_main_module():
    try:
        return importlib.import_module("main")
    except ModuleNotFoundError as exc:
        pytest.fail(f"main.py not implemented: {exc}")


def test_main_prints_phase3_training_proof(monkeypatch, capsys):
    main_module = _load_main_module()
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2020-01-01", periods=3, freq="B"),
    )
    preprocessing_bundle = {
        "X_train": type("FakeTensor", (), {"shape": (16, 60, 1)})(),
        "metadata": {
            "X_train_shape": (16, 60, 1),
            "X_test_shape": (4, 60, 1),
        },
    }
    training_result = {
        "checkpoint_path": "output/best_model.h5",
        "sidecar_path": "output/training_history.json",
        "metadata": {"best_epoch": 7},
    }
    calls = {}
    fake_model = object()

    monkeypatch.setattr(main_module, "setup_environment", lambda: None)
    monkeypatch.setattr(main_module, "load_data", lambda path: df)
    monkeypatch.setattr(main_module, "display_statistics", lambda loaded_df: None)
    monkeypatch.setattr(main_module, "check_missing_values", lambda loaded_df: 0)
    monkeypatch.setattr(
        main_module, "plot_price_history", lambda loaded_df: "output/raw_price.png"
    )

    def fake_preprocess(loaded_df):
        calls["preprocess_df"] = loaded_df
        return preprocessing_bundle

    monkeypatch.setattr(main_module, "preprocess", fake_preprocess)
    monkeypatch.setattr(
        main_module,
        "format_preprocessing_proof",
        lambda bundle: "X_train shape: (16, 60, 1)",
    )

    def fake_build_model(input_shape):
        calls["build_input_shape"] = input_shape
        return fake_model

    def fake_format_model_summary(model):
        calls["summary_model"] = model
        return "LSTM\nDropout\nDense"

    def fake_train_model(model, bundle):
        calls["train_model"] = (model, bundle)
        return training_result

    def fake_format_training_summary(bundle):
        calls["summary_bundle"] = bundle
        return (
            "Best epoch: 7\n"
            "EarlyStopping: Triggered at epoch 12\n"
            "Model: output/best_model.h5\n"
            "Training sidecar: output/training_history.json"
        )

    monkeypatch.setattr(main_module, "build_model", fake_build_model)
    monkeypatch.setattr(main_module, "format_model_summary", fake_format_model_summary)
    monkeypatch.setattr(main_module, "train_model", fake_train_model)
    monkeypatch.setattr(
        main_module, "format_training_summary", fake_format_training_summary
    )

    main_module.main()

    output = capsys.readouterr().out
    assert "PHASE 3: Model Architecture & Training" in output
    assert "LSTM" in output
    assert "Best epoch: 7" in output
    assert "EarlyStopping" in output
    assert "best_model.h5" in output
    assert calls["build_input_shape"] == preprocessing_bundle["X_train"].shape[1:]
    assert calls["summary_model"] is fake_model
    assert calls["train_model"] == (fake_model, preprocessing_bundle)
    assert calls["summary_bundle"] is training_result

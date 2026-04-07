import importlib

import pandas as pd
import pytest


def _load_main_module():
    try:
        return importlib.import_module("main")
    except ModuleNotFoundError as exc:
        pytest.fail(f"main.py not implemented: {exc}")


def test_main_prints_phase2_preprocessing_proof(monkeypatch, capsys):
    main_module = _load_main_module()
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2020-01-01", periods=3, freq="B"),
    )
    bundle = {
        "metadata": {
            "X_train_shape": (16, 60, 1),
            "X_test_shape": (4, 60, 1),
        }
    }
    calls = {}

    monkeypatch.setattr(
        main_module, "setup_environment", lambda: calls.setdefault("setup", True)
    )

    def fake_load_data(path):
        calls["load_path"] = path
        return df

    def fake_display_statistics(loaded_df):
        calls["stats_df"] = loaded_df

    def fake_check_missing_values(loaded_df):
        calls["missing_df"] = loaded_df
        return 0

    def fake_plot_price_history(loaded_df):
        calls["plot_df"] = loaded_df
        return "output/raw_price.png"

    monkeypatch.setattr(main_module, "load_data", fake_load_data)
    monkeypatch.setattr(main_module, "display_statistics", fake_display_statistics)
    monkeypatch.setattr(main_module, "check_missing_values", fake_check_missing_values)
    monkeypatch.setattr(main_module, "plot_price_history", fake_plot_price_history)

    def fake_preprocess(loaded_df):
        calls["preprocess_df"] = loaded_df
        return bundle

    def fake_format_preprocessing_proof(received_bundle):
        calls["proof_bundle"] = received_bundle
        return "X_train shape: (16, 60, 1)\nTrain date range: 2020-01-01 to 2020-03-31"

    monkeypatch.setattr(main_module, "preprocess", fake_preprocess)
    monkeypatch.setattr(
        main_module, "format_preprocessing_proof", fake_format_preprocessing_proof
    )

    main_module.main()

    output = capsys.readouterr().out
    assert "PHASE 2: Preprocessing & Sequence Generation" in output
    assert "X_train shape: (16, 60, 1)" in output
    assert "Train date range: 2020-01-01 to 2020-03-31" in output
    assert calls["preprocess_df"] is df
    assert calls["proof_bundle"] is bundle

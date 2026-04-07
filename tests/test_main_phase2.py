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
    monkeypatch.setattr(
        main_module, "load_data", lambda path: calls.setdefault("load_path", path) or df
    )
    monkeypatch.setattr(
        main_module,
        "display_statistics",
        lambda loaded_df: calls.setdefault("stats_df", loaded_df),
    )
    monkeypatch.setattr(
        main_module,
        "check_missing_values",
        lambda loaded_df: calls.setdefault("missing_df", loaded_df) or 0,
    )
    monkeypatch.setattr(
        main_module,
        "plot_price_history",
        lambda loaded_df: (
            calls.setdefault("plot_df", loaded_df) or "output/raw_price.png"
        ),
    )

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

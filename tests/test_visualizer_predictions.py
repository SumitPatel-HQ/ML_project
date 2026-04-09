import importlib

import matplotlib.pyplot as plt
import numpy as np
import pytest
import pandas as pd


def _load_visualizer_module():
    try:
        return importlib.reload(importlib.import_module("src.visualizer"))
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.visualizer module not implemented: {exc}")


def test_plot_predictions_saves_default_artifact_with_locked_labels_and_title(
    monkeypatch, tmp_path
):
    visualizer_module = _load_visualizer_module()
    captured = {}
    real_subplots = plt.subplots

    def _capturing_subplots(*args, **kwargs):
        fig, ax = real_subplots(*args, **kwargs)
        captured["fig"] = fig
        captured["ax"] = ax
        return fig, ax

    monkeypatch.setattr(visualizer_module.plt, "subplots", _capturing_subplots)
    monkeypatch.setattr(visualizer_module, "OUTPUT_DIR", str(tmp_path))

    output_path = visualizer_module.plot_predictions(
        actual_prices=np.array([101.0, 102.5, 104.0]),
        predicted_prices=np.array([100.5, 102.0, 103.5]),
        rmse=1.2345,
        mape=2.3456,
    )

    lines = captured["ax"].lines
    assert output_path.endswith("AAPL_prediction.png")
    assert tmp_path.joinpath("AAPL_prediction.png").exists()
    assert len(lines) == 2
    assert lines[0].get_color() == "#1f77b4"
    assert lines[0].get_linestyle() == "-"
    assert lines[1].get_color() == "#ff7f0e"
    assert lines[1].get_linestyle() == "--"
    assert captured["ax"].get_xlabel() == "Trading Days (Test Set)"
    assert captured["ax"].get_ylabel() == "Close Price (USD)"
    title = captured["ax"].get_title()
    assert "RMSE" in title
    assert "MAPE" in title


def test_plot_predictions_with_confidence_bands_saves_artifact_and_shaded_band(
    monkeypatch, tmp_path
):
    visualizer_module = _load_visualizer_module()
    captured = {}
    real_subplots = plt.subplots

    def _capturing_subplots(*args, **kwargs):
        fig, ax = real_subplots(*args, **kwargs)
        captured["fig"] = fig
        captured["ax"] = ax
        return fig, ax

    monkeypatch.setattr(visualizer_module.plt, "subplots", _capturing_subplots)
    monkeypatch.setattr(visualizer_module, "OUTPUT_DIR", str(tmp_path))

    output_path = visualizer_module.plot_predictions_with_confidence_bands(
        actual_prices=np.array([101.0, 102.5, 104.0]),
        predicted_prices=np.array([100.5, 102.0, 103.5]),
        rmse=1.2345,
        mape=2.3456,
    )

    assert output_path.endswith("AAPL_prediction_with_bands.png")
    assert tmp_path.joinpath("AAPL_prediction_with_bands.png").exists()
    assert len(captured["ax"].lines) == 2
    assert len(captured["ax"].collections) == 1
    assert captured["ax"].get_xlabel() == "Trading Days (Test Set)"


def test_plot_residuals_saves_artifact_with_zero_line_and_sigma_band(
    monkeypatch, tmp_path
):
    visualizer_module = _load_visualizer_module()
    captured = {}
    real_subplots = plt.subplots

    def _capturing_subplots(*args, **kwargs):
        fig, ax = real_subplots(*args, **kwargs)
        captured["fig"] = fig
        captured["ax"] = ax
        return fig, ax

    monkeypatch.setattr(visualizer_module.plt, "subplots", _capturing_subplots)
    monkeypatch.setattr(visualizer_module, "OUTPUT_DIR", str(tmp_path))

    output_path = visualizer_module.plot_residuals(
        actual_prices=np.array([101.0, 102.5, 104.0]),
        predicted_prices=np.array([100.5, 102.0, 103.5]),
    )

    assert output_path.endswith("residuals.png")
    assert tmp_path.joinpath("residuals.png").exists()
    assert len(captured["ax"].lines) == 2
    assert len(captured["ax"].collections) == 1
    assert captured["ax"].get_ylabel() == "Residual (USD)"


def test_plot_candlestick_chart_warns_and_skips_when_mplfinance_missing(
    monkeypatch, capsys
):
    visualizer_module = _load_visualizer_module()
    df = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
        },
        index=pd.date_range("2020-01-01", periods=2, freq="B"),
    )

    real_import_module = visualizer_module.importlib.import_module

    def _missing_mplfinance(name):
        if name == "mplfinance":
            raise ModuleNotFoundError("No module named 'mplfinance'")
        return real_import_module(name)

    monkeypatch.setattr(
        visualizer_module.importlib, "import_module", _missing_mplfinance
    )

    output_path = visualizer_module.plot_candlestick_chart(df)

    assert output_path is None
    assert (
        "[WARN] mplfinance not installed; skipping candlestick plot"
        in capsys.readouterr().out
    )


def test_plot_feature_correlation_heatmap_warns_and_skips_when_seaborn_missing(
    monkeypatch, capsys
):
    visualizer_module = _load_visualizer_module()
    df = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        },
        index=pd.date_range("2020-01-01", periods=2, freq="B"),
    )

    real_import_module = visualizer_module.importlib.import_module

    def _missing_seaborn(name):
        if name == "seaborn":
            raise ModuleNotFoundError("No module named 'seaborn'")
        return real_import_module(name)

    monkeypatch.setattr(visualizer_module.importlib, "import_module", _missing_seaborn)

    output_path = visualizer_module.plot_feature_correlation_heatmap(df)

    assert output_path is None
    assert (
        "[WARN] seaborn not installed; skipping correlation heatmap"
        in capsys.readouterr().out
    )


def test_plot_feature_correlation_heatmap_builds_balanced_features_for_close_only_data(
    monkeypatch, tmp_path
):
    visualizer_module = _load_visualizer_module()
    captured = {}

    class _FakeSeaborn:
        @staticmethod
        def heatmap(data, **kwargs):
            captured["corr"] = data
            captured["kwargs"] = kwargs

    real_import_module = visualizer_module.importlib.import_module

    def _import_with_fake_seaborn(name):
        if name == "seaborn":
            return _FakeSeaborn()
        return real_import_module(name)

    close = np.linspace(120.0, 180.0, 80) + np.sin(np.arange(80)) * 2.0
    df = pd.DataFrame(
        {"Close": close},
        index=pd.date_range("2020-01-01", periods=80, freq="B"),
    )

    monkeypatch.setattr(
        visualizer_module.importlib, "import_module", _import_with_fake_seaborn
    )
    monkeypatch.setattr(visualizer_module, "OUTPUT_DIR", str(tmp_path))

    output_path = visualizer_module.plot_feature_correlation_heatmap(df)

    assert output_path.endswith("correlation_heatmap.png")
    assert tmp_path.joinpath("correlation_heatmap.png").exists()
    assert "corr" in captured
    expected_features = {
        "Close",
        "Return_1D",
        "Log_Return_1D",
        "SMA_7",
        "SMA_21",
        "Volatility_7",
        "Volatility_21",
        "Momentum_5",
        "Momentum_10",
        "EMA_12",
        "EMA_26",
        "RSI_14",
    }
    assert expected_features.issubset(set(captured["corr"].columns))


def test_plot_feature_correlation_heatmap_warns_when_close_only_data_too_short(
    monkeypatch, capsys
):
    visualizer_module = _load_visualizer_module()

    class _FakeSeaborn:
        @staticmethod
        def heatmap(data, **kwargs):
            raise AssertionError("heatmap should not be called")

    real_import_module = visualizer_module.importlib.import_module

    def _import_with_fake_seaborn(name):
        if name == "seaborn":
            return _FakeSeaborn()
        return real_import_module(name)

    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2020-01-01", periods=3, freq="B"),
    )

    monkeypatch.setattr(
        visualizer_module.importlib, "import_module", _import_with_fake_seaborn
    )

    output_path = visualizer_module.plot_feature_correlation_heatmap(df)

    assert output_path is None
    assert (
        "[WARN] Close-only dataset does not have enough history"
        in capsys.readouterr().out
    )

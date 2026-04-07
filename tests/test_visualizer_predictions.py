import importlib

import matplotlib.pyplot as plt
import numpy as np
import pytest


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

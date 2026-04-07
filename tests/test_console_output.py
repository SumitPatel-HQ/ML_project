import io
import sys

import pandas as pd

from src import data_loader, visualizer


def test_load_data_prints_ascii_safe_status_messages(monkeypatch, tmp_path):
    csv_path = tmp_path / "AAPL.csv"
    csv_path.write_text(
        "Date,Close\n2020-01-01,100\n2020-01-02,101\n", encoding="utf-8"
    )

    stdout_buffer = io.BytesIO()
    ascii_stdout = io.TextIOWrapper(stdout_buffer, encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", ascii_stdout)

    df = data_loader.load_data(str(csv_path))
    ascii_stdout.flush()

    assert list(df.columns) == ["Close"]
    assert "Loaded data from" in stdout_buffer.getvalue().decode("cp1252")


def test_plot_price_history_prints_ascii_safe_status_messages(monkeypatch, tmp_path):
    df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]},
        index=pd.date_range("2020-01-01", periods=3, freq="B"),
    )
    stdout_buffer = io.BytesIO()
    ascii_stdout = io.TextIOWrapper(stdout_buffer, encoding="cp1252")

    monkeypatch.setattr(sys, "stdout", ascii_stdout)
    monkeypatch.setattr(visualizer, "OUTPUT_DIR", str(tmp_path))

    output_path = visualizer.plot_price_history(df)
    ascii_stdout.flush()

    assert output_path.endswith("raw_price.png")
    assert "Saved plot to" in stdout_buffer.getvalue().decode("cp1252")

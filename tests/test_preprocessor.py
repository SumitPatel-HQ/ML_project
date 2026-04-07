import importlib

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import MinMaxScaler


def _load_preprocessor_api():
    try:
        module = importlib.import_module("src.preprocessor")
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.preprocessor module not implemented: {exc}")

    missing = [
        name
        for name in ("preprocess", "format_preprocessing_proof")
        if not hasattr(module, name)
    ]
    if missing:
        pytest.fail(f"src.preprocessor missing public API: {missing}")

    return module.preprocess, module.format_preprocessing_proof


def _build_dataframe(length=120, start="2020-01-01"):
    dates = pd.date_range(start=start, periods=length, freq="B")
    close = np.arange(100.0, 100.0 + length)
    return pd.DataFrame(
        {
            "Open": close - 1,
            "High": close + 1,
            "Low": close - 2,
            "Close": close,
            "Volume": np.arange(length) + 1_000,
        },
        index=dates,
    )


def test_preprocess_returns_lstm_ready_tensors():
    preprocess, _ = _load_preprocessor_api()
    df = _build_dataframe()

    bundle = preprocess(df)

    assert set(bundle) == {
        "X_train",
        "y_train",
        "X_test",
        "y_test",
        "scaler",
        "metadata",
    }
    assert bundle["X_train"].shape[1:] == (60, 1)
    assert bundle["X_test"].shape[1:] == (60, 1)
    assert bundle["y_train"].ndim == 1
    assert bundle["y_test"].ndim == 1
    assert isinstance(bundle["scaler"], MinMaxScaler)


def test_preprocess_metadata_records_split_shapes_and_feature_context():
    preprocess, _ = _load_preprocessor_api()
    df = _build_dataframe()

    bundle = preprocess(df)
    metadata = bundle["metadata"]

    expected_keys = {
        "feature_name",
        "window_size",
        "train_split",
        "split_index",
        "train_date_range",
        "test_date_range",
        "train_sequence_count",
        "test_sequence_count",
        "X_train_shape",
        "y_train_shape",
        "X_test_shape",
        "y_test_shape",
        "train_scaled_min",
        "train_scaled_max",
        "test_scaled_min",
        "test_scaled_max",
        "first_sequence_preview",
        "first_sequence_target",
    }

    assert expected_keys <= set(metadata)
    assert metadata["feature_name"] == "Close"
    assert metadata["window_size"] == 60
    assert metadata["train_split"] == 0.8
    assert metadata["split_index"] == int(len(df) * 0.8)
    assert metadata["train_date_range"] == (
        df.index[0].strftime("%Y-%m-%d"),
        df.index[95].strftime("%Y-%m-%d"),
    )
    assert metadata["test_date_range"] == (
        df.index[96].strftime("%Y-%m-%d"),
        df.index[-1].strftime("%Y-%m-%d"),
    )
    assert metadata["train_sequence_count"] == bundle["X_train"].shape[0]
    assert metadata["test_sequence_count"] == bundle["X_test"].shape[0]
    assert metadata["X_train_shape"] == bundle["X_train"].shape
    assert metadata["y_train_shape"] == bundle["y_train"].shape
    assert metadata["X_test_shape"] == bundle["X_test"].shape
    assert metadata["y_test_shape"] == bundle["y_test"].shape


def test_preprocess_preserves_test_continuity_with_last_train_window():
    preprocess, _ = _load_preprocessor_api()
    df = _build_dataframe()

    bundle = preprocess(df)
    split_index = int(len(df) * 0.8)
    train_raw = df[["Close"]].values[:split_index]
    test_raw = df[["Close"]].values[split_index:]

    expected_scaler = MinMaxScaler(feature_range=(0, 1))
    expected_scaler.fit(train_raw)
    expected_test_input = np.concatenate([train_raw[-60:], test_raw])
    expected_test_scaled = expected_scaler.transform(expected_test_input)

    np.testing.assert_allclose(bundle["X_test"][0, :, 0], expected_test_scaled[:60, 0])
    np.testing.assert_allclose(bundle["y_test"][0], expected_test_scaled[60, 0])


def test_format_preprocessing_proof_includes_required_markers():
    preprocess, format_preprocessing_proof = _load_preprocessor_api()
    df = _build_dataframe()

    proof = format_preprocessing_proof(preprocess(df))

    assert "X_train shape:" in proof
    assert "y_train shape:" in proof
    assert "X_test shape:" in proof
    assert "y_test shape:" in proof
    assert "Train date range:" in proof
    assert "Test date range:" in proof
    assert "First normalized sequence preview:" in proof
    assert "First target:" in proof


@pytest.mark.parametrize(
    ("mutator", "match"),
    [
        (lambda df: df.drop(columns=["Close"]), "Close|feature"),
        (
            lambda df: df.assign(Close=df["Close"].mask(df.index == df.index[5])),
            "missing|null|NaN",
        ),
    ],
)
def test_preprocess_rejects_invalid_dataframe_inputs(mutator, match):
    preprocess, _ = _load_preprocessor_api()
    df = _build_dataframe()

    with pytest.raises(ValueError, match=match):
        preprocess(mutator(df))


@pytest.mark.parametrize(
    ("cfg", "match"),
    [
        ({"train_split": 0}, "train_split"),
        ({"train_split": 1.0}, "train_split"),
        ({"window_size": 0}, "window_size"),
        ({"window_size": -3}, "window_size"),
    ],
)
def test_preprocess_rejects_invalid_configuration(cfg, match):
    preprocess, _ = _load_preprocessor_api()

    with pytest.raises(ValueError, match=match):
        preprocess(_build_dataframe(), cfg=cfg)


def test_preprocess_rejects_too_short_dataset():
    preprocess, _ = _load_preprocessor_api()

    with pytest.raises(ValueError, match="too short|enough rows|sequence"):
        preprocess(_build_dataframe(length=75))

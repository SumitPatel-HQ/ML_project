import builtins
import importlib
import sys
import types

import pytest


def _load_model_module():
    try:
        module = importlib.import_module("src.model")
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.model module not implemented: {exc}")

    missing = [
        name
        for name in ("build_model", "format_model_summary")
        if not hasattr(module, name)
    ]
    if missing:
        pytest.fail(f"src.model missing public API: {missing}")

    return importlib.reload(module)


class FakeLSTM:
    def __init__(self, units, return_sequences=False, input_shape=None):
        self.units = units
        self.return_sequences = return_sequences
        self.input_shape = input_shape


class FakeDropout:
    def __init__(self, rate):
        self.rate = rate


class FakeDense:
    def __init__(self, units, activation=None):
        self.units = units
        self.activation = activation


class FakeAdam:
    def __init__(self, learning_rate):
        self.learning_rate = learning_rate


class FakeSequential:
    def __init__(self, layers):
        self.layers = layers
        self.optimizer = None
        self.loss = None

    def compile(self, optimizer, loss):
        self.optimizer = optimizer
        self.loss = loss

    def summary(self, print_fn=None):
        printer = print_fn or (lambda line: None)
        printer("Model: sequential")
        for layer in self.layers:
            if isinstance(layer, FakeLSTM):
                printer(
                    f"LSTM units={layer.units} return_sequences={layer.return_sequences}"
                )
            elif isinstance(layer, FakeDropout):
                printer(f"Dropout rate={layer.rate}")
            elif isinstance(layer, FakeDense):
                printer(f"Dense units={layer.units} activation={layer.activation}")


def _install_fake_tensorflow(monkeypatch):
    tensorflow = types.ModuleType("tensorflow")
    keras = types.ModuleType("tensorflow.keras")
    models = types.ModuleType("tensorflow.keras.models")
    layers = types.ModuleType("tensorflow.keras.layers")
    optimizers = types.ModuleType("tensorflow.keras.optimizers")

    models.Sequential = FakeSequential
    layers.LSTM = FakeLSTM
    layers.Dropout = FakeDropout
    layers.Dense = FakeDense
    optimizers.Adam = FakeAdam

    keras.Sequential = FakeSequential
    keras.models = models
    keras.layers = layers
    keras.optimizers = optimizers
    tensorflow.keras = keras

    monkeypatch.setitem(sys.modules, "tensorflow", tensorflow)
    monkeypatch.setitem(sys.modules, "tensorflow.keras", keras)
    monkeypatch.setitem(sys.modules, "tensorflow.keras.models", models)
    monkeypatch.setitem(sys.modules, "tensorflow.keras.layers", layers)
    monkeypatch.setitem(sys.modules, "tensorflow.keras.optimizers", optimizers)


def test_build_model_returns_required_stacked_lstm_architecture(monkeypatch):
    _install_fake_tensorflow(monkeypatch)
    model_module = _load_model_module()

    model = model_module.build_model()

    assert [layer.__class__.__name__ for layer in model.layers] == [
        "FakeLSTM",
        "FakeDropout",
        "FakeLSTM",
        "FakeDropout",
        "FakeDense",
        "FakeDense",
    ]
    assert model.layers[0].units == 64
    assert model.layers[0].return_sequences is True
    assert model.layers[0].input_shape == (60, 1)
    assert model.layers[1].rate == 0.2
    assert model.layers[2].units == 64
    assert model.layers[2].return_sequences is False
    assert model.layers[3].rate == 0.2
    assert model.layers[4].units == 32
    assert model.layers[4].activation == "relu"
    assert model.layers[5].units == 1


def test_build_model_compiles_with_adam_and_mean_squared_error(monkeypatch):
    _install_fake_tensorflow(monkeypatch)
    model_module = _load_model_module()

    model = model_module.build_model()

    assert model.optimizer.__class__.__name__ == "FakeAdam"
    assert model.optimizer.learning_rate == 0.001
    assert model.loss == "mean_squared_error"


def test_format_model_summary_contains_lstm_dropout_and_dense_markers(monkeypatch):
    _install_fake_tensorflow(monkeypatch)
    model_module = _load_model_module()

    summary_text = model_module.format_model_summary(model_module.build_model())

    assert "LSTM" in summary_text
    assert "Dropout" in summary_text
    assert "Dense" in summary_text


def test_build_model_raises_clear_runtime_error_when_tensorflow_is_unavailable_d06_d07(
    monkeypatch,
):
    model_module = _load_model_module()
    real_import = builtins.__import__

    def _raising_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("tensorflow"):
            raise ModuleNotFoundError("No module named 'tensorflow'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _raising_import)

    with pytest.raises(
        RuntimeError,
        match="TensorFlow is required to build or train the Phase 3 LSTM model.",
    ):
        model_module.build_model()

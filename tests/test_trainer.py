import builtins
import importlib
import json
import sys
import types

import pytest


def _load_trainer_module():
    try:
        module = importlib.import_module("src.trainer")
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.trainer module not implemented: {exc}")

    missing = [
        name
        for name in ("train_model", "format_training_summary")
        if not hasattr(module, name)
    ]
    if missing:
        pytest.fail(f"src.trainer missing public API: {missing}")

    return importlib.reload(module)


class FakeEarlyStopping:
    def __init__(self, monitor, patience, restore_best_weights, verbose):
        self.monitor = monitor
        self.patience = patience
        self.restore_best_weights = restore_best_weights
        self.verbose = verbose


class FakeModelCheckpoint:
    def __init__(self, filepath, monitor, save_best_only, verbose):
        self.filepath = filepath
        self.monitor = monitor
        self.save_best_only = save_best_only
        self.verbose = verbose


class FakeHistory:
    def __init__(self):
        self.history = {
            "loss": [0.8, 0.5, 0.45],
            "val_loss": [0.9, 0.4, 0.6],
        }
        self.epoch = [0, 1, 2]


class FakeModel:
    def __init__(self):
        self.fit_calls = []

    def fit(self, X_train, y_train, **kwargs):
        self.fit_calls.append((X_train, y_train, kwargs))
        return FakeHistory()


def _install_fake_tensorflow_callbacks(monkeypatch):
    tensorflow = types.ModuleType("tensorflow")
    keras = types.ModuleType("tensorflow.keras")
    callbacks = types.ModuleType("tensorflow.keras.callbacks")

    callbacks.EarlyStopping = FakeEarlyStopping
    callbacks.ModelCheckpoint = FakeModelCheckpoint
    keras.callbacks = callbacks
    tensorflow.keras = keras

    monkeypatch.setitem(sys.modules, "tensorflow", tensorflow)
    monkeypatch.setitem(sys.modules, "tensorflow.keras", keras)
    monkeypatch.setitem(sys.modules, "tensorflow.keras.callbacks", callbacks)


def _build_preprocessing_bundle():
    return {
        "X_train": [[1.0], [2.0]],
        "y_train": [0.1, 0.2],
        "X_test": [[3.0]],
        "y_test": [0.3],
        "metadata": {
            "X_train_shape": (16, 60, 1),
            "y_train_shape": (16,),
            "X_test_shape": (4, 60, 1),
            "y_test_shape": (4,),
        },
    }


def test_train_model_returns_structured_training_bundle(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    _install_fake_tensorflow_callbacks(monkeypatch)
    trainer_module = _load_trainer_module()
    model = FakeModel()
    bundle = _build_preprocessing_bundle()

    training_result = trainer_module.train_model(model, bundle)

    fit_X, fit_y, fit_kwargs = model.fit_calls[0]
    assert fit_X is bundle["X_train"]
    assert fit_y is bundle["y_train"]
    assert fit_kwargs["epochs"] == 100
    assert fit_kwargs["batch_size"] == 32
    assert fit_kwargs["validation_split"] == 0.1
    assert fit_kwargs["verbose"] == 2
    assert len(fit_kwargs["callbacks"]) == 2
    assert isinstance(fit_kwargs["callbacks"][0], FakeEarlyStopping)
    assert isinstance(fit_kwargs["callbacks"][1], FakeModelCheckpoint)
    assert fit_kwargs["callbacks"][0].monitor == "val_loss"
    assert fit_kwargs["callbacks"][0].patience == 10
    assert fit_kwargs["callbacks"][0].restore_best_weights is True
    assert fit_kwargs["callbacks"][1].filepath == "output/best_model.h5"
    assert fit_kwargs["callbacks"][1].save_best_only is True
    assert set(training_result) == {
        "model",
        "history",
        "checkpoint_path",
        "sidecar_path",
        "metadata",
    }
    assert training_result["model"] is model
    assert training_result["checkpoint_path"] == "output/best_model.h5"
    assert training_result["sidecar_path"] == "output/training_history.json"


def test_train_model_metadata_and_sidecar_capture_locked_training_details(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    _install_fake_tensorflow_callbacks(monkeypatch)
    trainer_module = _load_trainer_module()

    training_result = trainer_module.train_model(
        FakeModel(), _build_preprocessing_bundle()
    )
    metadata = training_result["metadata"]

    assert metadata["epochs_run"] == 3
    assert metadata["best_epoch"] == 2
    assert metadata["best_val_loss"] == 0.4
    assert metadata["stopped_epoch"] == 3
    assert metadata["early_stopped"] is False
    assert metadata["batch_size"] == 32
    assert metadata["validation_split"] == 0.1
    assert metadata["patience"] == 10
    assert metadata["monitor"] == "val_loss"
    assert metadata["checkpoint_path"] == "output/best_model.h5"
    assert metadata["X_train_shape"] == [16, 60, 1]
    assert metadata["y_train_shape"] == [16]

    sidecar = json.loads(
        tmp_path.joinpath("output", "training_history.json").read_text()
    )
    assert sidecar["loss"] == [0.8, 0.5, 0.45]
    assert sidecar["val_loss"] == [0.9, 0.4, 0.6]
    assert sidecar["best_epoch"] == 2
    assert sidecar["best_val_loss"] == 0.4
    assert sidecar["checkpoint_path"] == "output/best_model.h5"


def test_format_training_summary_contains_best_epoch_early_stopping_and_artifacts(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    _install_fake_tensorflow_callbacks(monkeypatch)
    trainer_module = _load_trainer_module()

    summary = trainer_module.format_training_summary(
        trainer_module.train_model(FakeModel(), _build_preprocessing_bundle())
    )

    assert "Best epoch: 2" in summary
    assert "Best val_loss: 0.400000" in summary
    assert "EarlyStopping:" in summary
    assert "Model: output/best_model.h5" in summary
    assert "Training sidecar: output/training_history.json" in summary


def test_train_model_raises_clear_runtime_error_when_tensorflow_is_unavailable_d06_d07(
    monkeypatch,
):
    trainer_module = _load_trainer_module()
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
        trainer_module.train_model(FakeModel(), _build_preprocessing_bundle())

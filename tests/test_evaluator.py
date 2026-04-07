import builtins
import importlib
import json
import sys
import types

import numpy as np
import pytest


def _load_evaluator_module():
    try:
        module = importlib.import_module("src.evaluator")
    except ModuleNotFoundError as exc:
        pytest.fail(f"src.evaluator module not implemented: {exc}")

    missing = [
        name
        for name in (
            "evaluate_model",
            "reload_saved_model_smoke_test",
            "format_evaluation_summary",
        )
        if not hasattr(module, name)
    ]
    if missing:
        pytest.fail(f"src.evaluator missing public API: {missing}")

    return importlib.reload(module)


class FakeModel:
    def __init__(self, predictions):
        self.predictions = np.array(predictions, dtype=float)
        self.predict_calls = []

    def predict(self, X_test, verbose=0):
        self.predict_calls.append((X_test, verbose))
        return self.predictions


class FakeScaler:
    def __init__(self, offset=100.0, multiplier=10.0):
        self.offset = offset
        self.multiplier = multiplier
        self.inverse_calls = []

    def inverse_transform(self, values):
        values = np.array(values, dtype=float)
        self.inverse_calls.append(values.copy())
        return values * self.multiplier + self.offset


def _build_preprocessing_bundle():
    return {
        "X_test": np.array(
            [
                [[0.1], [0.2], [0.3]],
                [[0.2], [0.3], [0.4]],
                [[0.3], [0.4], [0.5]],
            ],
            dtype=float,
        ),
        "y_test": np.array([0.5, 0.7, 0.9], dtype=float),
        "scaler": FakeScaler(),
    }


def _build_training_result(tmp_path, model=None):
    checkpoint_path = tmp_path.joinpath("output", "best_model.h5")
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text("fake model bytes", encoding="utf-8")
    return {
        "model": model or FakeModel([[0.4], [0.8], [1.0]]),
        "checkpoint_path": str(checkpoint_path).replace("\\", "/"),
    }


def test_evaluate_model_returns_predictions_metrics_and_artifact(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    evaluator_module = _load_evaluator_module()
    preprocessing_bundle = _build_preprocessing_bundle()
    training_result = _build_training_result(tmp_path)

    result = evaluator_module.evaluate_model(training_result, preprocessing_bundle)

    assert (
        training_result["model"].predict_calls[0][0] is preprocessing_bundle["X_test"]
    )
    assert training_result["model"].predict_calls[0][1] == 0
    assert set(result) == {
        "predictions_scaled",
        "actual_scaled",
        "predictions_usd",
        "actual_usd",
        "metrics",
        "thresholds",
        "passes",
        "metrics_path",
        "checkpoint_path",
    }
    np.testing.assert_allclose(result["predictions_scaled"], np.array([0.4, 0.8, 1.0]))
    np.testing.assert_allclose(result["actual_scaled"], np.array([0.5, 0.7, 0.9]))
    np.testing.assert_allclose(
        result["predictions_usd"], np.array([104.0, 108.0, 110.0])
    )
    np.testing.assert_allclose(result["actual_usd"], np.array([105.0, 107.0, 109.0]))
    assert result["metrics"]["rmse"] == pytest.approx(1.0)
    assert result["metrics"]["mape"] == pytest.approx(0.930144, rel=1e-6)
    assert result["thresholds"] == {"rmse_target": 5.0, "mape_target": 5.0}
    assert result["passes"] == {"rmse_pass": True, "mape_pass": True}
    assert result["checkpoint_path"] == training_result["checkpoint_path"]
    assert result["metrics_path"] == "output/metrics.json"


def test_evaluate_model_writes_metrics_json_with_thresholds_and_pass_fail(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    evaluator_module = _load_evaluator_module()

    result = evaluator_module.evaluate_model(
        _build_training_result(tmp_path, model=FakeModel([[0.0], [0.1], [0.2]])),
        _build_preprocessing_bundle(),
    )

    metrics = json.loads(tmp_path.joinpath("output", "metrics.json").read_text())
    assert metrics["rmse"] == pytest.approx(result["metrics"]["rmse"])
    assert metrics["mape"] == pytest.approx(result["metrics"]["mape"])
    assert metrics["rmse_target"] == 5.0
    assert metrics["mape_target"] == 5.0
    assert metrics["rmse_pass"] is False
    assert metrics["mape_pass"] is False


def test_reload_saved_model_smoke_test_loads_checkpoint_and_runs_inference(
    monkeypatch, tmp_path
):
    evaluator_module = _load_evaluator_module()
    preprocessing_bundle = _build_preprocessing_bundle()
    training_result = _build_training_result(tmp_path)
    load_calls = []

    class FakeLoadedModel:
        def predict(self, X_test, verbose=0):
            load_calls.append((X_test, verbose))
            return np.array([[0.42]], dtype=float)

    tensorflow = types.ModuleType("tensorflow")
    keras = types.ModuleType("tensorflow.keras")
    models = types.ModuleType("tensorflow.keras.models")

    def _load_model(path):
        load_calls.append(path)
        return FakeLoadedModel()

    models.load_model = _load_model
    keras.models = models
    tensorflow.keras = keras

    monkeypatch.setitem(sys.modules, "tensorflow", tensorflow)
    monkeypatch.setitem(sys.modules, "tensorflow.keras", keras)
    monkeypatch.setitem(sys.modules, "tensorflow.keras.models", models)

    proof = evaluator_module.reload_saved_model_smoke_test(
        preprocessing_bundle, training_result
    )

    assert load_calls[0] == training_result["checkpoint_path"]
    assert load_calls[1][0].shape == (1, 3, 1)
    assert load_calls[1][1] == 0
    assert proof["checkpoint_path"] == training_result["checkpoint_path"]
    assert proof["smoke_prediction_shape"] == [1, 1]
    assert proof["sample_count"] == 1


def test_reload_saved_model_smoke_test_raises_runtime_error_without_tensorflow(
    monkeypatch, tmp_path
):
    evaluator_module = _load_evaluator_module()
    real_import = builtins.__import__

    def _raising_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("tensorflow"):
            raise ModuleNotFoundError("No module named 'tensorflow'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _raising_import)

    with pytest.raises(
        RuntimeError,
        match="TensorFlow is required to reload the saved Phase 3 model for Phase 4 evaluation.",
    ):
        evaluator_module.reload_saved_model_smoke_test(
            _build_preprocessing_bundle(), _build_training_result(tmp_path)
        )


@pytest.mark.parametrize(
    ("training_result", "preprocessing_bundle", "error_message"),
    [
        (
            {"checkpoint_path": "output/best_model.h5"},
            _build_preprocessing_bundle(),
            r"training_result\['model'\] is required",
        ),
        (
            {
                "model": FakeModel([[0.4], [0.8], [1.0]]),
                "checkpoint_path": "output/best_model.h5",
            },
            {"X_test": np.array([[[0.1]]]), "y_test": np.array([0.2])},
            r"preprocessing_bundle\['scaler'\] is required",
        ),
    ],
)
def test_evaluate_model_raises_hard_errors_for_missing_required_inputs(
    monkeypatch, tmp_path, training_result, preprocessing_bundle, error_message
):
    monkeypatch.chdir(tmp_path)
    evaluator_module = _load_evaluator_module()

    if training_result.get("checkpoint_path") == "output/best_model.h5":
        training_result = dict(training_result)
        training_result["checkpoint_path"] = str(
            tmp_path.joinpath("output", "best_model.h5")
        ).replace("\\", "/")

    with pytest.raises((ValueError, RuntimeError), match=error_message):
        evaluator_module.evaluate_model(training_result, preprocessing_bundle)

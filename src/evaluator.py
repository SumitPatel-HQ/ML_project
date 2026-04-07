"""Evaluation helpers for Phase 4 prediction metrics and saved-model proof."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np

from src.config import MAPE_TARGET, METRICS_FILE, MODEL_FILE, OUTPUT_DIR, RMSE_TARGET


TF_RELOAD_REQUIRED_ERROR = (
    "TensorFlow is required to reload the saved Phase 3 model for Phase 4 evaluation."
)


def _build_config(cfg=None):
    overrides = cfg or {}
    return {
        "output_dir": overrides.get("output_dir", OUTPUT_DIR),
        "metrics_file": overrides.get("metrics_file", METRICS_FILE),
        "model_file": overrides.get("model_file", MODEL_FILE),
        "rmse_target": overrides.get("rmse_target", RMSE_TARGET),
        "mape_target": overrides.get("mape_target", MAPE_TARGET),
    }


def _require_mapping_value(mapping, mapping_name, key):
    if key not in mapping or mapping[key] is None:
        raise ValueError(f"{mapping_name}['{key}'] is required")
    return mapping[key]


def _require_checkpoint_path(training_result):
    checkpoint_path = _require_mapping_value(
        training_result, "training_result", "checkpoint_path"
    )
    path = Path(checkpoint_path)
    if not path.exists():
        raise RuntimeError(f"Saved model artifact not found: {checkpoint_path}")
    return checkpoint_path


def _inverse_transform_prices(scaler, values, label):
    try:
        reshaped = np.asarray(values, dtype=float).reshape(-1, 1)
        inverse = scaler.inverse_transform(reshaped)
    except Exception as exc:  # pragma: no cover - defensive contract guard
        raise RuntimeError(f"Failed to inverse-transform {label}") from exc

    return np.asarray(inverse, dtype=float).reshape(-1)


def _compute_metrics(actual_usd, predictions_usd):
    rmse = float(np.sqrt(np.mean(np.square(predictions_usd - actual_usd))))
    denominator = np.where(actual_usd == 0, np.finfo(float).eps, actual_usd)
    mape = float(np.mean(np.abs((actual_usd - predictions_usd) / denominator)) * 100)
    return {"rmse": rmse, "mape": mape}


def _write_metrics_artifact(metrics_path, payload):
    path = Path(metrics_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Failed to write metrics artifact: {metrics_path}") from exc


def evaluate_model(training_result, preprocessing_bundle, cfg=None):
    config = _build_config(cfg)
    model = _require_mapping_value(training_result, "training_result", "model")
    checkpoint_path = _require_checkpoint_path(training_result)
    X_test = _require_mapping_value(
        preprocessing_bundle, "preprocessing_bundle", "X_test"
    )
    y_test = _require_mapping_value(
        preprocessing_bundle, "preprocessing_bundle", "y_test"
    )
    scaler = _require_mapping_value(
        preprocessing_bundle, "preprocessing_bundle", "scaler"
    )

    predictions_scaled = np.asarray(
        model.predict(X_test, verbose=0), dtype=float
    ).reshape(-1)
    actual_scaled = np.asarray(y_test, dtype=float).reshape(-1)

    if predictions_scaled.shape[0] != actual_scaled.shape[0]:
        raise RuntimeError("Prediction count does not match y_test count")

    predictions_usd = _inverse_transform_prices(
        scaler, predictions_scaled, "predictions"
    )
    actual_usd = _inverse_transform_prices(scaler, actual_scaled, "actual prices")
    metrics = _compute_metrics(actual_usd, predictions_usd)
    thresholds = {
        "rmse_target": float(config["rmse_target"]),
        "mape_target": float(config["mape_target"]),
    }
    passes = {
        "rmse_pass": metrics["rmse"] < thresholds["rmse_target"],
        "mape_pass": metrics["mape"] < thresholds["mape_target"],
    }

    metrics_path = (Path(config["output_dir"]) / config["metrics_file"]).as_posix()
    _write_metrics_artifact(
        metrics_path,
        {
            **metrics,
            **thresholds,
            **passes,
            "checkpoint_path": checkpoint_path,
        },
    )

    return {
        "predictions_scaled": predictions_scaled,
        "actual_scaled": actual_scaled,
        "predictions_usd": predictions_usd,
        "actual_usd": actual_usd,
        "metrics": metrics,
        "thresholds": thresholds,
        "passes": passes,
        "metrics_path": metrics_path,
        "checkpoint_path": checkpoint_path,
    }


def reload_saved_model_smoke_test(preprocessing_bundle, training_result, cfg=None):
    _build_config(cfg)
    checkpoint_path = _require_checkpoint_path(training_result)
    X_test = _require_mapping_value(
        preprocessing_bundle, "preprocessing_bundle", "X_test"
    )

    try:
        load_model = importlib.import_module("tensorflow.keras.models").load_model
    except ModuleNotFoundError as exc:
        raise RuntimeError(TF_RELOAD_REQUIRED_ERROR) from exc

    model = load_model(checkpoint_path)
    smoke_input = np.asarray(X_test)[:1]
    if smoke_input.size == 0:
        raise RuntimeError(
            "preprocessing_bundle['X_test'] must contain at least one test sample"
        )

    smoke_prediction = np.asarray(model.predict(smoke_input, verbose=0), dtype=float)
    return {
        "checkpoint_path": checkpoint_path,
        "smoke_prediction_shape": list(smoke_prediction.shape),
        "sample_count": int(smoke_input.shape[0]),
    }


def format_evaluation_summary(result):
    metrics = result["metrics"]
    passes = result["passes"]
    return "\n".join(
        [
            f"RMSE: {metrics['rmse']:.6f} (target < {result['thresholds']['rmse_target']:.1f}) [{passes['rmse_pass']}]",
            f"MAPE: {metrics['mape']:.6f}% (target < {result['thresholds']['mape_target']:.1f}%) [{passes['mape_pass']}]",
            f"Metrics artifact: {result['metrics_path']}",
            f"Model checkpoint: {result['checkpoint_path']}",
        ]
    )

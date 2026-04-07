"""Training helpers for Phase 3 model fitting and artifact capture."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

from src.config import (
    BATCH_SIZE,
    EARLY_STOPPING_MONITOR,
    EARLY_STOPPING_PATIENCE,
    EPOCHS,
    MODEL_FILE,
    OUTPUT_DIR,
    TRAINING_SIDECAR_FILE,
    VALIDATION_SPLIT,
)
from src.model import TF_REQUIRED_ERROR


def _load_callback_runtime():
    try:
        callbacks = importlib.import_module("tensorflow.keras.callbacks")
    except ModuleNotFoundError as exc:
        raise RuntimeError(TF_REQUIRED_ERROR) from exc

    return callbacks.EarlyStopping, callbacks.ModelCheckpoint


def _build_config(cfg=None):
    overrides = cfg or {}
    return {
        "epochs": overrides.get("epochs", EPOCHS),
        "batch_size": overrides.get("batch_size", BATCH_SIZE),
        "validation_split": overrides.get("validation_split", VALIDATION_SPLIT),
        "patience": overrides.get("patience", EARLY_STOPPING_PATIENCE),
        "monitor": overrides.get("monitor", EARLY_STOPPING_MONITOR),
        "output_dir": overrides.get("output_dir", OUTPUT_DIR),
        "model_file": overrides.get("model_file", MODEL_FILE),
        "training_sidecar_file": overrides.get(
            "training_sidecar_file", TRAINING_SIDECAR_FILE
        ),
    }


def _build_paths(config):
    checkpoint_path = str(Path(config["output_dir"]) / config["model_file"])
    sidecar_path = str(Path(config["output_dir"]) / config["training_sidecar_file"])
    return checkpoint_path.replace("\\", "/"), sidecar_path.replace("\\", "/")


def _build_callbacks(config, checkpoint_path):
    EarlyStopping, ModelCheckpoint = _load_callback_runtime()
    early_stopping = EarlyStopping(
        monitor=config["monitor"],
        patience=config["patience"],
        restore_best_weights=True,
        verbose=1,
    )
    model_checkpoint = ModelCheckpoint(
        filepath=checkpoint_path,
        monitor=config["monitor"],
        save_best_only=True,
        verbose=1,
    )
    return [early_stopping, model_checkpoint], early_stopping


def _normalize_shape(value):
    return list(value) if value is not None else None


def _build_metadata(
    history, preprocessing_bundle, config, checkpoint_path, sidecar_path, early_stopping
):
    val_loss_history = history.history.get("val_loss", [])
    loss_history = history.history.get("loss", [])
    epochs_run = len(loss_history)
    best_val_loss = min(val_loss_history) if val_loss_history else None
    best_epoch = val_loss_history.index(best_val_loss) + 1 if val_loss_history else None
    stopped_epoch = getattr(early_stopping, "stopped_epoch", 0) or epochs_run
    early_stopped = bool(getattr(early_stopping, "stopped_epoch", 0))
    preprocessing_metadata = preprocessing_bundle.get("metadata", {})

    return {
        "epochs_run": epochs_run,
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "stopped_epoch": stopped_epoch,
        "early_stopped": early_stopped,
        "batch_size": config["batch_size"],
        "validation_split": config["validation_split"],
        "patience": config["patience"],
        "monitor": config["monitor"],
        "checkpoint_path": checkpoint_path,
        "sidecar_path": sidecar_path,
        "X_train_shape": _normalize_shape(preprocessing_metadata.get("X_train_shape")),
        "y_train_shape": _normalize_shape(preprocessing_metadata.get("y_train_shape")),
        "X_test_shape": _normalize_shape(preprocessing_metadata.get("X_test_shape")),
        "y_test_shape": _normalize_shape(preprocessing_metadata.get("y_test_shape")),
    }


def _write_sidecar(sidecar_path, history, metadata):
    sidecar = {
        "loss": history.history.get("loss", []),
        "val_loss": history.history.get("val_loss", []),
        **metadata,
    }
    path = Path(sidecar_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")


def train_model(model, preprocessing_bundle, cfg=None):
    config = _build_config(cfg)
    checkpoint_path, sidecar_path = _build_paths(config)
    callbacks, early_stopping = _build_callbacks(config, checkpoint_path)

    history = model.fit(
        preprocessing_bundle["X_train"],
        preprocessing_bundle["y_train"],
        epochs=config["epochs"],
        batch_size=config["batch_size"],
        validation_split=config["validation_split"],
        callbacks=callbacks,
        verbose=2,
    )

    metadata = _build_metadata(
        history,
        preprocessing_bundle,
        config,
        checkpoint_path,
        sidecar_path,
        early_stopping,
    )
    _write_sidecar(sidecar_path, history, metadata)

    return {
        "model": model,
        "history": history.history,
        "checkpoint_path": checkpoint_path,
        "sidecar_path": sidecar_path,
        "metadata": metadata,
    }


def format_training_summary(bundle):
    metadata = bundle["metadata"]
    best_val_loss = metadata["best_val_loss"]
    best_val_loss_text = (
        f"{best_val_loss:.6f}" if best_val_loss is not None else "unavailable"
    )
    early_stopping_text = (
        f"Triggered at epoch {metadata['stopped_epoch']}"
        if metadata["early_stopped"]
        else f"Not triggered (ran {metadata['epochs_run']} epochs)"
    )

    return "\n".join(
        [
            f"Best epoch: {metadata['best_epoch']}",
            f"Best val_loss: {best_val_loss_text}",
            f"EarlyStopping: {early_stopping_text}",
            f"Epochs run: {metadata['epochs_run']}",
            f"Model: {bundle['checkpoint_path']}",
            f"Training sidecar: {bundle['sidecar_path']}",
        ]
    )

"""Stock Price Prediction Pipeline - Main Entry Point."""

import os
import sys

from src.config import (
    DATA_PATH,
    OUTPUT_DIR,
    MODEL_FILE,
)
from src.utils import setup_environment
from src.data_loader import load_data, display_statistics, check_missing_values
from src.visualizer import plot_price_history
from src.visualizer import plot_predictions
from src.visualizer import plot_predictions_with_confidence_bands
from src.visualizer import plot_residuals
from src.visualizer import plot_candlestick_chart
from src.visualizer import plot_feature_correlation_heatmap
from src.preprocessor import preprocess, format_preprocessing_proof
from src.model import build_model, format_model_summary
from src.trainer import train_model, format_training_summary
from src.evaluator import (
    evaluate_model,
    reload_saved_model_smoke_test,
    format_evaluation_summary,
)


def _get_phase3_input_shape(bundle):
    X_train = bundle.get("X_train")
    if X_train is not None and hasattr(X_train, "shape"):
        return X_train.shape[1:]

    metadata = bundle.get("metadata", {})
    X_train_shape = metadata.get("X_train_shape")
    if X_train_shape is not None:
        return X_train_shape[1:]

    return None


    return None


def main():
    """
    Execute the stock price prediction pipeline.

    Currently implements Phase 1: Data loading and validation.
    Future phases will be added here as development progresses.
    """
    print("\n" + "=" * 70)
    print(" " * 15 + "STOCK PRICE PREDICTION PIPELINE")
    print(" " * 20 + "LSTM Neural Networks")
    print("=" * 70 + "\n")

    # ==========================================================================
    # SETUP
    # ==========================================================================
    print("Setting up environment...")
    setup_environment()
    print()

    # ==========================================================================
    # PHASE 1: DATA LOADING & VALIDATION
    # ==========================================================================
    print("=" * 70)
    print("PHASE 1: Data Loading & Validation")
    print("=" * 70 + "\n")

    # Load data
    print("Loading data...")
    df = load_data(DATA_PATH)
    print()

    # Display statistics
    display_statistics(df)

    # Check for missing values
    print("Checking data quality...")
    missing_count = check_missing_values(df)
    print()

    # Visualize raw price history
    print("Generating visualization...")
    plot_path = plot_price_history(df)
    print()

    # ==========================================================================
    # PHASE 2: PREPROCESSING & SEQUENCE GENERATION
    # ==========================================================================
    print("=" * 70)
    print("PHASE 2: Preprocessing & Sequence Generation")
    print("=" * 70 + "\n")

    bundle = preprocess(df)
    proof = format_preprocessing_proof(bundle)
    print(proof)
    print()

    # ==========================================================================
    # PHASE 3: MODEL ARCHITECTURE & TRAINING
    # ==========================================================================
    print("=" * 70)
    print("PHASE 3: Model Architecture & Training")
    print("=" * 70 + "\n")

    input_shape = _get_phase3_input_shape(bundle)
    training_result = {"checkpoint_path": "not-run", "sidecar_path": "not-run"}
    if input_shape is not None and "X_train" in bundle:
        checkpoint_path = os.path.join(OUTPUT_DIR, MODEL_FILE)
        if os.path.exists(checkpoint_path) and os.getenv("LSTM_REUSE_MODEL") == "1":
            print(f"Reusing existing model from checkpoint: {checkpoint_path}")
            try:
                from tensorflow.keras.models import load_model

                model = load_model(checkpoint_path)
                training_result = {
                    "model": model,
                    "checkpoint_path": checkpoint_path,
                    "sidecar_path": os.path.join(OUTPUT_DIR, "training_history.json"),
                }
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Failed to load existing model: {e}. Falling back to training.")
                model = build_model(input_shape=input_shape)
                training_result = train_model(model, bundle)
        else:
            model = build_model(input_shape=input_shape)
            print(format_model_summary(model))
            print()
            training_result = train_model(model, bundle)
            print(format_training_summary(training_result))
            print()
    else:
        print("Phase 3 skipped: preprocessing bundle is missing training tensors.")
        print()

    # ==========================================================================
    # PHASE 4: EVALUATION & VISUALIZATION
    # ==========================================================================
    print("=" * 70)
    print("PHASE 4: Evaluation & Visualization")
    print("=" * 70 + "\n")

    evaluation_result = {"metrics_path": "not-run"}
    prediction_plot_path = "not-run"
    prediction_bands_plot_path = "not-run"
    residual_plot_path = "not-run"
    candlestick_plot_path = "not-run"
    correlation_heatmap_path = "not-run"
    if "model" in training_result and "X_test" in bundle:
        evaluation_result = evaluate_model(training_result, bundle)
        print(format_evaluation_summary(evaluation_result))
        print()

        reload_saved_model_smoke_test(bundle, training_result)
        prediction_plot_path = plot_predictions(
            evaluation_result["actual_usd"],
            evaluation_result["predictions_usd"],
            rmse=evaluation_result["metrics"]["rmse"],
            mape=evaluation_result["metrics"]["mape"],
        )
        prediction_bands_plot_path = plot_predictions_with_confidence_bands(
            evaluation_result["actual_usd"],
            evaluation_result["predictions_usd"],
            rmse=evaluation_result["metrics"]["rmse"],
            mape=evaluation_result["metrics"]["mape"],
        )
        residual_plot_path = plot_residuals(
            evaluation_result["actual_usd"],
            evaluation_result["predictions_usd"],
        )
        candlestick_plot_path = plot_candlestick_chart(df)
        correlation_heatmap_path = plot_feature_correlation_heatmap(df)
        print()
    else:
        print("Phase 4 skipped: training result is missing model or test tensors.")
        print()

    # ==========================================================================
    # PHASE 4 COMPLETE
    # ==========================================================================
    print("=" * 70)
    print("PHASE 4 COMPLETE")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  - Plot: {plot_path}")
    print(f"  - Rows: {len(df)}")
    print(
        f"  - Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"
    )
    print(f"  - Missing values: {missing_count}")
    print(f"  - X_train shape: {bundle['metadata']['X_train_shape']}")
    print(f"  - X_test shape: {bundle['metadata']['X_test_shape']}")
    print(f"  - Model: {training_result['checkpoint_path']}")
    print(f"  - Training sidecar: {training_result['sidecar_path']}")
    print(f"  - Metrics artifact: {evaluation_result['metrics_path']}")
    print(f"  - Prediction plot: {prediction_plot_path}")
    print(f"  - Prediction bands plot: {prediction_bands_plot_path}")
    print(f"  - Residual plot: {residual_plot_path}")
    print(f"  - Candlestick plot: {candlestick_plot_path}")
    print(f"  - Correlation heatmap: {correlation_heatmap_path}")
    print()

    print("Pipeline complete.")
    print()


if __name__ == "__main__":
    main()

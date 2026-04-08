"""Stock Price Prediction Pipeline - Main Entry Point."""

import os
import sys

from src.config import AUTONOMOUS_FAILURE_ENV, DATA_PATH, REPAIR_LOG_FILE
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
from src.autonomous_verifier import (
    build_autonomous_verification_report,
    diagnose_verification_failure,
    format_autonomous_verification_summary,
)
from src.repair_loop import (
    format_repair_outcome,
    run_autonomous_repair_loop,
    run_pipeline_subprocess,
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


def _build_phase5_initial_run_result(
    training_result, evaluation_result, prediction_plot_path, phase4_ran
):
    if phase4_ran:
        return {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "duration_seconds": 0.0,
            "metrics_path": evaluation_result["metrics_path"],
            "checkpoint_path": training_result["checkpoint_path"],
            "prediction_plot_path": prediction_plot_path,
            "failure_injection": os.getenv(AUTONOMOUS_FAILURE_ENV, ""),
        }

    return {
        "exit_code": 1,
        "stdout": "phase4_skipped",
        "stderr": "phase4_skipped",
        "duration_seconds": 0.0,
        "metrics_path": evaluation_result["metrics_path"],
        "checkpoint_path": training_result["checkpoint_path"],
        "prediction_plot_path": prediction_plot_path,
        "failure_injection": os.getenv(AUTONOMOUS_FAILURE_ENV, ""),
    }


def _rerun_pipeline_without_phase5():
    child_env = {**os.environ, "LSTM_SKIP_PHASE5": "1"}
    return run_pipeline_subprocess([sys.executable, "main.py"], env=child_env)


def _verify_phase5_run(run_result):
    return build_autonomous_verification_report(run_result)


def _apply_autonomous_repair(diagnosis, report, attempt_number):
    return {
        "name": f"attempt-{attempt_number}-{diagnosis['category']}",
        "rationale": diagnosis["hints"][0]
        if diagnosis.get("hints")
        else "Retry verification.",
        "changed_files": [],
    }


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

    if os.getenv("LSTM_SKIP_PHASE5") == "1":
        return

    # ==========================================================================
    # PHASE 5: AUTONOMOUS CORRECTION & PERFORMANCE OPTIMIZATION LOOP
    # ==========================================================================
    print("=" * 70)
    print("PHASE 5: Autonomous Correction & Performance Optimization Loop")
    print("=" * 70 + "\n")

    phase4_ran = "model" in training_result and "X_test" in bundle
    initial_run_result = _build_phase5_initial_run_result(
        training_result,
        evaluation_result,
        prediction_plot_path,
        phase4_ran,
    )
    initial_report = build_autonomous_verification_report(initial_run_result)
    print(format_autonomous_verification_summary(initial_report))
    print()

    repair_result = run_autonomous_repair_loop(
        initial_report=initial_report,
        rerun_pipeline=_rerun_pipeline_without_phase5,
        verify_run=_verify_phase5_run,
        diagnose_failure=diagnose_verification_failure,
        apply_repair=_apply_autonomous_repair,
    )
    print(f"Autonomous status: {repair_result['status']}")
    print(f"Repair log: {REPAIR_LOG_FILE}")
    print(format_repair_outcome(repair_result))
    print()


if __name__ == "__main__":
    main()

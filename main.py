"""
Stock Price Prediction Pipeline - Main Entry Point

Orchestrates the full ML pipeline from data loading through
model training, evaluation, and visualization.

Usage:
    python main.py

Phases:
    Phase 1: Load data, validate, and visualize raw prices
    Phase 2: Preprocess and generate LSTM input sequences
    Phase 3: Build and train LSTM model
    Phase 4: Evaluate and visualize predictions
"""

from src.config import DATA_PATH
from src.utils import setup_environment
from src.data_loader import load_data, display_statistics, check_missing_values
from src.visualizer import plot_price_history
from src.preprocessor import preprocess, format_preprocessing_proof
from src.model import build_model, format_model_summary
from src.trainer import train_model, format_training_summary


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

    model = build_model(input_shape=bundle["X_train"].shape[1:])
    print(format_model_summary(model))
    print()

    training_result = train_model(model, bundle)
    print(format_training_summary(training_result))
    print()

    # ==========================================================================
    # PHASE 3 COMPLETE
    # ==========================================================================
    print("=" * 70)
    print("✓ PHASE 3 COMPLETE")
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
    print()


if __name__ == "__main__":
    main()

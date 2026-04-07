"""Main entry point for the stock price prediction pipeline."""

from src.config import DATA_PATH
from src.data_loader import check_missing_values, display_statistics, load_data
from src.preprocessor import format_preprocessing_proof, preprocess
from src.utils import setup_environment
from src.visualizer import plot_price_history


def main():
    print("\n" + "=" * 70)
    print("STOCK PRICE PREDICTION PIPELINE")
    print("=" * 70 + "\n")

    print("Setting up environment...")
    setup_environment()
    print()

    print("=" * 70)
    print("PHASE 1: Data Loading & Validation")
    print("=" * 70 + "\n")

    df = load_data(DATA_PATH)
    display_statistics(df)
    missing_count = check_missing_values(df)
    plot_path = plot_price_history(df)
    print()

    print("=" * 70)
    print("PHASE 2: Preprocessing & Sequence Generation")
    print("=" * 70 + "\n")

    bundle = preprocess(df)
    proof = format_preprocessing_proof(bundle)
    print(proof)
    print()

    print("=" * 70)
    print("✓ PHASE 1 COMPLETE")
    print("✓ PHASE 2 COMPLETE")
    print("=" * 70)
    print(f"Plot: {plot_path}")
    print(f"Rows: {len(df)}")
    print(f"Missing values: {missing_count}")
    print(f"X_train shape: {bundle['metadata']['X_train_shape']}")
    print(f"X_test shape: {bundle['metadata']['X_test_shape']}")


if __name__ == "__main__":
    main()

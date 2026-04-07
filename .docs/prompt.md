You are an expert ML engineer. Help me build a Stock Price Prediction 
project using LSTM Neural Networks step by step.

=== PROJECT CONTEXT ===
- Goal: Predict AAPL stock closing prices using a static Kaggle CSV dataset
- Dataset: "15Y Big Tech Stock Data" from Kaggle (local CSV file: data/AAPL.csv)
  Columns available: Date, Open, High, Low, Close, Adj Close, Volume
- Model: Stacked LSTM (2 layers) using TensorFlow 2.x / Keras
- Input feature: Close price ONLY (univariate — keep it simple)
- Prediction target: Next-day closing price (single-step)
- Plan - PRD, SRS,TDD are already created inside .docs folder

=== TECH STACK ===
- Python 3.10+
- pandas, numpy, scikit-learn
- tensorflow / keras
- matplotlib
- No live API calls — fully offline pipeline

=== PROJECT STRUCTURE TO FOLLOW ===
stock-lstm-predictor/
├── data/
│   └── AAPL.csv               ← Kaggle dataset (already downloaded)
├── output/                    ← auto-created by code
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── preprocessor.py
│   ├── model.py
│   ├── trainer.py
│   ├── evaluator.py
│   └── visualizer.py
├── main.py
├── notebook.ipynb
└── requirements.txt

=== ALGORITHMS & SPECS ===
1. MinMaxScaler → normalize Close to [0,1] (fit on train only, no leakage)
2. Sliding Window size = 60 (60 days → predict day 61)
3. Train/Test split = 80/20, NO shuffling (preserve temporal order)
4. LSTM Architecture:
   - LSTM(64 units, return_sequences=True, input_shape=(60,1))
   - Dropout(0.2)
   - LSTM(64 units, return_sequences=False)
   - Dropout(0.2)
   - Dense(32, activation='relu')
   - Dense(1)
5. Optimizer: Adam(lr=0.001)
6. Loss: mean_squared_error
7. Callbacks: EarlyStopping(patience=10), ModelCheckpoint(save_best_only=True)
8. Metrics: RMSE and MAPE on inverse-transformed predictions

=== IMPLEMENTATION RULES ===
- All hyperparameters must be in config.py as a single CONFIG dict
- Set random seeds: numpy seed=42, tf.random.set_seed(42)
- Scaler must be fit ONLY on training data — never on full dataset
- Test sequences must include last 60 rows of train for continuity
- Save trained model to output/best_model.h5
- Save prediction plot to output/AAPL_prediction.png

=== OUTPUT EXPECTED ===
- Console: training loss per epoch + final RMSE and MAPE values
- File: output/AAPL_prediction.png (Actual vs Predicted line plot)
- File: output/best_model.h5 (saved model)
- MAPE target: below 5%

=== BUILD ORDER ===
Build one file at a time in this order:
1. requirements.txt
2. src/config.py
3. src/data_loader.py  → test with: df = load_csv(CONFIG); print(df.head())
4. src/preprocessor.py → test with: shapes of X_train, X_test
5. src/model.py        → test with: model.summary()
6. src/trainer.py      → test with: training loss printed per epoch
7. src/evaluator.py    → test with: RMSE and MAPE printed
8. src/visualizer.py   → test with: plot saved to output/
9. main.py             → ties all modules together

Build end to end Ml project 
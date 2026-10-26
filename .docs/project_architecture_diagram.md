
```mermaid
flowchart TD
    A([📁 INPUT — Kaggle CSV AAPL.csv])

    A --> B

    subgraph PRE [🔧 PREPROCESSING]
        B[Load & Filter CSV]
        B --> C[MinMaxScaler — Normalize Close to 0-1]
        C --> D[Sliding Window — 60-day sequences]
        D --> E[Train Set — 80 percent]
        D --> F[Test Set — 20 percent]
    end

    subgraph MODEL [🧠 LSTM MODEL]
        G[LSTM Layer 1 — 64 units]
        G --> H[Dropout 0.2]
        H --> I[LSTM Layer 2 — 64 units]
        I --> J[Dropout 0.2]
        J --> K[Dense 32 — ReLU]
        K --> L[Dense 1 — Output]
    end

    subgraph TRAIN [⚙️ TRAINING]
        M[Adam Optimizer + MSE Loss]
        M --> N[EarlyStopping — patience 10]
        N --> O[(best_model.h5 — Saved Weights)]
    end

    subgraph OUT [📊 OUTPUT]
        P[Inverse Transform — USD Prices]
        P --> Q[Metrics — RMSE and MAPE]
        P --> R[Actual vs Predicted Plot PNG]
    end

    E --> G
    F --> P
    L --> M
    O --> P
```

## Block Descriptions

| Block | Components | Purpose |
|---|---|---|
| 🔧 Preprocessing | CSV Load, MinMaxScaler, Sliding Window, Split | Prepare raw data into LSTM-ready sequences |
| 🧠 LSTM Model | LSTM×2, Dropout×2, Dense(32), Dense(1) | Learn temporal price patterns |
| ⚙️ Training | Adam, MSE Loss, EarlyStopping, ModelCheckpoint | Optimize and save best weights |
| 📊 Output | Inverse Transform, RMSE, MAPE, Plot | Evaluate and visualize predictions |
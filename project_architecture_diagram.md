# Project Architecture Diagram

This document contains the high-level block diagram for the **Stock Price Prediction using LSTM Neural Networks** project. 

## High-Level Pipeline

```mermaid
graph TD
    %% Core Pipeline
    RawData[(Kaggle Dataset:\nAAPL.csv)] -->|Data Ingestion| DataLoader[src/data_loader.py]
    DataLoader -->|Raw Data| Preprocessor[src/preprocessor.py]
    Preprocessor -->|Scaled Sequences| Model[src/model.py]
    Model -->|Compiled LSTM| Trainer[src/trainer.py]
    Trainer -->|Predictions & Metrics| Visualizer[src/visualizer.py]

    %% Configuration and Orchestration
    Config[src/config.py\n(Hyperparameters)] -.->|Configures| DataLoader
    Config -.->|Configures| Preprocessor
    Config -.->|Configures| Model
    Config -.->|Configures| Trainer
    
    Utils[src/utils.py\n(Metrics/Helpers)] -.-> Trainer
    Utils -.-> Visualizer

    %% Main Orchestrator
    Main[main.py\n(Orchestrator)] === DataLoader
    Main === Preprocessor
    Main === Model
    Main === Trainer
    Main === Visualizer

    %% Verification & Autonomy (Phase 5)
    Verifier[tests/test_autonomous_verifier.py] -.->|Verification| Main
    Repair[tests/test_repair_loop.py] -.->|Repair Loop| Main

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef data fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef ml fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px;
    classDef ui fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef util fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef auto fill:#ffe0b2,stroke:#f57c00,stroke-width:2px;

    class RawData,DataLoader,Preprocessor data;
    class Model,Trainer ml;
    class Visualizer ui;
    class Config,Utils,Main util;
    class Verifier,Repair auto;
```

## Module Definitions
- **`src/config.py`**: Centralized configuration containing file paths, hyperparameters (window size, units, learning rate, etc.).
- **`src/data_loader.py`**: Handles loading and initial cleaning of the Kaggle CSV dataset.
- **`src/preprocessor.py`**: Transforms raw financial data into normalized training sequences fit for the LSTM (e.g. 60 timestep blocks).
- **`src/model.py`**: Constructs the stacked LSTM architecture using TensorFlow/Keras.
- **`src/trainer.py`**: Manages the training loop, learning callbacks, and execution.
- **`src/visualizer.py`**: Generates plots comparing predicted vs. actual stock prices and tracks diagnostics.
- **`src/utils.py`**: Houses reproducible seeds, metric calculations (e.g., MAPE, RMSE).
- **`main.py`**: Orchestrates the top-down workflow across core phases.
- **`tests/test_autonomous_verifier.py` & `tests/test_repair_loop.py`**: Perform automatic issue detection and automated code repair (Phase 5).

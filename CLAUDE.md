<!-- GSD:project-start source:PROJECT.md -->
## Project

**Stock Price Prediction using LSTM Neural Networks**

A machine learning application that predicts future stock closing prices using a Long Short-Term Memory (LSTM) neural network trained on a **static Kaggle CSV dataset**. The system preprocesses historical stock data, trains a stacked LSTM model, and outputs predicted vs. actual price visualizations alongside evaluation metrics — all without requiring live internet connectivity.

**Core Value:** **Accurate next-day closing price prediction with MAPE < 5% using a simple, offline LSTM pipeline.**

The ONE thing that must work: Given a CSV file of historical AAPL stock data, the system trains an LSTM model and produces predictions that are within 5% of actual prices, demonstrating the model can learn meaningful temporal patterns from price history.

### Constraints

### Technical
- **Dataset**: Kaggle "15Y Big Tech Stock Data" — AAPL.csv already downloaded
- **Date range**: 2018-01-01 to 2025-01-01 (~1,762 trading days)
- **Tech stack**: Python 3.10+, TensorFlow 2.x, pandas, scikit-learn, matplotlib
- **Hardware**: Must train in < 10 minutes on CPU (no GPU required)
- **No live data**: Zero API calls — fully offline pipeline

### Scope
- **In scope**: Load CSV → Preprocess → Train LSTM → Evaluate → Visualize
- **Out of scope**: Live data fetching, intraday prediction, multi-stock comparison, trading integration

### Success Metrics
| Metric              | Target                     |
|---------------------|----------------------------|
| MAPE on test set    | < 5%                       |
| RMSE on test set    | < $5 (for AAPL-scale data) |
| Training time       | < 5 minutes on CPU         |
| Visualization       | Clear actual vs. predicted plot |
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

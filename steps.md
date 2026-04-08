To run the standard pipeline:

.\venv\Scripts\python.exe main.py

To run the repair loop (only when you want to optimize):

.\venv\Scripts\python.exe -m src.repair_model


To reuse your existing model and skip training in main.py:

$env:LSTM_REUSE_MODEL="1"; .\venv\Scripts\python.exe main.py

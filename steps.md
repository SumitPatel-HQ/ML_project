# How to Run

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Standard Pipeline
Trains the model and generates evaluation metrics and plots:
```powershell
.\venv\Scripts\python.exe main.py
```

### 3. Reuse Saved Model (Skip Training)
Skips retraining and evaluates using the existing model:
```powershell
$env:LSTM_REUSE_MODEL="1"; .\venv\Scripts\python.exe main.py
```

### 4. Run Optimization / Repair Loop (Optional)
Automatically tunes hyperparameters to optimize performance:
```powershell
.\venv\Scripts\python.exe -m src.repair_model
```

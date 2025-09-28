import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
import os
from src.components.dtde_preprocessor import DTDEPreprocessor # <--- IMPORT

# --- Configuration ---
DATA_FILE = os.path.join(os.path.dirname(__file__), '../../data/kms_access_logs.json')
MODEL_FILE = os.path.join(os.path.dirname(__file__), '../../models/dtde_model.joblib')

def train_dtde_model():
    print("--- DTDE Model Training Started (Refactored) ---")
    
    # 1. Load Data
    df = pd.read_json(DATA_FILE)

    # 2. Use the Preprocessor to fit and transform the data
    print("Step 2: Fitting preprocessor and transforming data...")
    preprocessor = DTDEPreprocessor()
    preprocessor.fit(df)
    features = preprocessor.transform(df)

    # 3. Train the AI Model
    print("Step 3: Training the Isolation Forest model...")
    model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
        model.learn(total_timesteps=50000, progress_bar=True)

    # 4. Save the Model AND the FITTED Preprocessor
    print(f"Step 4: Saving the model and preprocessor to '{MODEL_FILE}'...")
    joblib.dump({'model': model, 'preprocessor': preprocessor}, MODEL_FILE)

    print("\n--- DTDE Model Training Complete! ---")

if __name__ == "__main__":
    train_dtde_model()
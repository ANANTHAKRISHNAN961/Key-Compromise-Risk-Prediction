from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime, timezone # <--- MAKE SURE timezone IS IMPORTED
import json

# Initialize the FastAPI app
app = FastAPI(title="SRAE - Static Risk Assessment Engine API")

# --- CORS MIDDLEWARE SETUP ---
# This allows your React frontend to communicate with your API
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------

# --- Load the trained model once when the API starts ---
try:
    # IMPORTANT: Update this path to be correct relative to where you run uvicorn
    # If you run uvicorn from the root folder, this path is correct:
    model = joblib.load('models/srae_model.joblib')
    print("Model loaded successfully!")
except FileNotFoundError:
    model = None
    print("Error: Model file 'models/srae_model.joblib' not found.")


# --- Define the input data structure for prediction ---
class KeyConfiguration(BaseModel):
    key_id: str # Add all fields from the CSV to match the data being sent
    creation_date: str
    algorithm: str
    is_hsm_backed: bool
    rotation_enabled: bool
    permission_policy: str

# --- (CORRECTED) Feature Engineering Function ---
def prepare_input(key_data: KeyConfiguration):
    df_new = pd.DataFrame([key_data.dict()])
    
    # Pandas automatically makes the column tz-aware if the string has a 'Z'
    df_new['creation_date'] = pd.to_datetime(df_new['creation_date']) 
    
    # --- FIX: Use a timezone-aware 'now' for correct comparison ---
    now_utc = datetime.now(timezone.utc)
    df_new['key_age_days'] = (now_utc - df_new['creation_date']).dt.days
    # --- END FIX ---

    df_new['is_hsm_backed'] = df_new['is_hsm_backed'].astype(int)
    df_new['rotation_enabled'] = df_new['rotation_enabled'].astype(int)
    df_new['has_wildcard'] = df_new['permission_policy'].apply(lambda x: 1 if '"*"' in x else 0)
    
    df = pd.get_dummies(df_new, columns=['algorithm'], prefix='algo', dtype=int)
    
    all_feature_cols = [
        'key_age_days', 'is_hsm_backed', 'rotation_enabled', 'has_wildcard',
        'algo_AES_256', 'algo_RSA_4096', 'algo_RSA_2048', 'algo_3DES'
    ]
    for col in all_feature_cols:
        if col not in df.columns:
            df[col] = 0
            
    return df[all_feature_cols]

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "SRAE API is running."}

@app.get("/keys/inventory")
def get_key_inventory():
    try:
        # IMPORTANT: Update this path
        df = pd.read_csv('data/new_keys_to_predict.csv')
        keys = df.to_dict(orient='records')
        return {"keys": keys}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Key inventory file not found.")

@app.post("/predict_vulnerability")
def predict_score(key_config: KeyConfiguration):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    
    try:
        prepared_data = prepare_input(key_config)
        score = model.predict(prepared_data)
        return {"key_algorithm": key_config.algorithm, "predicted_vulnerability_score": round(score[0])}
    except Exception as e:
        # This will help debug future errors by showing them in the server logs
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Error during prediction.")
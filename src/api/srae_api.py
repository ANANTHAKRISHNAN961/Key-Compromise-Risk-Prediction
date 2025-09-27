from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
import joblib
import pandas as pd
from datetime import datetime
import json

# Initialize the FastAPI app
app = FastAPI(title="SRAE - Static Risk Assessment Engine API")
# --- CORS MIDDLEWARE SETUP ---
# This allows your React frontend to communicate with your API
origins = [
    "http://localhost:5173", # The default port for Vite React apps
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
    model = joblib.load('../../models/srae_model.joblib')
    print("Model loaded successfully!")
except FileNotFoundError:
    model = None
    print("Error: Model file 'srae_model.joblib' not found.")

# --- Define the input data structure for prediction ---
class KeyConfiguration(BaseModel):
    creation_date: str
    algorithm: str
    is_hsm_backed: bool
    rotation_enabled: bool
    permission_policy: str

# --- Feature Engineering Function ---
def prepare_input(key_data: KeyConfiguration):
    df_new = pd.DataFrame([key_data.dict()])
    df_new['creation_date'] = pd.to_datetime(df_new['creation_date'])
    df_new['key_age_days'] = (datetime.now() - df_new['creation_date']).dt.days
    df_new['is_hsm_backed'] = df_new['is_hsm_backed'].astype(int)
    df_new['rotation_enabled'] = df_new['rotation_enabled'].astype(int)
    df_new['has_wildcard'] = df_new['permission_policy'].apply(lambda x: 1 if '"*"' in x else 0)
    all_algo_cols = ['algo_AES_256', 'algo_RSA_4096', 'algo_RSA_2048', 'algo_3DES']
    for col in all_algo_cols:
        df_new[col] = 1 if f"algo_{df_new['algorithm'][0]}" == col else 0
    features_order = [
        'key_age_days', 'is_hsm_backed', 'rotation_enabled', 'has_wildcard',
        'algo_AES_256', 'algo_RSA_4096', 'algo_RSA_2048', 'algo_3DES'
    ]
    return df_new[features_order]

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "SRAE API is running."}

# ***************************************************************
# *** NEW ENDPOINT TO SEND KEY DATA TO THE FRONTEND ***
# ***************************************************************
@app.get("/keys/inventory")
def get_key_inventory():
    """
    Reads the key data from the local CSV file and returns it as JSON.
    This endpoint provides the initial data for the frontend dashboard.
    """
    try:
        df = pd.read_csv('../../data/new_keys_to_predict.csv')
        # Convert the DataFrame to a list of dictionaries (which becomes a JSON array)
        keys = df.to_dict(orient='records')
        return {"keys": keys}
    except FileNotFoundError:
        # Return a proper HTTP 404 error if the file doesn't exist
        raise HTTPException(status_code=404, detail="Key inventory file ('new_keys_to_predict.csv') not found.")
    except Exception as e:
        # Catch other potential errors
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_vulnerability")
def predict_score(key_config: KeyConfiguration):
    """
    Receives a single key's configuration and returns its predicted score.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    prepared_data = prepare_input(key_config)
    score = model.predict(prepared_data)
    return {"key_algorithm": key_config.algorithm, "predicted_vulnerability_score": round(score[0])}
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import json
import math
from src.components.dtde_preprocessor import DTDEPreprocessor
from stable_baselines3 import PPO
from src.components.kms_env import KmsEnv
from typing import Optional

# --- App Setup ---
app = FastAPI(title="Project Chimera API")

# --- Global Variables for Models and Data ---
srae_model = None
dtde_model = None
dtde_preprocessor = None
apce_model = None
key_inventory_df = None
access_logs_df = None

# --- App Startup Event ---
@app.on_event("startup")
def load_resources():
    """Load all models and data into memory when the server starts."""
    global srae_model, dtde_model, dtde_preprocessor, apce_model, key_inventory_df, access_logs_df
    
    # Load SRAE model
    try:
        srae_model = joblib.load('models/srae_model.joblib')
        print("SRAE model loaded successfully!")
    except FileNotFoundError:
        print("Warning: SRAE model not found.")

    # Load DTDE model and preprocessor
    try:
        dtde_data = joblib.load('models/dtde_model.joblib')
        dtde_model = dtde_data['model']
        dtde_preprocessor = dtde_data['preprocessor']
        print("DTDE model and preprocessor loaded successfully!")
    except FileNotFoundError:
        print("Warning: DTDE model not found.")

    # Load APCE model
    try:
        apce_model = PPO.load('models/apce_model.zip')
        print("APCE model loaded successfully!")
    except FileNotFoundError:
        print("Warning: APCE model not found.")

    # Load datasets into memory
    try:
        key_inventory_df = pd.read_csv('data/new_keys_to_predict.csv')
        print(f"Loaded {len(key_inventory_df)} keys into memory.")
    except FileNotFoundError:
        print("Warning: Key inventory CSV not found.")
        
    try:
        access_logs_df = pd.read_json('data/kms_access_logs.json')
        print(f"Loaded {len(access_logs_df)} logs into memory.")
    except FileNotFoundError:
        print("Warning: Access logs JSON not found.")

# --- CORS Middleware ---
origins = ["http://localhost:5173", "http://localhost:5174"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class KeyConfiguration(BaseModel):
    key_id: str
    creation_date: str
    algorithm: str
    is_hsm_backed: bool
    rotation_enabled: bool
    permission_policy: str

class LogEntry(BaseModel):
    log_id: str
    timestamp: str
    key_id: str
    user_id: str
    source_ip: str
    action: str
    user_agent: str
    status: str

class RiskInput(BaseModel):
    vulnerability_score: Optional[float] = None
    anomaly_score: Optional[float] = None

# --- SRAE Feature Engineering (as provided) ---
def prepare_srae_input(key_config: KeyConfiguration):
    df_new = pd.DataFrame([key_config.dict()])
    df_new['creation_date'] = pd.to_datetime(df_new['creation_date'])
    now_utc = datetime.now(timezone.utc)
    df_new['key_age_days'] = (now_utc - df_new['creation_date']).dt.days
    df_new['is_hsm_backed'] = df_new['is_hsm_backed'].astype(int)
    df_new['rotation_enabled'] = df_new['rotation_enabled'].astype(int)
    df_new['has_wildcard'] = df_new['permission_policy'].apply(lambda x: 1 if '"*"' in x else 0)
    df = pd.get_dummies(df_new, columns=['algorithm'], prefix='algo', dtype=int)
    
    all_feature_cols = [
        'key_age_days', 'is_hsm_backed', 'rotation_enabled', 'has_wildcard', 
        'algo_AES_256', 'algo_RSA_4096', 'algo_RSA_2048', 'algo_3DES'
    ]
    # Reindex to ensure all columns are present, matching training
    final_df = df.reindex(columns=all_feature_cols, fill_value=0)
            
    return final_df[all_feature_cols]

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Project Chimera API is running."}

# SRAE Endpoints
@app.get("/keys/inventory")
def get_key_inventory():
    if key_inventory_df is None:
        raise HTTPException(status_code=404, detail="Key inventory data not loaded.")
    return {"keys": key_inventory_df.to_dict(orient='records')}

@app.post("/predict_vulnerability")
def predict_vulnerability(key_config: KeyConfiguration):
    if srae_model is None:
        raise HTTPException(status_code=503, detail="SRAE model not loaded.")
    prepared_data = prepare_srae_input(key_config)
    score = srae_model.predict(prepared_data)
    return {"predicted_vulnerability_score": round(score[0])}

# DTDE Endpoint
@app.get("/logs/scored")
def get_scored_logs(page: int = 1, limit: int = 50):
    if dtde_model is None or dtde_preprocessor is None or access_logs_df is None:
        raise HTTPException(status_code=503, detail="DTDE resources or log data not loaded.")

    total_logs = len(access_logs_df)
    total_pages = math.ceil(total_logs / limit)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    df_page = access_logs_df.iloc[start_index:end_index]
    if df_page.empty:
        return {"logs": [], "total_pages": total_pages, "current_page": page}

    prepared_data = dtde_preprocessor.transform(df_page)
    raw_scores = dtde_model.score_samples(prepared_data)
    
    # A more balanced normalization: scale scores to a 0-100 range
    # We'll establish a baseline and scale based on deviation from the mean
    mean_score = raw_scores.mean()
    std_dev = raw_scores.std()
    
    # Normalize using a Z-score-like approach, then scale to 0-100
    # This centers the "average" log around a score of 20-30
    if std_dev > 0:
        normalized_scores = 50 + (raw_scores - mean_score) / std_dev * 25
    else:
        normalized_scores = pd.Series([50] * len(raw_scores)) # Handle case with no deviation
        
    final_scores = pd.Series(normalized_scores).clip(0, 100).round().astype(int)
    
    df_page = df_page.assign(anomaly_score=final_scores.values)
    
    return {"logs": df_page.to_dict(orient='records'), "total_pages": total_pages, "current_page": page}

# APCE Endpoint
@app.post("/get_action")
async def get_action(risk_input: RiskInput):
    """
    Determines the recommended security action based on a composite risk score.
    The composite score is derived from an optional vulnerability score and an
    optional anomaly score.
    """
    if apce_model is None:
        raise HTTPException(status_code=503, detail="APCE model not loaded.")

    # Normalize scores to a 0.0-1.0 scale, as expected by the training environment
    vuln_norm = (risk_input.vulnerability_score / 10.0) if risk_input.vulnerability_score is not None else 0.0
    anom_norm = (risk_input.anomaly_score / 100.0) if risk_input.anomaly_score is not None else 0.0

    # If one score is present, use it directly. If both, use a weighted average.
    if vuln_norm > 0 and anom_norm == 0:
        composite_risk = vuln_norm
    elif anom_norm > 0 and vuln_norm == 0:
        composite_risk = anom_norm
    else:
        # Combine scores: vulnerability is static (weight 0.4), anomaly is dynamic (weight 0.6)
        composite_risk = (vuln_norm * 0.4) + (anom_norm * 0.6)
    
    # The observation must be a numpy array, clipped to ensure it's within [0, 1]
    obs = np.array([composite_risk], dtype=np.float32).clip(0, 1)

    action, _ = apce_model.predict(obs, deterministic=True)
    
    action_map = {
        0: "NO_OP",
        1: "ALERT_SOC",
        2: "FORCE_ROTATE_KEY",
        3: "RESTRICT_PERMISSIONS",
        4: "QUARANTINE_KEY"
    }
    
    return {"recommended_action": action_map.get(int(action), "UNKNOWN")}
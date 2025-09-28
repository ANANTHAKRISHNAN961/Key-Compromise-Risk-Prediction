import pandas as pd
import joblib
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Pydantic Model for Input Validation ---
# This defines the expected structure of a single log entry for incoming requests.
# The 'example' values will show up in the automatic API documentation.
class LogEntry(BaseModel):
    eventTime: str = Field(..., example="2025-09-28T11:00:00Z")
    sourceIPAddress: str = Field(..., example="198.143.44.113")
    userIdentity_arn: str = Field(..., example="arn:aws:iam::12345:assumed-role/SecurityAuditorRole")
    eventName: str = Field(..., example="Encrypt")
    key_arn: str = Field(..., example="key-00006")
    errorCode: Optional[str] = Field(None, example="AccessDeniedException")

# --- Initialize the FastAPI App ---
app = FastAPI(title="DTDE - Dynamic Threat Detection Engine API")

# --- CORS MIDDLEWARE SETUP ---
# This allows your frontend (e.g., running on http://localhost:5173) to communicate with this API.
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Model and Columns on Application Startup ---
# This is efficient as it happens only once.
try:
    model = joblib.load('../../models/srae_dtde_model.joblib')
    with open('../../models/srae_dtde_model_columns.json', 'r') as f:
        model_columns = json.load(f)
    print("DTDE Model and columns loaded successfully.")
except FileNotFoundError:
    model = None
    model_columns = None
    print("CRITICAL ERROR: DTDE model or columns file not found. Please train the model first.")

# --- Feature Engineering Function ---
# This function must be identical to the one used during training to ensure consistency.
def engineer_features(df):
    """Processes raw log data into features the model can understand."""
    df['eventTime'] = pd.to_datetime(df['eventTime'])
    df['time_of_day'] = df['eventTime'].dt.hour
    df = df.sort_values(by='eventTime')
    
    # Set eventTime as the index for the time-based rolling calculation
    df = df.set_index('eventTime')
    
    # Calculate frequency using a 1-hour rolling window
    df['api_call_frequency'] = df.groupby('userIdentity_arn')['key_arn'].transform(lambda x: x.rolling('1h').count())
    
    # Reset the index to make eventTime a regular column again
    df = df.reset_index()
    
    # Fill any missing error codes with 'Success'
    df['errorCode'] = df['errorCode'].fillna('Success')
    
    # Convert categorical features into a numerical format (one-hot encoding)
    features_to_encode = ['sourceIPAddress', 'userIdentity_arn', 'eventName', 'key_arn', 'errorCode']
    engineered_df = pd.get_dummies(df, columns=features_to_encode)
    return engineered_df

# --- API Endpoints ---
@app.get("/")
def read_root():
    """Root endpoint to check if the API is running."""
    return {"message": "DTDE API is running."}

@app.post("/predict_anomaly")
def predict(log_entries: List[LogEntry]):
    """
    Receives a list of log entries, processes them, and returns predictions.
    """
    if model is None or model_columns is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model before running the API.")
    
    # Convert the incoming list of Pydantic models to a pandas DataFrame
    df = pd.DataFrame([entry.dict() for entry in log_entries])
    
    # Process the new data using the same feature engineering logic
    prepared_data = engineer_features(df.copy())
    
    # Align the columns of the new data to match the training data perfectly
    aligned_data = prepared_data.reindex(columns=model_columns, fill_value=0)
    
    # Make a prediction using the trained model
    raw_scores = model.decision_function(aligned_data)
    
    # Scale the scores to your desired 1-100 range
    anomaly_scores_0_1 = 1 - (raw_scores - (-0.5)) / (0.5 - (-0.5))
    scaled_scores = (anomaly_scores_0_1.clip(0, 1) * 99) + 1
    df['PredictedAnomalyScore'] = scaled_scores.astype(int)

    # Return the original data along with the new prediction
    # FastAPI automatically converts this to a JSON response
    return df.to_dict(orient='records')


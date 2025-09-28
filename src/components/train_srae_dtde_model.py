# train_srae_dtde_model.py (Score scaled 1-100)
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import json
import os

def train_model(df):
    print("\nPreparing data for the model...")
    df['errorCode'].fillna('Success', inplace=True)
    
    features_to_encode = ['sourceIPAddress', 'userIdentity_arn', 'eventName', 'key_arn', 'errorCode']
    featured_df = pd.get_dummies(df, columns=features_to_encode)

    model_features = featured_df.select_dtypes(include=['number', 'uint8'])
    
    model_columns = model_features.columns.tolist()
    os.makedirs('../../models', exist_ok=True)
    
    with open('../../models/srae_dtde_model_columns.json', 'w') as f:
        json.dump(model_columns, f)
    print("Model columns saved to 'models/srae_dtde_model_columns.json'")
    
    print("Training the Isolation Forest model...")
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(model_features)
    
    joblib.dump(model, '../../models/srae_dtde_model.joblib')
    print("Model trained and saved to 'models/srae_dtde_model.joblib'")
    
    raw_scores = model.decision_function(model_features)
    # --- FIX: Scale score to 1-100 range ---
    anomaly_scores_0_1 = 1 - ((raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min()))
    scaled_scores = (anomaly_scores_0_1 * 99) + 1
    df['AnomalyScore'] = scaled_scores.astype(int) # Convert to integer
    # --- END FIX ---
    
    return df

if __name__ == '__main__':
    DATA_FILE_PATH = '../../data/srae_aware_dtde_logs.csv'
    try:
        raw_df = pd.read_csv(DATA_FILE_PATH)
        print("Adding engineered feature columns...")
        raw_df['eventTime'] = pd.to_datetime(raw_df['eventTime'])
        raw_df['time_of_day'] = raw_df['eventTime'].dt.hour
        raw_df = raw_df.sort_values(by='eventTime')
        raw_df = raw_df.set_index('eventTime')
        raw_df['api_call_frequency'] = raw_df.groupby('userIdentity_arn')['key_arn'].transform(lambda x: x.rolling('1h').count())
        raw_df = raw_df.reset_index()
        
        results_df = train_model(raw_df.copy())
        print("\n--- Top 15 Anomalies Found in Training Data ---")
        print(results_df.sort_values(by='AnomalyScore', ascending=False).head(15))
    except FileNotFoundError:
        print(f"Error: Could not find '{DATA_FILE_PATH}'. Please run the generator script first.")
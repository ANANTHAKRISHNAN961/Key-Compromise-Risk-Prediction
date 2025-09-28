# predict_srae_anomalies.py (Score scaled 1-100)
import pandas as pd
import joblib
import json

MODEL_PATH = '../../models/srae_dtde_model.joblib'
COLUMNS_PATH = '../../models/srae_dtde_model_columns.json'
NEW_DATA_PATH = '../../data/test_logs.csv'

def engineer_features(df):
    df['eventTime'] = pd.to_datetime(df['eventTime'])
    df['time_of_day'] = df['eventTime'].dt.hour
    df = df.sort_values(by='eventTime')
    df = df.set_index('eventTime')
    df['api_call_frequency'] = df.groupby('userIdentity_arn')['key_arn'].transform(lambda x: x.rolling('1h').count())
    df = df.reset_index()
    df['errorCode'] = df['errorCode'].fillna('Success')
    
    features_to_encode = ['sourceIPAddress', 'userIdentity_arn', 'eventName', 'key_arn', 'errorCode']
    engineered_df = pd.get_dummies(df, columns=features_to_encode)
    return engineered_df

if __name__ == '__main__':
    try:
        model = joblib.load(MODEL_PATH)
        with open(COLUMNS_PATH, 'r') as f:
            model_columns = json.load(f)
        print("Successfully loaded model and columns.")

        new_df = pd.read_csv(NEW_DATA_PATH)
        prepared_new_data = engineer_features(new_df.copy())
        
        aligned_data = prepared_new_data.reindex(columns=model_columns, fill_value=0)

        print(f"\nPredicting anomalies on '{NEW_DATA_PATH}'...")
        raw_scores = model.decision_function(aligned_data)
        
        # --- FIX: Scale score to 1-100 range ---
        anomaly_scores_0_1 = 1 - (raw_scores - (-0.5)) / (0.5 - (-0.5))
        scaled_scores = (anomaly_scores_0_1.clip(0, 1) * 99) + 1
        new_df['PredictedAnomalyScore'] = scaled_scores.astype(int) # Convert to integer
        # --- END FIX ---

        print("\n--- Prediction Results ---")
        print(new_df.sort_values(by='PredictedAnomalyScore', ascending=False))

    except FileNotFoundError as e:
        print(f"\nError: A required file was not found. Please check your file paths.\nDetails: {e}")
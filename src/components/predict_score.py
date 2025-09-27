import pandas as pd
import joblib
from datetime import datetime, timezone

# --- Feature Engineering Function ---
# This function is now designed to process an entire DataFrame of new keys.
# --- (CORRECTED) Feature Engineering Function ---
# This function is now designed to process an entire DataFrame of new keys.
# --- (FINAL CORRECTED) Feature Engineering Function ---
def prepare_dataframe(df):
    """Takes a DataFrame of new keys and prepares it for the model."""
    
    # 1. Engineer date feature
    # The 'creation_date' column is already tz-aware because the 'Z' in the CSV
    # is recognized by pandas as UTC.
    
    # Get the current time in a timezone-aware (UTC) format
    now_utc = datetime.now(timezone.utc)
    
    # Both are now tz-aware in UTC, so subtraction works
    df['key_age_days'] = (now_utc - df['creation_date']).dt.days
    
    # 2. Engineer boolean features
    df['is_hsm_backed'] = df['is_hsm_backed'].astype(int)
    df['rotation_enabled'] = df['rotation_enabled'].astype(int)
    
    # 3. Engineer policy feature
    df['has_wildcard'] = df['permission_policy'].apply(lambda x: 1 if '"*"' in x else 0)

    # 4. One-hot encode algorithm feature
    df = pd.get_dummies(df, columns=['algorithm'], prefix='algo', dtype=int)
    
    # 5. Ensure all possible feature columns from training exist
    all_feature_cols = [
        'key_age_days', 'is_hsm_backed', 'rotation_enabled', 'has_wildcard',
        'algo_AES_256', 'algo_RSA_4096', 'algo_RSA_2048', 'algo_3DES'
    ]
    for col in all_feature_cols:
        if col not in df.columns:
            df[col] = 0
            
    return df[all_feature_cols]
# --- Main Prediction Logic ---
if __name__ == "__main__":
    MODEL_FILE = '../../models/srae_model.joblib'
    NEW_DATA_FILE = 'new_keys_to_predict.csv'
    
    try:
        # 1. Load the trained model
        print(f"Loading trained model from '{MODEL_FILE}'...")
        srae_model = joblib.load(MODEL_FILE)
        print("Model loaded successfully. 🔮")
        
        # 2. Load the new, unseen data from the CSV file
        print(f"Loading new key data from '{NEW_DATA_FILE}'...")
        new_keys_df = pd.read_csv(NEW_DATA_FILE, parse_dates=['creation_date'])
        
        # Keep a copy of the original data for the final report
        original_data = new_keys_df.copy()

        # 3. Prepare the new data using the feature engineering function
        print("Preparing data for prediction...")
        prepared_df = prepare_dataframe(new_keys_df)
        
        # 4. Make predictions on the entire DataFrame
        print("Making predictions...")
        predictions = srae_model.predict(prepared_df)
        
        # 5. Add the predictions to the original data for a clear report
        original_data['predicted_vulnerability_score'] = predictions.round().astype(int)

        print("\n--- Prediction Results ---")
        print(original_data[['key_id', 'algorithm', 'predicted_vulnerability_score']])

    except FileNotFoundError as e:
        print(f"FATAL ERROR: A required file was not found.")
        print(f"Details: {e}")
        print("Please make sure both 'srae_model.joblib' and 'new_keys_to_predict.csv' exist.")
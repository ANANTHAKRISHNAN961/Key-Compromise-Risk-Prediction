import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import datetime
import joblib

def train_srae_model(dataset_path='../Dataset/key_inventory_labeled.csv'):
    """
    Loads the dataset, engineers features, trains the SRAE AI model,
    evaluates its performance, and saves the trained model to a file.
    """
    print("--- SRAE AI Model Training Started ---")

    # 1. Load Data
    print(f"Step 1: Loading dataset from '{dataset_path}'...")
    try:
        df = pd.read_csv(dataset_path, parse_dates=['creation_date'])
    except FileNotFoundError:
        print(f"FATAL ERROR: The dataset file '{dataset_path}' was not found.")
        print("Please run the 'generate_dataset.py' script first.")
        return

    # 2. Feature Engineering
    print("Step 2: Performing feature engineering...")
    df['key_age_days'] = (datetime.now() - df['creation_date']).dt.days
    df['is_hsm_backed'] = df['is_hsm_backed'].astype(int)
    df['rotation_enabled'] = df['rotation_enabled'].astype(int)
    df['has_wildcard'] = df['permission_policy'].apply(lambda x: 1 if '"*"' in x else 0)
    df = pd.get_dummies(df, columns=['algorithm'], prefix='algo', dtype=int)

    # 3. Prepare Data for Training
    print("Step 3: Preparing data and splitting into training/testing sets...")
    features = [
        'key_age_days', 'is_hsm_backed', 'rotation_enabled', 'has_wildcard',
        'algo_AES_256', 'algo_RSA_4096', 'algo_RSA_2048', 'algo_3DES'
    ]
    target = 'vulnerability_score'
    
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Train the AI Model
    print("Step 4: Training the XGBoost Regressor model...")
    model = xgb.XGBRegressor(objective='reg:squarederror',
                             n_estimators=500,
                             learning_rate=0.05,
                             max_depth=6,
                             early_stopping_rounds=10,
                             random_state=42)
    
    model.fit(X_train, y_train,
              eval_set=[(X_test, y_test)],
              verbose=False)

    # 5. Evaluate the Model
    print("Step 5: Evaluating model performance...")
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"  > Mean Absolute Error (MAE): {mae:.2f}")

    # 6. Save the Trained Model to a File
    model_filename = 'srae_model.joblib'
    print(f"Step 6: Saving the trained model to '{model_filename}'...")
    joblib.dump(model, model_filename)

    print("\n--- SRAE AI Model Training Complete! ---")
    print(f"The trained model is now saved in the file: {model_filename} 💾")

# This block ensures the function runs when you execute the script
if __name__ == "__main__":
    train_srae_model()
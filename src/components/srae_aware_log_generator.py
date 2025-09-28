# srae_aware_log_generator.py (with feature engineering)
import pandas as pd
import json
import random
from faker import Faker
from datetime import datetime, timedelta
import csv

# --- Configuration ---
SRAE_INPUT_FILE = '../../data/new_keys_to_predict.csv'
OUTPUT_FILE = '../../data/srae_featured_dtde_logs_to_predict.csv' # New output file name
NUM_LOGS = 5000
START_DATE = datetime(2025, 9, 1)

# --- Define User Personas ---
personas = {
    'arn:aws:iam::12345:role/specific-role': {
        'ips': [Faker().ipv4_public() for _ in range(3)],
        'normal_hours': range(8, 20),
    },
    'arn:aws:iam::12345:user/unauthorized-user': {
        'ips': [Faker().ipv4_public() for _ in range(10)],
        'normal_hours': range(0, 24),
    },
    'arn:aws:iam::12345:assumed-role/ExternalPartnerRole': {
        'ips': [Faker().ipv4_public()],
        'normal_hours': range(9, 17),
    }
}

def check_permission(policy_str, principal_arn):
    """Parses the JSON policy and checks if the principal is allowed."""
    try:
        policy = json.loads(policy_str)
        allowed_principal = policy.get("Principal", {}).get("AWS")
        if allowed_principal == "*" or allowed_principal == principal_arn:
            return True
        if isinstance(allowed_principal, list) and principal_arn in allowed_principal:
            return True
    except (json.JSONDecodeError, AttributeError):
        return False
    return False

def generate_logs():
    try:
        srae_df = pd.read_csv(SRAE_INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: Make sure '{SRAE_INPUT_FILE}' exists at the specified path.")
        return

    logs = []
    fake = Faker()
    print(f"Generating {NUM_LOGS} raw log entries...")

    # --- Generate Normal and AccessDenied Logs ---
    for _ in range(NUM_LOGS):
        actor_arn, actor_profile = random.choice(list(personas.items()))
        key_row = srae_df.sample(1).iloc[0]
        key_id = key_row['key_id']
        policy = key_row['permission_policy']
        is_allowed = check_permission(policy, actor_arn)
        
        time_delta = timedelta(days=random.randint(0, 25), hours=random.choice(actor_profile['normal_hours']), minutes=random.randint(0, 59))
        event_time = START_DATE + time_delta

        log_entry = {
            'eventTime': event_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'sourceIPAddress': random.choice(actor_profile['ips']),
            'userIdentity_arn': actor_arn,
            'eventName': 'Decrypt',
            'key_arn': key_id,
            'errorCode': '' if is_allowed else 'AccessDeniedException'
        }
        logs.append(log_entry)

    # --- Convert to DataFrame ---
    df = pd.DataFrame(logs)
    
    # --- Feature Engineering Steps ---
    print("Adding engineered feature columns...")
    df['eventTime'] = pd.to_datetime(df['eventTime'])
    df['time_of_day'] = df['eventTime'].dt.hour
    df = df.sort_values(by='eventTime')
    
    # Set eventTime as the index for the rolling calculation
    df = df.set_index('eventTime')
    
    # Calculate frequency using a 1-hour rolling window
    df['api_call_frequency'] = df.groupby('userIdentity_arn')['key_arn'].transform(lambda x: x.rolling('1h').count())

    # Reset the index to turn eventTime back into a column
    df = df.reset_index()
    
    print("Feature engineering complete.")
    # --- End of Feature Engineering ---

    # --- Write the FINAL DataFrame to CSV ---
    df.to_csv(OUTPUT_FILE, index=False)
        
    print(f"\nSuccessfully generated '{OUTPUT_FILE}' with all feature columns.")
    print("\nHere's a sample of the final data:")
    print(df.head())

if __name__ == '__main__':
    generate_logs()
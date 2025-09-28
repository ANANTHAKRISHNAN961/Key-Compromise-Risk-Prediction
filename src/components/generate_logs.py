import json
import random
from datetime import datetime, timedelta, timezone # <-- FIX: Import timezone
import os # <-- FIX: Import the os module
from faker import Faker

# --- Configuration ---
NUM_LOGS = 10000
ANOMALY_RATE = 0.02

# --- FIX: Build a robust file path based on the script's location ---
SCRIPT_DIR = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '../../data/kms_access_logs.json')
# --- END FIX ---

fake = Faker()

# --- User & Key Profiles for Realistic Simulation ---
NORMAL_USERS = [
    'arn:aws:iam::12345:role/app-server-prod',
    'arn:aws:iam::12345:role/data-pipeline-etl',
    'arn:aws:iam::12345:user/security-admin'
]
KEY_IDS = [f'key-new-{i:03d}' for i in range(1, 21)]

def generate_normal_log(timestamp):
    """Generates a log entry representing typical behavior."""
    user = random.choice(NORMAL_USERS)
    ip_address = fake.ipv4(network=False)
    
    if 'app-server' in user:
        action = 'Encrypt'
        ip_address = '52.95.110.1'
    elif 'data-pipeline' in user:
        action = 'Decrypt'
        ip_address = '10.0.1.55'
    else: # admin
        action = random.choice(['Encrypt', 'Decrypt', 'DescribeKey'])
        ip_address = fake.ipv4_private()

    return {
        "log_id": fake.uuid4(),
        "timestamp": timestamp.isoformat(),
        "key_id": random.choice(KEY_IDS),
        "user_id": user,
        "source_ip": ip_address,
        "action": action,
        "user_agent": "aws-sdk-py/1.28.58",
        "status": "Success"
    }

def generate_anomaly(timestamp):
    """Generates a log entry representing suspicious behavior."""
    anomaly_type = random.choice(['ip', 'action', 'time', 'brute_force'])
    
    log = generate_normal_log(timestamp)
    log['status'] = 'Success'
    
    if anomaly_type == 'ip':
        log['user_id'] = 'arn:aws:iam::12345:role/app-server-prod'
        log['source_ip'] = fake.ipv4_public()
        log['action'] = 'Decrypt'
    elif anomaly_type == 'action':
        log['user_id'] = 'arn:aws:iam::12345:role/app-server-prod'
        log['action'] = 'Decrypt'
    elif anomaly_type == 'time':
        log['user_id'] = 'arn:aws:iam::12345:user/security-admin'
    elif anomaly_type == 'brute_force':
        log['action'] = 'Decrypt'
        log['status'] = 'Failure'
        
    return log

# --- Main Generation Logic ---
print(f"Generating {NUM_LOGS} log records...")
logs = []
# --- FIX: Use timezone-aware datetime.now() ---
current_time = datetime.now(timezone.utc)
# --- END FIX ---

for i in range(NUM_LOGS):
    time_delta = timedelta(minutes=random.randint(1, 10))
    log_time = current_time - (i * time_delta)
    
    is_odd_hour = 2 <= log_time.hour <= 4
    
    if is_odd_hour and random.random() < 0.5:
        logs.append(generate_anomaly(log_time))
    elif random.random() < ANOMALY_RATE:
        logs.append(generate_anomaly(log_time))
    else:
        logs.append(generate_normal_log(log_time))

# Save to a JSON file
with open(OUTPUT_FILE, 'w') as f:
    json.dump(logs, f, indent=2)

print(f"Successfully generated log file at '{OUTPUT_FILE}'")
print("\nSample of a normal log entry:")
print(json.dumps(logs[0], indent=2))
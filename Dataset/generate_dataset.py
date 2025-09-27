import pandas as pd
import random
import json
from datetime import datetime, timedelta

# --- Configuration ---
NUM_RECORDS = 10000
OUTPUT_FILE = 'key_inventory_labeled.csv'

# --- (IMPROVED) Helper Functions to create diverse data ---
def get_random_date():
    """Generates a truly random datetime within the last 5 years."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1825) # Approx. 5 years ago
    
    time_between_dates = end_date - start_date
    seconds_between_dates = time_between_dates.total_seconds()
    random_number_of_seconds = random.randrange(int(seconds_between_dates))
    
    random_date = start_date + timedelta(seconds=random_number_of_seconds)
    return random_date

def get_random_algorithm():
    return random.choices(['AES_256', 'RSA_4096', 'RSA_2048', '3DES'], weights=[60, 20, 15, 5], k=1)[0]

def get_random_policy():
    if random.random() < 0.1: # 10% chance of a wildcard policy
        return json.dumps({"Principal":{"AWS":"*"},"Action":"kms:*"})
    return json.dumps({"Principal":{"AWS":"arn:aws:iam::12345:role/specific-role"},"Action":"kms:Encrypt"})

# --- Rule-based scoring function (our "teacher") ---
def calculate_score(row):
    score = 0
    # Age risk
    age_days = (datetime.now() - row['creation_date']).days
    if age_days > 730: score += 20
    elif age_days > 365: score += 10
    # Algorithm risk
    if row['algorithm'] in ['RSA_2048', '3DES']: score += 30
    # HSM risk
    if not row['is_hsm_backed']: score += 15
    # Rotation risk
    if not row['rotation_enabled']: score += 15
    # Permission risk
    policy = json.loads(row['permission_policy'])
    if policy.get('Principal', {}).get('AWS', '') == '*': score += 40
    
    # Normalize to 0-100 and add noise
    normalized_score = min(100, score)
    noisy_score = normalized_score + random.uniform(-3, 3) # Add randomness
    return max(0, min(100, round(noisy_score)))

# --- Main Generation Logic ---
print(f"Generating {NUM_RECORDS} synthetic records with varied timestamps...")
data = []
for i in range(NUM_RECORDS):
    record = {
        'key_id': f'key-{i:05d}',
        'creation_date': get_random_date(), # Using the improved function
        'algorithm': get_random_algorithm(),
        'is_hsm_backed': random.choice([True, False]),
        'rotation_enabled': random.choice([True, False]),
        'permission_policy': get_random_policy()
    }
    data.append(record)

df = pd.DataFrame(data)
# Apply the "teacher" scoring function to create our labels
df['vulnerability_score'] = df.apply(calculate_score, axis=1)

# Save to CSV
df.to_csv(OUTPUT_FILE, index=False)
print(f"Labeled dataset successfully created at '{OUTPUT_FILE}'")
print("\nSample of the newly generated data:")
print(df[['key_id', 'creation_date', 'vulnerability_score']].head())
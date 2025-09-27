// Define a shared type for our key data
export interface CryptoKey {
  key_id: string;
  creation_date: string;
  algorithm: string;
  is_hsm_backed: boolean;
  rotation_enabled: boolean;
}

const API_BASE_URL = 'http://127.0.0.1:8000';

export async function fetchKeys(): Promise<CryptoKey[]> {
  const response = await fetch(`${API_BASE_URL}/keys/inventory`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch key inventory from the API.');
  }
  
  const data = await response.json();
  return data.keys;
}

// Add this new function to the bottom of the file
export async function fetchVulnerabilityScore(key: CryptoKey): Promise<number> {
  const response = await fetch(`${API_BASE_URL}/predict_vulnerability`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(key),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch vulnerability score.');
  }

  const data = await response.json();
  return data.predicted_vulnerability_score;
}
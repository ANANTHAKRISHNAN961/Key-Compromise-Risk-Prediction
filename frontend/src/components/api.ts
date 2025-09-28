import type { CryptoKey, LogEntryWithScore } from '../types';

export interface PaginatedLogsResponse {
  logs: LogEntryWithScore[];
  total_pages: number;
  current_page: number;
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

export async function fetchVulnerabilityScore(key: CryptoKey): Promise<number> {
  const response = await fetch(`${API_BASE_URL}/predict_vulnerability`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(key),
  });
  if (!response.ok) {
    throw new Error('Failed to fetch vulnerability score.');
  }
  const data = await response.json();
  return data.predicted_vulnerability_score;
}

export async function fetchScoredLogs(page: number): Promise<PaginatedLogsResponse> {
  const limit = 50; // Page size is fixed at 50
  const response = await fetch(`${API_BASE_URL}/logs/scored?page=${page}&limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch scored logs.');
  }
  return await response.json();
}

export async function getRecommendedAction(riskInput: { vulnerability_score?: number; anomaly_score?: number }): Promise<{ recommended_action: string }> {
  const response = await fetch(`${API_BASE_URL}/get_action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(riskInput),
  });
  if (!response.ok) {
    throw new Error('Failed to fetch recommended action.');
  }
  return await response.json();
}
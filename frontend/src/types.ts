export interface CryptoKey {
  key_id: string;
  creation_date: string;
  algorithm: string;
  is_hsm_backed: boolean;
  rotation_enabled: boolean;
  permission_policy: string;
}

export interface CryptoKeyWithScore extends CryptoKey {
  vulnerability_score?: number | string;
  recommended_action?: string;
}

export interface LogEntry {
  log_id: string;
  timestamp: string;
  key_id: string;
  user_id: string;
  source_ip: string;
  action: string;
  user_agent: string;
  status: string;
}

export interface LogEntryWithScore extends LogEntry {
  anomaly_score?: number;
  recommended_action?: string;
}
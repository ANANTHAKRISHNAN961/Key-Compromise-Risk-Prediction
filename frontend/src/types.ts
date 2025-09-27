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
}
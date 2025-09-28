import React from 'react';
import type { CryptoKeyWithScore } from '../types';

interface KeyTableProps {
  keys: CryptoKeyWithScore[];
  onGetAction: (keyId: string) => void;
}

const getScoreColor = (score: number | string) => {
  if (typeof score !== 'number') return { color: 'gray' };
  if (score > 75) return { backgroundColor: '#e76f51', color: 'white' };
  if (score > 50) return { backgroundColor: '#f4a261', color: 'black' };
  if (score > 25) return { backgroundColor: '#e9c46a', color: 'black' };
  return { backgroundColor: '#2a9d8f', color: 'white' };
};

const getActionStyle = (action: string | null | undefined) => {
    if (!action) return '';
    switch (action) {
      case 'QUARANTINE_KEY':
      case 'RESTRICT_PERMISSIONS':
        return 'action-severe';
      case 'FORCE_ROTATE_KEY':
        return 'action-moderate';
      case 'ALERT_SOC':
        return 'action-mild';
      case 'NO_OP':
        return 'action-none';
      default:
        return '';
    }
  };

const KeyTable: React.FC<KeyTableProps> = ({ keys, onGetAction }) => {
  return (
    <table>
      <thead>
        <tr>
          <th>Key ID</th>
          <th>Algorithm</th>
          <th>Creation Date</th>
          <th>HSM Backed</th>
          <th>Rotation Enabled</th>
          <th>Vulnerability Score</th>
          <th>Recommended Action</th>
        </tr>
      </thead>
      <tbody>
        {keys.map((key) => (
          <tr key={key.key_id}>
            <td>{key.key_id}</td>
            <td>{key.algorithm}</td>
            <td>{new Date(key.creation_date).toLocaleDateString()}</td>
            <td>{key.is_hsm_backed ? '✅ Yes' : '❌ No'}</td>
            <td>{key.rotation_enabled ? '✅ Yes' : '❌ No'}</td>
            <td>
              <span className="score-badge" style={getScoreColor(key.vulnerability_score || 0)}>
                {key.vulnerability_score ?? '...'}
              </span>
            </td>
            <td>
              {key.recommended_action ? (
                <span className={`action-badge ${getActionStyle(key.recommended_action)}`}>
                  {key.recommended_action}
                </span>
              ) : (
                <button 
                  onClick={() => onGetAction(key.key_id)} 
                  disabled={typeof key.vulnerability_score !== 'number'}
                  className="action-button"
                >
                  Analyze
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default KeyTable;
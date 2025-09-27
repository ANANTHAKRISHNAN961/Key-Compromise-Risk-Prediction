import React from 'react';
import type { CryptoKey } from './api';

// Update the CryptoKey type to include the optional score
interface CryptoKeyWithScore extends CryptoKey {
  vulnerability_score?: number | string;
}

interface KeyTableProps {
  keys: CryptoKeyWithScore[];
}

// Helper function to get the color for the score
const getScoreColor = (score: number | string) => {
  if (typeof score !== 'number') return { color: 'gray' };
  if (score > 75) return { backgroundColor: '#ff4b4b', color: 'white' };
  if (score > 50) return { backgroundColor: '#ffac33', color: 'black' };
  if (score > 25) return { backgroundColor: '#fce83a', color: 'black' };
  return { backgroundColor: '#3dd56d', color: 'white' };
};

const KeyTable: React.FC<KeyTableProps> = ({ keys }) => {
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
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default KeyTable;
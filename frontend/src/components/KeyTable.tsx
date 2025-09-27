import React from 'react';
import type { CryptoKey } from './api';

// Define the props (inputs) that this component expects
interface KeyTableProps {
  keys: CryptoKey[];
}

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
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default KeyTable;
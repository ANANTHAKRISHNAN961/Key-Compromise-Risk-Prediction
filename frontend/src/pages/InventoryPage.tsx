import React, { useState, useEffect } from 'react';
import { type CryptoKey, fetchKeys } from '../components/api';
import KeyTable from '../components/KeyTable';

const InventoryPage: React.FC = () => {
  const [keys, setKeys] = useState<CryptoKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchKeys()
      .then(fetchedKeys => {
        setKeys(fetchedKeys);
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return (
    <div className="container">
      <header>
        <h1>Key Inventory</h1>
        <p>A detailed list of all monitored cryptographic keys.</p>
      </header>
      <main>
        {isLoading && <p className="loading-text">Loading keys from API...</p>}
        {error && <p className="error-text">{error}</p>}
        {!isLoading && !error && (
          <KeyTable keys={keys} />
        )}
      </main>
    </div>
  );
};

export default InventoryPage;
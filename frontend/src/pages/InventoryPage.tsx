import React, { useState, useEffect } from 'react';
import { fetchKeys, fetchVulnerabilityScore, type CryptoKey } from '../components/api';
import KeyTable from '../components/KeyTable';

// Define the updated type here as well
interface CryptoKeyWithScore extends CryptoKey {
  vulnerability_score?: number | string;
}

const InventoryPage: React.FC = () => {
  const [keys, setKeys] = useState<CryptoKeyWithScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAndScoreKeys() {
      try {
        // Step 1: Fetch the initial list of keys
        const initialKeys = await fetchKeys();
        // Initially, display keys without scores
        setKeys(initialKeys);
        setIsLoading(false); // Stop initial loading

        // Step 2: Asynchronously fetch scores for each key
        const scoredKeys = await Promise.all(
          initialKeys.map(async (key) => {
            try {
              const score = await fetchVulnerabilityScore(key);
              return { ...key, vulnerability_score: score };
            } catch (error) {
              console.error(`Failed to get score for key ${key.key_id}`, error);
              return { ...key, vulnerability_score: 'Error' };
            }
          })
        );
        
        // Step 3: Update the state with the new keys that include scores
        setKeys(scoredKeys);

      } catch (err) {
        if (err instanceof Error) setError(err.message);
        setIsLoading(false);
      }
    }

    loadAndScoreKeys();
  }, []);

  return (
    <div className="container">
      <header>
        <h1>Key Inventory</h1>
        <p>A detailed list of all monitored cryptographic keys.</p>
      </header>
      <main>
        {isLoading && <p className="loading-text">Loading key inventory...</p>}
        {error && <p className="error-text">{error}</p>}
        {!isLoading && !error && (
          <KeyTable keys={keys} />
        )}
      </main>
    </div>
  );
};

export default InventoryPage;
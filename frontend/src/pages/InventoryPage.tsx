import React, { useState, useEffect } from 'react';
import { fetchKeys, fetchVulnerabilityScore, getRecommendedAction } from '../components/api';
import KeyTable from '../components/KeyTable';
import type { CryptoKeyWithScore } from '../types';


const InventoryPage: React.FC = () => {
  const [keys, setKeys] = useState<CryptoKeyWithScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAndScoreKeys() {
      try {
        const initialKeys = await fetchKeys();
        setKeys(initialKeys.map(key => ({ ...key, vulnerability_score: '...' })));
        setIsLoading(false);

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
        
        setKeys(scoredKeys);

      } catch (err) {
        if (err instanceof Error) setError(err.message);
        setIsLoading(false);
      }
    }

    loadAndScoreKeys();
  }, []);

  const handleGetAction = async (keyId: string) => {
    const key = keys.find(k => k.key_id === keyId);
    if (!key || typeof key.vulnerability_score !== 'number') return;

    // Set loading state for this specific key
    setKeys(currentKeys =>
      currentKeys.map(k =>
        k.key_id === keyId ? { ...k, recommended_action: 'Loading...' } : k
      )
    );

    try {
      const response = await getRecommendedAction({ vulnerability_score: key.vulnerability_score });
      setKeys(currentKeys =>
        currentKeys.map(k =>
          k.key_id === keyId ? { ...k, recommended_action: response.recommended_action } : k
        )
      );
    } catch (error) {
      console.error("Failed to get recommended action", error);
      setKeys(currentKeys =>
        currentKeys.map(k =>
          k.key_id === keyId ? { ...k, recommended_action: 'Error' } : k
        )
      );
    }
  };


  return (
    <div className="container">
      <header>
        <h1>Key Inventory</h1>
        <p>A detailed list of all monitored cryptographic keys and their AI-driven risk assessments.</p>
      </header>
      <main>
        {isLoading && <p className="loading-text">Loading key inventory...</p>}
        {error && <p className="error-text">{error}</p>}
        {!isLoading && !error && (
          <KeyTable keys={keys} onGetAction={handleGetAction} />
        )}
      </main>
    </div>
  );
};

export default InventoryPage;
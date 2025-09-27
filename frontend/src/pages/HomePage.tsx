import React, { useState, useEffect } from 'react';
import './HomePage.css';
import { fetchKeys, fetchVulnerabilityScore } from '../components/api';
import type { CryptoKeyWithScore } from '../types';
import RiskChart from '../components/RiskChart'; // Import our new chart

interface KpiData {
  totalKeys: number;
  highRiskKeys: number;
}

const HomePage: React.FC = () => {
  const [scoredKeys, setScoredKeys] = useState<CryptoKeyWithScore[]>([]);
  const [kpiData, setKpiData] = useState<KpiData>({ totalKeys: 0, highRiskKeys: 0 });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadAndScoreKeys() {
      try {
        const initialKeys = await fetchKeys();
        const keysWithScores = await Promise.all(
          initialKeys.map(async (key) => {
            const score = await fetchVulnerabilityScore(key);
            return { ...key, vulnerability_score: score };
          })
        );
        
        // Calculate KPIs
        const total = keysWithScores.length;
        const highRisk = keysWithScores.filter(k => typeof k.vulnerability_score === 'number' && k.vulnerability_score > 50).length;
        
        setScoredKeys(keysWithScores);
        setKpiData({ totalKeys: total, highRiskKeys: highRisk });

      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setIsLoading(false);
      }
    }
    loadAndScoreKeys();
  }, []);

  return (
    <div className="homepage-container">
      <div className="kpi-grid">
        <div className="kpi-card">
          <h2>Total Keys Monitored</h2>
          <p className="kpi-value">{isLoading ? '...' : kpiData.totalKeys}</p>
        </div>
        <div className="kpi-card high-risk">
          <h2>High-Risk Keys {'>'}50</h2>
          <p className="kpi-value">{isLoading ? '...' : kpiData.highRiskKeys}</p>
        </div>
        <div className="kpi-card">
          <h2>Active Alerts (24h)</h2>
          <p className="kpi-value">0</p>
        </div>
        <div className="kpi-card operational">
          <h2>System Status</h2>
          <p className="kpi-value">Operational</p>
        </div>
      </div>

      <div className="main-content-grid">
        <div className="content-card">
          <h3>Risk Distribution</h3>
          {isLoading ? <p>Loading chart data...</p> : <RiskChart keys={scoredKeys} />}
        </div>
        <div className="content-card">
          <h3>Recent Activity</h3>
          <ul className="activity-feed">
            <li><span className="timestamp">12:28 AM</span> - Dashboard data refreshed.</li>
            <li><span className="timestamp">12:25 AM</span> - Analyst logged in.</li>
            <li><span className="timestamp">Sep 27</span> - Model 'srae_model.joblib' updated.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
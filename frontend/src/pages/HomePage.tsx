import React from 'react';
import './HomePage.css'; // We'll create this file next

const HomePage: React.FC = () => {
  return (
    <div className="homepage-container">
      <div className="kpi-grid">
        <div className="kpi-card">
          <h2>Total Keys Monitored</h2>
          <p className="kpi-value">4</p>
        </div>
        <div className="kpi-card high-risk">
          <h2>High-Risk Keys</h2>
          <p className="kpi-value">2</p>
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
          <p>This chart shows the breakdown of keys by their calculated SRAE vulnerability score. (Chart component to be added later).</p>
          
        </div>
        <div className="content-card">
          <h3>Recent Activity</h3>
          <ul className="activity-feed">
            <li><span className="timestamp">11:00 PM</span> - SRAE scan completed on 4 keys.</li>
            <li><span className="timestamp">10:58 PM</span> - Analyst logged in.</li>
            <li><span className="timestamp">Sep 26</span> - Model 'srae_model.joblib' updated.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
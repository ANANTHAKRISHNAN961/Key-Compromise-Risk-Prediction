import React, { useState, useEffect, useMemo } from 'react';
import type { LogEntryWithScore } from '../types';
import { fetchScoredLogs } from '../components/api';
import './AccessLogsPage.css';

const ANOMALY_THRESHOLD = 75;

const AccessLogsPage: React.FC = () => {
  // === STATE MANAGEMENT ===
  const [logs, setLogs] = useState<LogEntryWithScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'time' | 'score'>('time');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  // === DATA FETCHING EFFECT ===
  useEffect(() => {
    // This effect re-runs whenever the currentPage changes
    async function loadScoredLogs() {
      setIsLoading(true);
      try {
        const response = await fetchScoredLogs(currentPage);
        setLogs(response.logs);
        setTotalPages(response.total_pages);
      } catch (error) {
        console.error("Failed to load scored logs", error);
      } finally {
        setIsLoading(false);
      }
    }
    loadScoredLogs();
  }, [currentPage]);

  // === SORTING LOGIC ===
  // useMemo will re-calculate the sorted logs only when 'logs' or 'sortBy' changes
  const sortedLogs = useMemo(() => {
    const logsCopy = [...logs]; // Create a copy to avoid mutating the original state
    if (sortBy === 'score') {
      logsCopy.sort((a, b) => {
        const scoreA = typeof a.anomaly_score === 'number' ? a.anomaly_score : -1;
        const scoreB = typeof b.anomaly_score === 'number' ? b.anomaly_score : -1;
        return scoreB - scoreA; // Sorts highest numbers (anomalies) to the top
      });
    }
    // Default is 'time', which is the order from the API (reverse chronological)
    return logsCopy;
  }, [logs, sortBy]);

  // === JSX FOR RENDERING ===
  return (
    <div className="container">
      <header>
        <h1>Access Log Analysis</h1>
        <div className="header-controls">
          <p>Real-time anomaly detection. Scores &gt; {ANOMALY_THRESHOLD} are high-risk.</p>
          <div className="sort-controls">
            <span>Sort by:</span>
            <button onClick={() => setSortBy('time')} className={sortBy === 'time' ? 'active' : ''}>Time</button>
            <button onClick={() => setSortBy('score')} className={sortBy === 'score' ? 'active' : ''}>Score</button>
          </div>
        </div>
      </header>
      <main>
        {isLoading ? (
          <p className="loading-text">Loading and analyzing logs...</p>
        ) : (
          <>
            <div className="log-table-container">
              <table>
                <thead>
                  <tr>
                    <th>Anomaly Score</th>
                    <th>Timestamp</th>
                    <th>User ID</th>
                    <th>Action</th>
                    <th>Source IP</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedLogs.map((log) => (
                    <tr key={log.log_id} className={log.anomaly_score && log.anomaly_score > ANOMALY_THRESHOLD ? 'anomaly-row' : ''}>
                      <td>
                        <span className="score-badge" style={{backgroundColor: log.anomaly_score && log.anomaly_score > ANOMALY_THRESHOLD ? '#ff4b4b' : '#3a3a3a'}}>
                          {log.anomaly_score ?? '...'}
                        </span>
                      </td>
                      <td>{new Date(log.timestamp).toLocaleString()}</td>
                      <td>{log.user_id}</td>
                      <td>{log.action}</td>
                      <td>{log.source_ip}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination-controls">
              <button onClick={() => setCurrentPage(currentPage - 1)} disabled={currentPage <= 1}>
                &larr; Previous
              </button>
              <span>Page {currentPage} of {totalPages}</span>
              <button onClick={() => setCurrentPage(currentPage + 1)} disabled={currentPage >= totalPages}>
                Next &rarr;
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default AccessLogsPage;
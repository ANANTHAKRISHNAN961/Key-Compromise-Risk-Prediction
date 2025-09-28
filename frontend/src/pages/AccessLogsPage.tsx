import React, { useState, useEffect, useMemo } from 'react';
import type { LogEntryWithScore } from '../types';
import { fetchScoredLogs, getRecommendedAction } from '../components/api';
import './AccessLogsPage.css';

const ANOMALY_THRESHOLD = 75;

const AccessLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntryWithScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'time' | 'score'>('time');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
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

  const handleGetAction = async (logId: string) => {
    const log = logs.find(l => l.log_id === logId);
    if (!log || typeof log.anomaly_score !== 'number') return;

    setLogs(currentLogs =>
      currentLogs.map(l =>
        l.log_id === logId ? { ...l, recommended_action: 'Loading...' } : l
      )
    );

    try {
      const response = await getRecommendedAction({ anomaly_score: log.anomaly_score });
      setLogs(currentLogs =>
        currentLogs.map(l =>
          l.log_id === logId ? { ...l, recommended_action: response.recommended_action } : l
        )
      );
    } catch (error) {
      console.error("Failed to get recommended action", error);
      setLogs(currentLogs =>
        currentLogs.map(l =>
          l.log_id === logId ? { ...l, recommended_action: 'Error' } : l
        )
      );
    }
  };

  const sortedLogs = useMemo(() => {
    const logsCopy = [...logs];
    if (sortBy === 'score') {
      logsCopy.sort((a, b) => (b.anomaly_score ?? 0) - (a.anomaly_score ?? 0));
    }
    return logsCopy;
  }, [logs, sortBy]);

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

  return (
    <div className="container">
      <header>
        <h1>Access Log Analysis</h1>
        <div className="header-controls">
          <p>Real-time anomaly detection with AI-driven action recommendations. Scores &gt; {ANOMALY_THRESHOLD} are high-risk.</p>
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
                    <th>Recommended Action</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedLogs.map((log) => (
                    <tr key={log.log_id} className={log.anomaly_score && log.anomaly_score > ANOMALY_THRESHOLD ? 'anomaly-row' : ''}>
                      <td>
                        <span className="score-badge" style={{backgroundColor: log.anomaly_score && log.anomaly_score > ANOMALY_THRESHOLD ? '#e76f51' : '#3a3a3a'}}>
                          {log.anomaly_score ?? '...'}
                        </span>
                      </td>
                      <td>{new Date(log.timestamp).toLocaleString()}</td>
                      <td>{log.user_id}</td>
                      <td>{log.action}</td>
                      <td>{log.source_ip}</td>
                      <td>
                        {log.recommended_action ? (
                          <span className={`action-badge ${getActionStyle(log.recommended_action)}`}>
                            {log.recommended_action}
                          </span>
                        ) : (
                          <button 
                            onClick={() => handleGetAction(log.log_id)} 
                            disabled={typeof log.anomaly_score !== 'number'}
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
import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function Dashboard() {
  const [boards, setBoards] = useState([]);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [dropStats, setDropStats] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    // Initial load
    loadDashboardData();

    // Set up auto-refresh
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadDashboardData();
      }, refreshInterval * 1000);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, selectedBoard]);

  const loadDashboardData = async () => {
    if (selectedBoard) {
      await Promise.all([
        loadLeaderboard(),
        loadDropStats()
      ]);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/leaderboard/${selectedBoard}`);
      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data);
      }
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    }
  };

  const loadDropStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats/drops`);
      if (response.ok) {
        const data = await response.json();
        setDropStats(data);
      }
    } catch (error) {
      console.error('Error loading drop stats:', error);
    }
  };

  const handleRefreshClick = () => {
    loadDashboardData();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>BINGO Tracker Dashboard</h1>
        <div className="dashboard-controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh every
          </label>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            disabled={!autoRefresh}
          >
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
            <option value={300}>5m</option>
          </select>
          <button onClick={handleRefreshClick} className="refresh-btn">
            🔄 Refresh Now
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <section className="board-selector">
          <h2>Select Board</h2>
          <input
            type="text"
            placeholder="Enter board name..."
            value={selectedBoard || ''}
            onChange={(e) => setSelectedBoard(e.target.value)}
            className="board-input"
          />
        </section>

        {selectedBoard && (
          <>
            <section className="leaderboard-section">
              <h2>Team Leaderboard</h2>
              {leaderboard.length > 0 ? (
                <div className="leaderboard">
                  {leaderboard.map((team, index) => (
                    <div
                      key={team.team}
                      className="leaderboard-item"
                      style={{ borderLeft: `5px solid ${team.color}` }}
                    >
                      <div className="rank">#{index + 1}</div>
                      <div className="team-info">
                        <div className="team-name">{team.team}</div>
                        <div className="team-stats">
                          <span className="points">{team.points} points</span>
                          <span className="completed">{team.completed} tiles</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No leaderboard data available</p>
              )}
            </section>

            <section className="drops-section">
              <h2>Recent Drops</h2>
              {dropStats && dropStats.recent_drops ? (
                <div className="drops-list">
                  {dropStats.recent_drops.map((drop, index) => (
                    <div key={index} className="drop-item">
                      <div className="drop-header">
                        <span className="player-name">{drop.playerName}</span>
                        {drop.teamName && (
                          <span className="team-badge">{drop.teamName}</span>
                        )}
                      </div>
                      <div className="drop-details">
                        <span className="item-name">
                          {drop.itemName} x{drop.quantity}
                        </span>
                        {drop.value && (
                          <span className="item-value">
                            {drop.value.toLocaleString()} GP
                          </span>
                        )}
                        {drop.rarity && (
                          <span className="item-rarity">{drop.rarity}</span>
                        )}
                      </div>
                      <div className="drop-time">
                        {new Date(drop.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No recent drops</p>
              )}
            </section>

            <section className="stats-section">
              <h2>Statistics</h2>
              {dropStats && (
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{dropStats.total_drops}</div>
                    <div className="stat-label">Total Drops</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{dropStats.unique_players}</div>
                    <div className="stat-label">Active Players</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{leaderboard.length}</div>
                    <div className="stat-label">Teams</div>
                  </div>
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;

import React, { useState } from 'react';

export default function SetupScreen({ onStartGame }) {
  const [playerCount, setPlayerCount] = useState(4);
  const [playerName, setPlayerName] = useState('You');
  const [difficulty, setDifficulty] = useState('Medium');

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartGame(playerCount, playerName, difficulty);
  };

  return (
    <div className="setup-screen">
      <div className="setup-card">
        <h1 className="setup-title">🦆 Duck: The Card Game</h1>
        <p className="setup-subtitle">
          Strategic trick-taking game for 3 to 7 players. Predict your exact wins to claim +10 bonus points!
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Your Name:</label>
            <input
              type="text"
              className="form-input"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Total Players (3 to 7):</label>
            <select
              className="form-select"
              value={playerCount}
              onChange={(e) => setPlayerCount(Number(e.target.value))}
            >
              {[3, 4, 5, 6, 7].map((num) => (
                <option key={num} value={num}>
                  {num} Players ({num - 1} AI Bots)
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">AI Bot Difficulty:</label>
            <select
              className="form-select"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="Easy">Easy (Casual)</option>
              <option value="Medium">Medium (Tactical)</option>
              <option value="Hard">Hard (Aggressive)</option>
            </select>
          </div>

          <button type="submit" className="btn-primary">
            🚀 Deal First Hand (7 Cards)
          </button>
        </form>
      </div>
    </div>
  );
}

import React from 'react';

export default function ScoreboardModal({ gameState, onClose }) {
  if (!gameState) return null;

  const players = gameState.players || [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        style={{ maxWidth: '640px' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="modal-title">🏆 Scoreboard Breakdown</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1rem' }}>
          Round {gameState.current_round} of {gameState.max_rounds} ({gameState.hand_size} Cards)
        </p>

        <table className="score-table">
          <thead>
            <tr>
              <th>Player</th>
              <th>Bid</th>
              <th>Won</th>
              <th>Past Rounds</th>
              <th>This Round</th>
              <th>Total Score</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p) => {
              const exactBonus = p.has_exact_bonus;
              return (
                <tr key={p.player_id}>
                  <td style={{ fontWeight: 700, textAlign: 'left' }}>
                    {p.name} {p.is_human ? '(You)' : ''}
                  </td>
                  <td>{p.bid !== null ? p.bid : '-'}</td>
                  <td>{p.tricks_won}</td>
                  <td style={{ color: '#94a3b8' }}>{p.cumulative_score}</td>
                  <td style={{ fontWeight: 600, color: exactBonus ? '#4ade80' : '#cbd5e1' }}>
                    +{p.current_round_points} {exactBonus ? '🌟' : ''}
                  </td>
                  <td style={{ fontWeight: 800, color: '#e5b94c', fontSize: '1.05rem' }}>
                    {p.score}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <p
          style={{
            marginTop: '1rem',
            color: '#cbd5e1',
            fontSize: '0.8rem',
            fontStyle: 'italic',
          }}
        >
          * 🌟 = Exact prediction match (+10 Bonus Points added to Total Score).
        </p>

        <button
          className="btn-primary"
          style={{ marginTop: '1.5rem', width: 'auto', padding: '0.6rem 2rem' }}
          onClick={onClose}
        >
          Close Scoreboard
        </button>
      </div>
    </div>
  );
}

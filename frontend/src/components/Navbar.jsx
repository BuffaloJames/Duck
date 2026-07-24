import React from 'react';

export default function Navbar({ gameState, onOpenScoreboard, onOpenRules, onNewGame }) {
  const currentRound = gameState?.current_round || 1;
  const handSize = gameState?.hand_size || 7;

  return (
    <header className="navbar">
      <div className="navbar-left">
        <div className="brand-title">
          <span>🦆 DUCK</span>
          <span className="brand-badge">Cards</span>
        </div>

        {gameState && (
          <div className="game-info-pills">
            <div className="info-pill">
              <span>Round {currentRound} of 7</span>
              <small>({handSize} {handSize === 1 ? 'card' : 'cards'})</small>
            </div>

            <div className="info-pill trump-spades">
              <span>♠ Permanent Trump: Spades</span>
            </div>
          </div>
        )}
      </div>

      <div className="navbar-actions">
        <button className="btn-nav" onClick={onOpenRules}>
          📜 Rules
        </button>
        {gameState && (
          <button className="btn-nav" onClick={onOpenScoreboard}>
            📊 Scoreboard
          </button>
        )}
        <button className="btn-nav" onClick={onNewGame}>
          🔄 New Game
        </button>
      </div>
    </header>
  );
}

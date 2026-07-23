import React, { useState } from 'react';
import CardUnit from './CardUnit';

const BOT_AVATARS = ['🦆', '🐤', '🦆', '🦢', '🐣', '🦆'];

export default function GameBoard({ gameState, onPlayCard, onAdvanceRound }) {
  const [showHistory, setShowHistory] = useState(false);

  if (!gameState) return null;

  const {
    players,
    current_turn_id,
    current_trick,
    last_completed_trick,
    phase,
    hand_size,
    trick_history,
  } = gameState;

  const humanPlayer = players[0];
  const botPlayers = players.slice(1);
  const isHumanTurn = current_turn_id === humanPlayer?.player_id && phase === 'PLAYING';

  const displayTrick =
    current_trick && current_trick.cards_played && current_trick.cards_played.length > 0
      ? current_trick
      : last_completed_trick;

  const trickWinnerPlayer = displayTrick?.winner_id
    ? players.find((p) => p.player_id === displayTrick.winner_id)
    : null;

  return (
    <div className="table-container">
      {/* History Drawer Button */}
      <div style={{ position: 'absolute', top: '10px', right: '15px', zIndex: 80 }}>
        <button
          className="btn-nav"
          style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? '❌ Close Log' : '📜 Trick Log'}
        </button>
      </div>

      {/* History Modal Drawer */}
      {showHistory && (
        <div
          style={{
            position: 'absolute',
            top: '45px',
            right: '15px',
            background: 'rgba(10, 30, 18, 0.95)',
            backdropFilter: 'blur(12px)',
            border: '1px solid #e5b94c',
            borderRadius: '12px',
            padding: '1rem',
            maxWidth: '320px',
            maxHeight: '300px',
            overflowY: 'auto',
            zIndex: 90,
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
          }}
        >
          <h4 style={{ color: '#e5b94c', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
            📜 Round Trick Log ({trick_history.length} played)
          </h4>
          {trick_history.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: '0.8rem' }}>No tricks completed yet this round.</p>
          ) : (
            trick_history.map((trick, tIdx) => {
              const winner = players.find((p) => p.player_id === trick.winner_id);
              return (
                <div
                  key={tIdx}
                  style={{
                    marginBottom: '0.6rem',
                    paddingBottom: '0.4rem',
                    borderBottom: '1px solid rgba(255,255,255,0.1)',
                    fontSize: '0.8rem',
                  }}
                >
                  <div style={{ color: '#4ade80', fontWeight: 600 }}>
                    Trick #{tIdx + 1}: Winner {winner?.name || trick.winner_id}
                  </div>
                  <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.2rem' }}>
                    {trick.cards_played.map((p, cIdx) => {
                      const pPlayer = players.find((pl) => pl.player_id === p.player_id);
                      return (
                        <span key={cIdx} style={{ color: '#cbd5e1' }}>
                          {pPlayer?.name}: {p.card.symbol}{p.card.suit[0]}
                        </span>
                      );
                    })}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Opponents Row */}
      <div className="opponents-row">
        {botPlayers.map((bot, idx) => {
          const isActive = current_turn_id === bot.player_id && phase === 'PLAYING';
          const avatar = BOT_AVATARS[idx % BOT_AVATARS.length];

          return (
            <div
              key={bot.player_id}
              className={`seat ${isActive ? 'active-turn' : ''}`}
            >
              <div className="seat-avatar">{avatar}</div>
              <div className="seat-name">{bot.name}</div>
              <div className="seat-stats">
                <span className="stat-badge">Bid: {bot.bid !== null ? bot.bid : '?'}</span>
                <span className="stat-badge">Won: {bot.tricks_won}</span>
                <span
                  className="stat-badge"
                  style={bot.has_exact_bonus ? { borderColor: '#4ade80', color: '#4ade80', fontWeight: 700 } : {}}
                >
                  Pts: {bot.score} {bot.has_exact_bonus ? '🌟' : ''}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Center Trick Table */}
      <div className="center-trick-area">
        <div className="felt-ring" />

        {/* Winner Banner */}
        {displayTrick?.is_complete && trickWinnerPlayer && (
          <div
            style={{
              marginBottom: '0.75rem',
              padding: '0.4rem 1.2rem',
              background: 'rgba(229, 185, 76, 0.95)',
              color: '#000',
              fontWeight: 800,
              borderRadius: '20px',
              fontSize: '0.95rem',
              boxShadow: '0 0 15px rgba(229, 185, 76, 0.6)',
              zIndex: 30,
              animation: 'pulse 1.5s infinite',
            }}
          >
            🏆 {trickWinnerPlayer.name} won the trick!
          </div>
        )}

        <div className="trick-cards-grid">
          {displayTrick && displayTrick.cards_played && displayTrick.cards_played.length > 0 ? (
            displayTrick.cards_played.map((play, idx) => {
              const player = players.find((p) => p.player_id === play.player_id);
              const isWinner = displayTrick.is_complete && displayTrick.winner_id === play.player_id;

              return (
                <div
                  key={idx}
                  className="played-card-wrapper"
                  style={isWinner ? { transform: 'scale(1.08)', zIndex: 20 } : {}}
                >
                  <span
                    className="played-by-label"
                    style={isWinner ? { color: '#4ade80', fontWeight: 800 } : {}}
                  >
                    {player ? player.name : play.player_id} {isWinner ? '👑' : ''}
                  </span>
                  <CardUnit card={play.card} isClickable={false} />
                </div>
              );
            })
          ) : (
            <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontStyle: 'italic', fontSize: '0.95rem' }}>
              {phase === 'PLAYING' ? 'Waiting for lead card...' : 'Round Bidding Phase...'}
            </div>
          )}
        </div>

        {phase === 'ROUND_OVER' && (
          <button
            className="btn-primary"
            style={{ marginTop: '1.5rem', width: 'auto', zIndex: 50 }}
            onClick={onAdvanceRound}
          >
            ➡️ Advance to Next Round ({hand_size - 1} Cards)
          </button>
        )}

        {phase === 'GAME_OVER' && (
          <div style={{ marginTop: '1.5rem', zIndex: 50 }}>
            <h2 style={{ color: '#e5b94c', marginBottom: '0.5rem' }}>🏆 GAME OVER!</h2>
            <p>Check the scoreboard for final rankings!</p>
          </div>
        )}
      </div>

      {/* Bottom Area (Human Player) */}
      <div className="player-bottom-area">
        {isHumanTurn && <div className="turn-notification">⚡ YOUR TURN TO PLAY!</div>}

        <div
          className={`seat ${isHumanTurn ? 'active-turn' : ''}`}
          style={{ width: 'auto', minWidth: '240px', padding: '0.5rem 1.5rem' }}
        >
          <div className="seat-name">{humanPlayer.name} (You)</div>
          <div className="seat-stats">
            <span className="stat-badge">Bid: {humanPlayer.bid !== null ? humanPlayer.bid : '?'}</span>
            <span className="stat-badge">Won: {humanPlayer.tricks_won}</span>
            <span
              className="stat-badge"
              style={humanPlayer.has_exact_bonus ? { borderColor: '#4ade80', color: '#4ade80', fontWeight: 700 } : {}}
            >
              Score: {humanPlayer.score} {humanPlayer.has_exact_bonus ? '🌟 (+10)' : ''}
            </span>
          </div>
        </div>

        <div className="player-hand-flex">
          {humanPlayer.hand && humanPlayer.hand.length > 0 ? (
            humanPlayer.hand.map((card, idx) => (
              <CardUnit
                key={idx}
                card={card}
                disabled={!isHumanTurn}
                onClick={() => onPlayCard(card)}
              />
            ))
          ) : (
            <div style={{ color: '#94a3b8' }}>No cards in hand</div>
          )}
        </div>
      </div>
    </div>
  );
}

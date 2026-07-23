import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SetupScreen from './components/SetupScreen';
import GameBoard from './components/GameBoard';
import BidModal from './components/BidModal';
import ScoreboardModal from './components/ScoreboardModal';
import RulesModal from './components/RulesModal';
import * as api from './services/api';

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [showScoreboard, setShowScoreboard] = useState(false);
  const [showRules, setShowRules] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Poll / step AI turns sequentially
  useEffect(() => {
    if (!sessionId || !gameState) return;

    // Auto-step AI turns sequentially if currently AI's turn in playing phase
    const isAITurn =
      gameState.phase === 'PLAYING' &&
      gameState.current_turn_id !== gameState.players[0]?.player_id;

    const timer = setTimeout(async () => {
      try {
        if (isAITurn) {
          const updatedState = await api.stepAITurn(sessionId);
          setGameState(updatedState);
        } else {
          const updatedState = await api.fetchGameState(sessionId);
          setGameState(updatedState);
        }
      } catch (err) {
        // Silently skip transient polling errors
      }
    }, isAITurn ? 750 : 1200);

    return () => clearTimeout(timer);
  }, [sessionId, gameState]);

  const handleStartGame = async (playerCount, playerName, difficulty) => {
    try {
      setErrorMsg(null);
      const state = await api.createGame(playerCount, playerName, difficulty);
      setSessionId(state.session_id);
      setGameState(state);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to connect to backend server. Make sure Django is running!');
    }
  };

  const handleSelectBid = async (bid) => {
    if (!sessionId) return;
    try {
      setErrorMsg(null);
      const updatedState = await api.submitBid(sessionId, bid);
      setGameState(updatedState);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  const handlePlayCard = async (card) => {
    if (!sessionId) return;
    try {
      setErrorMsg(null);
      const updatedState = await api.playCard(sessionId, card.suit, card.rank);
      setGameState(updatedState);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  const handleAdvanceRound = async () => {
    if (!sessionId) return;
    try {
      setErrorMsg(null);
      const updatedState = await api.advanceRound(sessionId);
      setGameState(updatedState);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  const handleNewGame = () => {
    setSessionId(null);
    setGameState(null);
    setErrorMsg(null);
  };

  const humanPlayer = gameState?.players?.[0];
  const isHumanBiddingTurn =
    gameState?.phase === 'BIDDING' && gameState?.bidding_turn_id === humanPlayer?.player_id;
  const currentBiddingPlayer = gameState?.players?.find(
    (p) => p.player_id === gameState?.bidding_turn_id
  );

  return (
    <div className="app-container">
      <Navbar
        gameState={gameState}
        onOpenScoreboard={() => setShowScoreboard(true)}
        onOpenRules={() => setShowRules(true)}
        onNewGame={handleNewGame}
      />

      {errorMsg && (
        <div
          style={{
            background: '#ef4444',
            color: '#fff',
            padding: '0.6rem 1rem',
            textAlign: 'center',
            fontSize: '0.9rem',
            fontWeight: 600,
          }}
        >
          ⚠️ {errorMsg}
        </div>
      )}

      {!gameState ? (
        <SetupScreen onStartGame={handleStartGame} />
      ) : (
        <GameBoard
          gameState={gameState}
          onPlayCard={handlePlayCard}
          onAdvanceRound={handleAdvanceRound}
        />
      )}

      {/* Sequential Non-Blocking Bidding Toolbar */}
      {gameState && gameState.phase === 'BIDDING' && (
        <BidModal
          handSize={gameState.hand_size}
          biddingPlayerName={currentBiddingPlayer ? currentBiddingPlayer.name : 'Bot'}
          isHumanTurn={isHumanBiddingTurn}
          onSelectBid={handleSelectBid}
        />
      )}

      {/* Scoreboard Modal */}
      {showScoreboard && (
        <ScoreboardModal
          gameState={gameState}
          onClose={() => setShowScoreboard(false)}
        />
      )}

      {/* Rules Modal */}
      {showRules && (
        <RulesModal onClose={() => setShowRules(false)} />
      )}
    </div>
  );
}

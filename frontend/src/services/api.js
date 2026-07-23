/**
 * API service for communicating with Duck Django REST Backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export async function createGame(playerCount = 4, playerName = 'You', difficulty = 'Medium') {
  const res = await fetch(`${API_BASE_URL}/game/new/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_count: playerCount, player_name: playerName, difficulty }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to create game session');
  }
  return await res.json();
}

export async function fetchGameState(sessionId) {
  const res = await fetch(`${API_BASE_URL}/game/${sessionId}/`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to fetch game state');
  }
  return await res.json();
}

export async function submitBid(sessionId, bid) {
  const res = await fetch(`${API_BASE_URL}/game/${sessionId}/bid/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bid: Number(bid) }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to submit bid');
  }
  return await res.json();
}

export async function playCard(sessionId, cardSuit, cardRank) {
  const res = await fetch(`${API_BASE_URL}/game/${sessionId}/play/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suit: cardSuit, rank: cardRank }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to play card');
  }
  return await res.json();
}

export async function stepAITurn(sessionId) {
  const res = await fetch(`${API_BASE_URL}/game/${sessionId}/step_ai/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to step AI turn');
  }
  return await res.json();
}

export async function advanceRound(sessionId) {
  const res = await fetch(`${API_BASE_URL}/game/${sessionId}/next_round/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to advance round');
  }
  return await res.json();
}

import React from 'react';

const SUIT_SYMBOLS = {
  Spades: '♠',
  Hearts: '♥',
  Diamonds: '♦',
  Clubs: '♣',
};

export default function CardUnit({ card, onClick, disabled, isClickable = true }) {
  if (!card) return null;

  const suitClass = card.suit ? card.suit.toLowerCase() : 'spades';
  const symbol = SUIT_SYMBOLS[card.suit] || '♠';

  return (
    <div
      className={`card-unit ${suitClass} ${disabled ? 'disabled' : ''} ${
        isClickable && !disabled ? 'clickable' : ''
      }`}
      onClick={() => {
        if (!disabled && onClick) onClick(card);
      }}
    >
      <div className="card-top">
        <span className="card-rank">{card.symbol}</span>
        <span className="card-suit-symbol">{symbol}</span>
      </div>

      <div className="card-center-symbol">{symbol}</div>

      <div className="card-bottom">
        <span className="card-rank">{card.symbol}</span>
        <span className="card-suit-symbol">{symbol}</span>
      </div>
    </div>
  );
}

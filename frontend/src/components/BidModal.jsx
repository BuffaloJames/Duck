import React from 'react';

export default function BidModal({ handSize, biddingPlayerName, isHumanTurn, onSelectBid }) {
  const bidOptions = Array.from({ length: handSize + 1 }, (_, i) => i);

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '160px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: 'rgba(15, 34, 23, 0.95)',
        backdropFilter: 'blur(12px)',
        border: '2px solid #e5b94c',
        borderRadius: '20px',
        padding: '1.25rem 2rem',
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.7)',
        zIndex: 150,
        textAlign: 'center',
        maxWidth: '90vw',
      }}
    >
      <h3 style={{ color: '#e5b94c', fontSize: '1.25rem', marginBottom: '0.4rem' }}>
        {isHumanTurn ? '🎯 Select Your Bid Prediction' : `⏳ Waiting for ${biddingPlayerName} to bid...`}
      </h3>

      <p style={{ color: '#cbd5e1', fontSize: '0.85rem', marginBottom: '0.85rem' }}>
        Look at your cards below! Exact prediction awards <strong>+10 Bonus Points</strong>.
      </p>

      {isHumanTurn ? (
        <div style={{ display: 'flex', gap: '0.6rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          {bidOptions.map((bid) => (
            <button
              key={bid}
              className="btn-bid"
              style={{ width: '48px', height: '48px', padding: 0 }}
              onClick={() => onSelectBid(bid)}
            >
              {bid}
            </button>
          ))}
        </div>
      ) : (
        <div style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.9rem' }}>
          Bids are made sequentially in turn order...
        </div>
      )}
    </div>
  );
}

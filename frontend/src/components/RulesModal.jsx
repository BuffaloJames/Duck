import React from 'react';

export default function RulesModal({ onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        style={{ maxWidth: '640px', textAlign: 'left', maxHeight: '85vh', overflowY: 'auto' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="modal-title" style={{ textAlign: 'center' }}>📜 Duck Game Rules</h2>

        <div style={{ lineHeight: '1.6', color: '#cbd5e1', fontSize: '0.95rem' }}>
          <h3 style={{ color: '#e5b94c', marginTop: '1rem', marginBottom: '0.3rem' }}>
            1. Objective & Hand Sizes
          </h3>
          <p>
            Compete across <strong>7 rounds</strong> to accurately predict and win an exact number of tricks.
            Round 1 starts with <strong>7 cards</strong> per player, decreasing by 1 card each round down to 1 card in Round 7.
          </p>

          <h3 style={{ color: '#e5b94c', marginTop: '1rem', marginBottom: '0.3rem' }}>
            2. Permanent Trump Suit
          </h3>
          <p>
            <strong>Spades (♠)</strong> serve as the permanent trump suit in every round. High Spades win over non-trump suits regardless of rank.
          </p>

          <h3 style={{ color: '#e5b94c', marginTop: '1rem', marginBottom: '0.3rem' }}>
            3. Sequential Bidding Phase
          </h3>
          <p>
            Review your dealt hand, then each player bids in order (starting to the left of dealer, dealer bidding last) to predict exactly how many tricks they will win (0 to hand size). Unrestricted bidding applies.
          </p>

          <h3 style={{ color: '#e5b94c', marginTop: '1rem', marginBottom: '0.3rem' }}>
            4. Trick-Taking Rules
          </h3>
          <p>
            Player to the left of dealer leads the first trick. Winner of each trick leads the next trick.
          </p>
          <ul style={{ paddingLeft: '1.2rem', marginTop: '0.3rem' }}>
            <li>You <strong>must follow the lead suit</strong> if you hold matching cards.</li>
            <li>If void in the lead suit, you may play a Spade (trump) or discard any other suit.</li>
            <li>Highest card of lead suit wins, unless a Spade is played. Highest Spade wins.</li>
          </ul>

          <h3 style={{ color: '#e5b94c', marginTop: '1rem', marginBottom: '0.3rem' }}>
            5. Scoring & The +10 Bonus
          </h3>
          <ul style={{ paddingLeft: '1.2rem', marginTop: '0.3rem' }}>
            <li><strong>+1 point</strong> for every trick won in the round.</li>
            <li>
              <strong style={{ color: '#4ade80' }}>+10 BONUS POINTS</strong> if your total tricks won matches your exact prediction bid!
            </li>
          </ul>
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <button
            className="btn-primary"
            style={{ width: 'auto', padding: '0.6rem 2.5rem' }}
            onClick={onClose}
          >
            Got It! Let's Play
          </button>
        </div>
      </div>
    </div>
  );
}

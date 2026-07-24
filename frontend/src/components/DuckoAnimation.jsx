import React, { useEffect } from 'react';

export default function DuckoAnimation({ playerName, onComplete }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      if (onComplete) onComplete();
    }, 1800);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="ducko-overlay">
      <div className="ducko-text-container">
        <h1 className="ducko-title">DUCKO! 🦆</h1>
        <p className="ducko-subtitle">
          {playerName} bid 0 & won 0 tricks! Perfect Ducko!
        </p>
      </div>

      <div className="ducko-flying-wrapper">
        <div className="ducko-flying-svg-container">
          <svg
            className="ducko-svg"
            viewBox="0 0 120 80"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Duck Body */}
            <path
              d="M20 45 C 30 30, 60 30, 80 40 C 95 42, 105 35, 100 25 C 95 18, 85 20, 80 25 C 75 22, 60 25, 45 35 C 30 40, 20 45, 20 45 Z"
              fill="#e5b94c"
            />
            {/* Duck Head & Neck */}
            <circle cx="88" cy="24" r="11" fill="#1e5c3c" />
            {/* Duck Eye */}
            <circle cx="91" cy="22" r="2" fill="#ffffff" />
            <circle cx="91.5" cy="22" r="1" fill="#000000" />
            {/* Duck Beak */}
            <path d="M97 24 L 112 26 L 97 29 Z" fill="#f97316" />
            {/* Duck Tail Feathers */}
            <path d="M15 42 L 5 35 L 18 47 Z" fill="#ca8a04" />
            {/* Flapping Top Wing */}
            <g className="ducko-wing-top">
              <path
                d="M45 36 C 40 10, 65 5, 75 30 Z"
                fill="#fef08a"
                stroke="#e5b94c"
                strokeWidth="2"
              />
            </g>
            {/* Flapping Bottom Wing */}
            <g className="ducko-wing-bottom">
              <path
                d="M42 38 C 35 55, 60 65, 70 42 Z"
                fill="#ca8a04"
                stroke="#a16207"
                strokeWidth="2"
              />
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
}

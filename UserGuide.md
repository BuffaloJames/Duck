# Duck Card Game - User Guide

Welcome to **Duck**, the strategic trick-taking card game!

---

## Game Overview & Rules

In **Duck**, 3 to 7 players compete over 7 rounds to predict and win exact numbers of tricks.

- **Hand Sizes**: Round 1 deals 7 cards. Each subsequent round deals 1 fewer card (7, 6, 5, 4, 3, 2, 1).
- **Trump Suit**: **Spades** are ALWAYS the permanent trump suit.
- **Bidding**: Before play begins, each player predicts exactly how many tricks they will win in that round.
- **Trick-Taking**:
  - The player to the right of the dealer leads first.
  - Players **must follow suit** if possible.
  - If a player cannot follow suit, they may play a Spade (trump) or discard any card.
  - Highest card of the led suit wins, unless a Spade is played. Highest Spade wins.
- **Scoring**:
  - 1 point per trick won.
  - **+10 Bonus Points** if your total tricks won matches your exact bid prediction!

---

## Technical Stack Architecture

- **Core Engine (`duck_engine/`)**: Python domain logic (Strict type hints, Google docstrings, Black formatted, graceful error handling).
- **API Backend (`backend/`)**: Django / Django REST Framework serving local API endpoints.
- **Frontend App (`frontend/`)**: React (Vite) application styled with a Classic Green Felt Casino theme.

---

## Installation & Running Locally

### 1. Backend Setup (Django & Engine)
```bash
# Install dependencies
pip install django djangorestframework pytest pytest-cov black

# Run migrations and start Django server
python manage.py migrate
python manage.py runserver 8000
```

### 2. Testing Core Engine & API
```bash
pytest --cov=duck_engine --cov=duck_api --cov-report=term-missing
```

### 3. Frontend Setup (React)
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` on desktop or mobile browser to play!

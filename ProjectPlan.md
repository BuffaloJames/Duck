# Duck Card Game - Project Plan & Roadmap

## Overview
Duck is a strategic trick-taking card game for 3 to 7 players. Rounds start with hands of 7 cards and decrease down to 1 card. Spades are the permanent trump suit, and exact bid predictions earn a +10 bonus point reward.

---

## Technical Component Architecture & Communication Layer

```
┌─────────────────────────────────────────────────────────────┐
│               Frontend: React Application (Vite)            │
│  - Classic Green Felt Casino UI & Card Animations           │
│  - Bid Modal, Scoreboard Table, Trick Log, Bot Avatars       │
└──────────────────────────────┬──────────────────────────────┘
                               │  REST API Calls (HTTP / JSON)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Backend: Django / Django REST Framework          │
│  - Game session API endpoints (`/api/game/new`, `/play`)     │
│  - Session state persistence & validation                    │
└──────────────────────────────┬──────────────────────────────┘
                               │  Python Engine Import
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Core Engine: `duck_engine/` (Python)          │
│  - Pure domain model (Cards, Decks, Rules, AI Bots)         │
│  - Graceful degradation for bad inputs/illegal plays        │
│  - 100% Type Hints, Google Docstrings, Black Formatted      │
└─────────────────────────────────────────────────────────────┘
```

- **Core Game Engine (`duck_engine/`)**: Python domain logic managing cards, decks, dealing, lead suit validation, spade trump logic, bid prediction recording, trick resolution, AI bot decisions, and score calculations.
- **Backend API (`backend/`)**: Django REST API serving game session state, handling user actions (bids, plays), and controlling bot turns.
- **Frontend App (`frontend/`)**: Modern React (Vite) app styled with a Classic Green Felt Casino aesthetic, smooth card animations, live score table, trick history log, and responsive controls for iMac desktop and iPhone mobile devices.
- **Automated Test Suite (`tests/`)**: PyTest suite targeting >= 80% code coverage across engine and API endpoints.

---

## Phased Implementation Plan

### Phase 1: Core Engine & Test Suite (Python Standards)
- **Deliverables**:
  1. `duck_engine/cards.py`: Card, Deck, and Hand domain classes with type hints and Google docstrings.
  2. `duck_engine/game.py`: Game rules, trick evaluation, bidding, and scoring (+10 exact match bonus) with graceful error handling.
  3. `duck_engine/ai.py`: Bot players with customizable difficulty levels (Easy, Medium, Hard).
  4. `tests/test_duck_engine.py`: PyTest suite verifying rules and edge cases (>=80% coverage).
- **Standards**: Black formatting, strict type hints, Google docstrings, no crashes on invalid inputs.

### Phase 2: Django REST API Communication Layer
- **Deliverables**:
  1. Django backend setup (`backend/` project & `duck_api` app).
  2. REST API endpoints:
     - `POST /api/game/new/`: Start a new game session with configurable AI bots.
     - `GET /api/game/<id>/`: Retrieve current game state (hand, bids, current trick, scores).
     - `POST /api/game/<id>/bid/`: Submit player bid prediction (gracefully handling invalid bids).
     - `POST /api/game/<id>/play/`: Play a card (verifying lead suit rules & executing bot turns).
  3. API Unit & Integration tests (`tests/test_api.py`).

### Phase 3: React Frontend & Classic Green Felt Casino UI
- **Deliverables**:
  1. Modern React frontend (Vite) connecting to the Django API.
  2. Classic Green Felt Casino theme with smooth card deal and trick animations.
  3. Interactive bid selector, card play controls, live scoreboard, and trick history.
  4. Desktop & Mobile responsive layout (ready for iMac VS Code development and future AWS deployment).

---

## Developer Queries & Sign-Off Request

> [!IMPORTANT]
> **User Sign-Off Required**: Please review this updated ProjectPlan.md featuring the Django API backend + React frontend architecture and confirm sign-off to begin Phase 1 execution.

---

## Enhancements Backlog
- AWS Deployment scripts & Docker containerization.
- Multi-player WebSockets for live remote play against family on iPhone.
- Game session history and stats dashboard.

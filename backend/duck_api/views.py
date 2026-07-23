"""Django REST API views for Duck card game session management.

Provides HTTP endpoints to create game sessions, query current game state,
submit bid predictions, play cards, step AI turns, and advance rounds.
"""

import json
import uuid
from typing import Any, Dict, Optional, Tuple

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from duck_engine.ai import AIDifficulty
from duck_engine.cards import Card, Rank, Suit
from duck_engine.game import DuckGameSession, PlayerState

# In-memory storage for active local game sessions
ACTIVE_SESSIONS: Dict[str, DuckGameSession] = {}


def _parse_json_body(
    request: HttpRequest,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse JSON body from HttpRequest safely.

    Args:
        request: The incoming HttpRequest.

    Returns:
        Tuple of (parsed dictionary or None, error message string or None).
    """
    if not request.body:
        return {}, None
    try:
        data = json.loads(request.body.decode("utf-8"))
        if not isinstance(data, dict):
            return None, "Request payload must be a JSON object."
        return data, None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "Invalid JSON payload."


@csrf_exempt
def create_game_view(request: HttpRequest) -> JsonResponse:
    """Create a new Duck game session.

    Args:
        request: HttpRequest with optional JSON payload (player_count, player_name, difficulty).

    Returns:
        JsonResponse containing session_id and initial game state, or error message.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    data, err = _parse_json_body(request)
    if err or data is None:
        return JsonResponse({"error": err or "Invalid payload."}, status=400)

    try:
        player_count = int(data.get("player_count", 4))
    except (ValueError, TypeError):
        player_count = 4

    if not (3 <= player_count <= 7):
        return JsonResponse(
            {"error": "Player count must be between 3 and 7."}, status=400
        )

    player_name = str(data.get("player_name", "You")).strip() or "You"
    diff_str = str(data.get("difficulty", "Medium")).capitalize()

    try:
        difficulty = AIDifficulty(diff_str)
    except ValueError:
        difficulty = AIDifficulty.MEDIUM

    human_player = PlayerState(
        player_id="p1", name=player_name, is_human=True, difficulty=difficulty
    )
    players = [human_player]

    bot_names = ["Quacky", "Mallard", "Donald", "Daphne", "Feathers", "Webfoot"]
    for i in range(2, player_count + 1):
        bot_name = bot_names[(i - 2) % len(bot_names)]
        players.append(
            PlayerState(
                player_id=f"p{i}",
                name=bot_name,
                is_human=False,
                difficulty=difficulty,
            )
        )

    session_id = str(uuid.uuid4())
    session = DuckGameSession(players)
    ACTIVE_SESSIONS[session_id] = session

    state = session.get_state_dict(for_player_id="p1")
    state["session_id"] = session_id

    return JsonResponse(state, status=201)


@csrf_exempt
def game_detail_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """Retrieve current game state for a session.

    Args:
        request: HttpRequest object.
        session_id: Unique session identifier.

    Returns:
        JsonResponse containing current game state or 404 error.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed. Use GET."}, status=405)

    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return JsonResponse({"error": "Game session not found."}, status=404)

    state = session.get_state_dict(for_player_id="p1")
    state["session_id"] = session_id
    return JsonResponse(state, status=200)


@csrf_exempt
def submit_bid_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """Submit bid prediction for human player in session.

    Args:
        request: HttpRequest containing bid JSON payload.
        session_id: Unique session identifier.

    Returns:
        JsonResponse with updated game state or error details.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return JsonResponse({"error": "Game session not found."}, status=404)

    data, err = _parse_json_body(request)
    if err or data is None:
        return JsonResponse({"error": err or "Invalid payload."}, status=400)

    try:
        bid = int(data.get("bid"))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Bid must be an integer."}, status=400)

    success, msg = session.submit_bid("p1", bid)
    if not success:
        return JsonResponse({"error": msg}, status=400)

    state = session.get_state_dict(for_player_id="p1")
    state["session_id"] = session_id
    return JsonResponse(state, status=200)


@csrf_exempt
def play_card_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """Play a card for human player in current trick.

    Args:
        request: HttpRequest containing suit and rank JSON payload.
        session_id: Unique session identifier.

    Returns:
        JsonResponse with updated game state or error details.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return JsonResponse({"error": "Game session not found."}, status=404)

    data, err = _parse_json_body(request)
    if err or data is None:
        return JsonResponse({"error": err or "Invalid payload."}, status=400)

    suit_val = data.get("suit")
    rank_val = data.get("rank")

    if not suit_val or rank_val is None:
        return JsonResponse({"error": "Card suit and rank are required."}, status=400)

    try:
        card_suit = Suit(str(suit_val))
        card_rank = Rank(int(rank_val))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid card suit or rank value."}, status=400)

    target_card = Card(card_suit, card_rank)
    success, msg = session.play_card("p1", target_card)
    if not success:
        return JsonResponse({"error": msg}, status=400)

    state = session.get_state_dict(for_player_id="p1")
    state["session_id"] = session_id
    return JsonResponse(state, status=200)


@csrf_exempt
def step_ai_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """Execute a single AI turn if currently an AI bot's turn.

    Args:
        request: HttpRequest object.
        session_id: Unique session identifier.

    Returns:
        JsonResponse with updated game state.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return JsonResponse({"error": "Game session not found."}, status=404)

    stepped = session.step_single_ai_turn()
    state = session.get_state_dict(for_player_id="p1")
    state["session_id"] = session_id
    state["ai_stepped"] = stepped
    return JsonResponse(state, status=200)


@csrf_exempt
def advance_round_view(request: HttpRequest, session_id: str) -> JsonResponse:
    """Advance game session to next round after round completion.

    Args:
        request: HttpRequest object.
        session_id: Unique session identifier.

    Returns:
        JsonResponse with updated game state or error details.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return JsonResponse({"error": "Game session not found."}, status=404)

    success, msg = session.advance_to_next_round()
    if not success:
        return JsonResponse({"error": msg}, status=400)

    state = session.get_state_dict(for_player_id="p1")
    state["session_id"] = session_id
    return JsonResponse(state, status=200)

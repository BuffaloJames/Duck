"""Duck card game engine logic.

Manages player hands, turn-by-turn bidding phases, sequential trick resolution,
transparent score calculations, and round progression from 7 cards down to 1 card.
"""

from typing import Any, Dict, List, Optional, Tuple

from duck_engine.ai import AIDifficulty, calculate_ai_bid, select_ai_card_play
from duck_engine.cards import Card, Deck, Hand, Suit


class PlayerState:
    """Represents state of an individual player in a Duck game."""

    def __init__(
        self,
        player_id: str,
        name: str,
        is_human: bool = False,
        difficulty: AIDifficulty = AIDifficulty.MEDIUM,
    ) -> None:
        """Initialize player state.

        Args:
            player_id: Unique identifier for player.
            name: Display name.
            is_human: True if human player, False if AI.
            difficulty: AI difficulty setting if bot.
        """
        self.player_id: str = player_id
        self.name: str = name
        self.is_human: bool = is_human
        self.difficulty: AIDifficulty = difficulty
        self.hand: Hand = Hand()
        self.current_bid: Optional[int] = None
        self.tricks_won: int = 0
        self.cumulative_score: int = 0

    def commit_round_score(self) -> None:
        """Commit current round points into cumulative score before resetting round."""
        self.cumulative_score += self.current_round_points

    def reset_for_round(self) -> None:
        """Reset player bid and tricks won for a new round."""
        self.hand = Hand()
        self.current_bid = None
        self.tricks_won = 0

    @property
    def has_exact_bonus(self) -> bool:
        """Check if player matched their exact prediction bid."""
        return self.current_bid is not None and self.tricks_won == self.current_bid

    @property
    def current_round_points(self) -> int:
        """Calculate points earned so far in current round including bonus."""
        pts = self.tricks_won
        if self.has_exact_bonus:
            pts += 10
        return pts

    @property
    def total_score(self) -> int:
        """Calculate overall total score (cumulative from past rounds + current round)."""
        return self.cumulative_score + self.current_round_points

    @property
    def score(self) -> int:
        """Alias property for total_score."""
        return self.total_score

    def to_dict(self, reveal_hand: bool = True) -> Dict[str, Any]:
        """Convert player state to dictionary.

        Args:
            reveal_hand: True to include full card details, False to hide.

        Returns:
            Dictionary with player information.
        """
        return {
            "player_id": self.player_id,
            "name": self.name,
            "is_human": self.is_human,
            "difficulty": self.difficulty.value,
            "hand_count": len(self.hand.cards),
            "hand": self.hand.to_dict_list() if reveal_hand else [],
            "bid": self.current_bid,
            "tricks_won": self.tricks_won,
            "cumulative_score": self.cumulative_score,
            "current_round_points": self.current_round_points,
            "score": self.total_score,
            "has_exact_bonus": self.has_exact_bonus,
        }


class TrickState:
    """Represents a single trick played in a round."""

    def __init__(self, leader_id: str) -> None:
        """Initialize trick state.

        Args:
            leader_id: Player ID leading this trick.
        """
        self.leader_id: str = leader_id
        self.lead_suit: Optional[Suit] = None
        self.cards_played: List[Tuple[str, Card]] = []
        self.winner_id: Optional[str] = None
        self.is_complete: bool = False

    def add_play(self, player_id: str, card: Card) -> None:
        """Add card play to trick.

        Args:
            player_id: Player playing the card.
            card: Card played.
        """
        if not self.lead_suit:
            self.lead_suit = card.suit
        self.cards_played.append((player_id, card))

    def evaluate_winner(self) -> Optional[str]:
        """Determine winner of the trick according to Duck rules.

        Spades are permanent trump. Highest Spade wins if played.
        Otherwise, highest card of lead suit wins.

        Returns:
            Winning player_id string, or None if trick empty.
        """
        if not self.cards_played:
            return None

        spade_plays = [
            (pid, c) for pid, c in self.cards_played if c.suit == Suit.SPADES
        ]
        if spade_plays:
            winner = max(spade_plays, key=lambda item: item[1].value)
            self.winner_id = winner[0]
            self.is_complete = True
            return winner[0]

        lead_plays = [
            (pid, c) for pid, c in self.cards_played if c.suit == self.lead_suit
        ]
        if lead_plays:
            winner = max(lead_plays, key=lambda item: item[1].value)
            self.winner_id = winner[0]
            self.is_complete = True
            return winner[0]

        self.winner_id = self.cards_played[0][0]
        self.is_complete = True
        return self.winner_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert trick state to dictionary representation.

        Returns:
            Dictionary with trick information.
        """
        return {
            "leader_id": self.leader_id,
            "lead_suit": self.lead_suit.value if self.lead_suit else None,
            "cards_played": [
                {"player_id": pid, "card": c.to_dict()} for pid, c in self.cards_played
            ],
            "winner_id": self.winner_id,
            "is_complete": self.is_complete,
        }


class DuckGameSession:
    """Manages complete Duck game session across 7 shrinking rounds."""

    def __init__(self, players: List[PlayerState]) -> None:
        """Initialize game session with list of players.

        Args:
            players: List of 3 to 7 PlayerState instances.

        Raises:
            ValueError: If player count is not between 3 and 7.
        """
        if not (3 <= len(players) <= 7):
            raise ValueError("Duck game requires 3 to 7 players.")

        self.players: List[PlayerState] = players
        self.player_map: Dict[str, PlayerState] = {p.player_id: p for p in players}
        self.current_round: int = 1
        self.max_rounds: int = 7
        self.hand_size: int = 7
        self.dealer_idx: int = 0
        self.bidding_turn_idx: int = 0
        self.current_turn_idx: int = 0
        self.phase: str = "BIDDING"  # BIDDING, PLAYING, ROUND_OVER, GAME_OVER
        self.current_trick: Optional[TrickState] = None
        self.last_completed_trick: Optional[TrickState] = None
        self.trick_history: List[Dict[str, Any]] = []

        self.start_new_round(is_first_round=True)

    def start_new_round(self, is_first_round: bool = False) -> None:
        """Initialize state for a new round and deal cards."""
        self.hand_size = (
            8 - self.current_round
        )  # Round 1=7 cards down to Round 7=1 card

        deck = Deck()
        for p in self.players:
            if not is_first_round:
                p.commit_round_score()
            p.reset_for_round()
            p.hand = Hand(deck.deal(self.hand_size))

        # First to bid & lead is player to left of dealer ((dealer_idx + 1) % len)
        first_bidder_idx = (self.dealer_idx + 1) % len(self.players)
        self.bidding_turn_idx = first_bidder_idx
        self.current_turn_idx = first_bidder_idx
        self.phase = "BIDDING"
        self.current_trick = None
        self.last_completed_trick = None
        self.trick_history = []

        # Auto-process AI bids up to first human turn or all bids
        self._process_ai_bids_sequential()

    def _process_ai_bids_sequential(self) -> None:
        """Process AI bids in turn order until reaching human turn or finishing bidding."""
        while self.phase == "BIDDING":
            current_bidder = self.players[self.bidding_turn_idx]
            if current_bidder.is_human and current_bidder.current_bid is None:
                # Pause for human bid input
                break

            if current_bidder.current_bid is None:
                current_bidder.current_bid = calculate_ai_bid(
                    current_bidder.hand, self.hand_size, current_bidder.difficulty
                )

            # Move to next bidder clockwise
            self.bidding_turn_idx = (self.bidding_turn_idx + 1) % len(self.players)

            # Check if all players have bid
            if all(p.current_bid is not None for p in self.players):
                self._start_playing_phase()
                break

    def submit_bid(self, player_id: str, bid: int) -> Tuple[bool, str]:
        """Submit a bid prediction for a player safely.

        Args:
            player_id: Player submitting bid.
            bid: Number of predicted tricks won.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if self.phase != "BIDDING":
            return False, "Not currently in bidding phase."

        current_bidder = self.players[self.bidding_turn_idx]
        if current_bidder.player_id != player_id:
            return False, f"Not {player_id}'s turn to bid."

        if not (0 <= bid <= self.hand_size):
            return False, f"Bid must be between 0 and {self.hand_size}."

        current_bidder.current_bid = bid
        self.bidding_turn_idx = (self.bidding_turn_idx + 1) % len(self.players)

        if all(p.current_bid is not None for p in self.players):
            self._start_playing_phase()
        else:
            self._process_ai_bids_sequential()

        return True, "Bid recorded successfully."

    def _start_playing_phase(self) -> None:
        """Transition from bidding to trick playing phase."""
        self.phase = "PLAYING"
        leader_idx = (self.dealer_idx + 1) % len(self.players)
        self.current_turn_idx = leader_idx
        self.current_trick = TrickState(self.players[leader_idx].player_id)
        self.last_completed_trick = None

    def play_card(self, player_id: str, card: Card) -> Tuple[bool, str]:
        """Play a card for the specified player safely.

        Args:
            player_id: Player attempting card play.
            card: Card instance to play.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if self.phase != "PLAYING" or not self.current_trick:
            return False, "Not currently in playing phase."

        expected_player = self.players[self.current_turn_idx]
        if expected_player.player_id != player_id:
            return False, f"Not {player_id}'s turn."

        legal_cards = expected_player.hand.get_legal_plays(self.current_trick.lead_suit)
        if card not in legal_cards:
            return False, "Illegal move. You must follow suit if possible."

        # Execute play
        expected_player.hand.remove_card(card)
        self.current_trick.add_play(player_id, card)

        # Move turn to next player clockwise
        self.current_turn_idx = (self.current_turn_idx + 1) % len(self.players)

        # If all players have played card, resolve trick
        if len(self.current_trick.cards_played) == len(self.players):
            winner_id = self.current_trick.evaluate_winner()
            if winner_id and winner_id in self.player_map:
                self.player_map[winner_id].tricks_won += 1

            self.last_completed_trick = self.current_trick
            self.trick_history.append(self.current_trick.to_dict())

            # Check if round is over (hands empty)
            if all(len(p.hand.cards) == 0 for p in self.players):
                self._finish_round()
            else:
                # Next trick led by winner of current trick
                winner_idx = next(
                    i for i, p in enumerate(self.players) if p.player_id == winner_id
                )
                self.current_turn_idx = winner_idx
                self.current_trick = TrickState(winner_id)

        return True, "Card played successfully."

    def step_single_ai_turn(self) -> bool:
        """Step exactly one AI turn if it is currently an AI's turn to play.

        Returns:
            True if an AI turn was taken, False otherwise.
        """
        if (
            self.phase != "PLAYING"
            or not self.current_trick
            or self.players[self.current_turn_idx].is_human
        ):
            return False

        bot = self.players[self.current_turn_idx]
        chosen_card = select_ai_card_play(
            hand=bot.hand,
            lead_suit=self.current_trick.lead_suit,
            current_trick=self.current_trick.cards_played,
            tricks_won=bot.tricks_won,
            bid=bot.current_bid if bot.current_bid is not None else 0,
            hand_size=self.hand_size,
            difficulty=bot.difficulty,
        )
        if chosen_card:
            success, _ = self.play_card(bot.player_id, chosen_card)
            return success
        return False

    def _finish_round(self) -> None:
        """Complete current round and set phase."""
        if self.current_round >= self.max_rounds:
            # Commit final round scores for game over
            for p in self.players:
                p.commit_round_score()
            self.phase = "GAME_OVER"
        else:
            self.phase = "ROUND_OVER"

    def advance_to_next_round(self) -> Tuple[bool, str]:
        """Advance game to next round after ROUND_OVER phase.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if self.phase != "ROUND_OVER":
            return False, "Round is not over yet."

        self.current_round += 1
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        self.start_new_round(is_first_round=False)
        return True, f"Advanced to round {self.current_round}."

    def get_state_dict(self, for_player_id: str) -> Dict[str, Any]:
        """Get game state dictionary sanitized for a specific viewing player.

        Args:
            for_player_id: Player ID requesting state.

        Returns:
            JSON-serializable dictionary representation of game state.
        """
        current_trick_data = (
            self.current_trick.to_dict() if self.current_trick else None
        )
        last_completed_trick_data = (
            self.last_completed_trick.to_dict() if self.last_completed_trick else None
        )
        current_turn_player = self.players[self.current_turn_idx]
        bidding_turn_player = self.players[self.bidding_turn_idx]

        return {
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "hand_size": self.hand_size,
            "phase": self.phase,
            "dealer_id": self.players[self.dealer_idx].player_id,
            "bidding_turn_id": bidding_turn_player.player_id,
            "current_turn_id": current_turn_player.player_id,
            "current_trick": current_trick_data,
            "last_completed_trick": last_completed_trick_data,
            "players": [
                p.to_dict(reveal_hand=(p.player_id == for_player_id))
                for p in self.players
            ],
            "trick_history": self.trick_history,
        }

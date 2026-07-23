"""Card, Suit, Rank, Deck, and Hand representations for Duck card game.

Provides data structures for standard 52-card playing deck operations,
hand card management, suit filtering, and legal move validation.
"""

from enum import Enum
import random
from typing import Any, Dict, List, Optional


class Suit(str, Enum):
    """Playing card suits."""

    SPADES = "Spades"
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"


class Rank(int, Enum):
    """Playing card ranks and numeric values."""

    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


RANK_SYMBOLS: Dict[Rank, str] = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A",
}

SYMBOL_TO_RANK: Dict[str, Rank] = {v: k for k, v in RANK_SYMBOLS.items()}


class Card:
    """Represents a single playing card with suit and rank."""

    def __init__(self, suit: Suit, rank: Rank) -> None:
        """Initialize card with suit and rank.

        Args:
            suit: Suit of the card.
            rank: Rank of the card.
        """
        self.suit: Suit = suit
        self.rank: Rank = rank

    @property
    def value(self) -> int:
        """Return numeric value of the card rank."""
        return self.rank.value

    @property
    def symbol(self) -> str:
        """Return rank symbol string (e.g. 'A', 'K', '10')."""
        return RANK_SYMBOLS.get(self.rank, str(self.value))

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to a JSON-serializable dictionary.

        Returns:
            Dictionary with suit, rank value, and symbol.
        """
        return {
            "suit": self.suit.value,
            "rank": self.value,
            "symbol": self.symbol,
            "code": f"{self.symbol}{self.suit.value[0]}",
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Card"]:
        """Construct card from dictionary safely.

        Args:
            data: Dictionary containing suit and rank keys.

        Returns:
            Card instance or None if data invalid.
        """
        if not data or not isinstance(data, dict):
            return None

        suit_val = data.get("suit")
        rank_val = data.get("rank")

        if suit_val is None or rank_val is None:
            return None

        try:
            matched_suit = Suit(suit_val)
            matched_rank = Rank(int(rank_val))
            return cls(matched_suit, matched_rank)
        except (ValueError, TypeError):
            return None

    def __repr__(self) -> str:
        """Return string representation of card."""
        return f"{self.symbol} of {self.suit.value}"

    def __eq__(self, other: Any) -> bool:
        """Check equality between two cards."""
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __lt__(self, other: Any) -> bool:
        """Compare card values."""
        if not isinstance(other, Card):
            return False
        if self.suit != other.suit:
            return self.suit.value < other.suit.value
        return self.value < other.value


class Deck:
    """Standard 52-card playing deck."""

    def __init__(self) -> None:
        """Initialize and shuffle standard 52-card deck."""
        self.cards: List[Card] = [Card(suit, rank) for suit in Suit for rank in Rank]
        self.shuffle()

    def shuffle(self) -> None:
        """Randomly shuffle cards in deck."""
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Card]:
        """Deal specified number of cards from deck.

        Args:
            num_cards: Count of cards to draw.

        Returns:
            List of Card objects popped from deck.
        """
        if num_cards <= 0:
            return []
        count = min(num_cards, len(self.cards))
        dealt: List[Card] = []
        for _ in range(count):
            dealt.append(self.cards.pop())
        return dealt


class Hand:
    """Represents a player's hand of cards."""

    def __init__(self, cards: Optional[List[Card]] = None) -> None:
        """Initialize player hand.

        Args:
            cards: Optional initial list of cards.
        """
        self.cards: List[Card] = list(cards) if cards else []

    def add_card(self, card: Optional[Card]) -> None:
        """Add card to hand.

        Args:
            card: Card to add.
        """
        if card and isinstance(card, Card):
            self.cards.append(card)

    def remove_card(self, card: Optional[Card]) -> bool:
        """Remove card from hand safely.

        Args:
            card: Card to remove.

        Returns:
            True if card was found and removed, False otherwise.
        """
        if not card or card not in self.cards:
            return False
        self.cards.remove(card)
        return True

    def get_legal_plays(self, lead_suit: Optional[Suit]) -> List[Card]:
        """Get legal cards to play given current lead suit.

        Follows suit rule: if player holds lead suit cards, they MUST play
        one of those cards. Otherwise, any card in hand is legal.

        Args:
            lead_suit: Lead suit of the current trick, or None if leading.

        Returns:
            List of legal Card objects.
        """
        if not self.cards:
            return []

        if lead_suit is None:
            return list(self.cards)

        matching_cards = [c for c in self.cards if c.suit == lead_suit]
        if matching_cards:
            return matching_cards

        return list(self.cards)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all cards in hand to list of dictionaries.

        Returns:
            List of card dictionary representations.
        """
        return [c.to_dict() for c in self.cards]

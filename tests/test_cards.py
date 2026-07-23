"""Unit tests for cards module in duck_engine."""

import pytest
from duck_engine.cards import Card, Deck, Hand, Rank, Suit


class TestCard:
    """Tests for Card class."""

    def test_card_initialization_and_properties(self) -> None:
        """Test card initialization, value, and symbol properties."""
        card = Card(Suit.SPADES, Rank.ACE)
        assert card.suit == Suit.SPADES
        assert card.rank == Rank.ACE
        assert card.value == 14
        assert card.symbol == "A"
        assert repr(card) == "A of Spades"

    def test_card_equality_and_comparison(self) -> None:
        """Test card equality and sorting comparison."""
        card1 = Card(Suit.HEARTS, Rank.TEN)
        card2 = Card(Suit.HEARTS, Rank.TEN)
        card3 = Card(Suit.HEARTS, Rank.KING)

        assert card1 == card2
        assert card1 != card3
        assert card1 < card3
        assert not (card1 == "not a card")

    def test_to_and_from_dict(self) -> None:
        """Test dictionary serialization and deserialization."""
        card = Card(Suit.DIAMONDS, Rank.QUEEN)
        data = card.to_dict()

        assert data["suit"] == "Diamonds"
        assert data["rank"] == 12
        assert data["symbol"] == "Q"

        reconstructed = Card.from_dict(data)
        assert reconstructed == card

    def test_from_dict_graceful_failures(self) -> None:
        """Test from_dict handles invalid data gracefully without crashing."""
        assert Card.from_dict(None) is None
        assert Card.from_dict({}) is None
        assert Card.from_dict({"suit": "Invalid", "rank": 10}) is None
        assert Card.from_dict({"suit": "Spades", "rank": "invalid"}) is None


class TestDeck:
    """Tests for Deck class."""

    def test_deck_initialization_and_deal(self) -> None:
        """Test deck creation and card dealing."""
        deck = Deck()
        assert len(deck.cards) == 52

        dealt = deck.deal(7)
        assert len(dealt) == 7
        assert len(deck.cards) == 45

    def test_deal_zero_or_overflow(self) -> None:
        """Test dealing zero or more cards than remaining."""
        deck = Deck()
        assert deck.deal(0) == []

        all_cards = deck.deal(60)
        assert len(all_cards) == 52
        assert len(deck.cards) == 0


class TestHand:
    """Tests for Hand class."""

    def test_add_and_remove_card(self) -> None:
        """Test adding and removing cards from hand."""
        hand = Hand()
        card = Card(Suit.CLUBS, Rank.FIVE)

        hand.add_card(card)
        assert len(hand.cards) == 1
        assert card in hand.cards

        assert hand.remove_card(card) is True
        assert len(hand.cards) == 0

        # Remove non-existent card returns False gracefully
        assert hand.remove_card(card) is False
        assert hand.remove_card(None) is False

    def test_legal_plays_following_suit(self) -> None:
        """Test follow suit rules for legal plays."""
        c1 = Card(Suit.SPADES, Rank.ACE)
        c2 = Card(Suit.HEARTS, Rank.TEN)
        c3 = Card(Suit.HEARTS, Rank.KING)

        hand = Hand([c1, c2, c3])

        # Lead suit is Hearts: must play Hearts
        legal_hearts = hand.get_legal_plays(Suit.HEARTS)
        assert len(legal_hearts) == 2
        assert c2 in legal_hearts and c3 in legal_hearts
        assert c1 not in legal_hearts

        # Lead suit is Clubs (void in hand): any card legal
        legal_clubs = hand.get_legal_plays(Suit.CLUBS)
        assert len(legal_clubs) == 3

        # Lead suit is None (leading trick): any card legal
        legal_lead = hand.get_legal_plays(None)
        assert len(legal_lead) == 3

    def test_empty_hand_legal_plays(self) -> None:
        """Test empty hand returns empty legal plays list."""
        empty_hand = Hand()
        assert empty_hand.get_legal_plays(Suit.SPADES) == []

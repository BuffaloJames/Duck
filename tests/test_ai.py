"""Unit tests for AI strategy module in duck_engine."""

from duck_engine.ai import AIDifficulty, calculate_ai_bid, select_ai_card_play
from duck_engine.cards import Card, Hand, Rank, Suit


class TestAIBidding:
    """Tests for AI bidding logic."""

    def test_calculate_ai_bid_medium(self) -> None:
        """Test bid estimation for medium difficulty."""
        cards = [
            Card(Suit.SPADES, Rank.ACE),  # ~1.0
            Card(Suit.SPADES, Rank.KING),  # ~1.0
            Card(Suit.HEARTS, Rank.ACE),  # ~0.8
            Card(Suit.DIAMONDS, Rank.TWO),  # ~0.0
        ]
        hand = Hand(cards)
        bid = calculate_ai_bid(hand, hand_size=4, difficulty=AIDifficulty.MEDIUM)

        assert 0 <= bid <= 4
        assert bid >= 2  # Strong hand should bid at least 2

    def test_calculate_ai_bid_empty_hand(self) -> None:
        """Test bid calculation on empty hand returns 0 safely."""
        empty_hand = Hand()
        assert calculate_ai_bid(empty_hand, hand_size=5) == 0

    def test_calculate_ai_bid_easy(self) -> None:
        """Test random bid calculation for Easy bot."""
        cards = [Card(Suit.CLUBS, Rank.FIVE), Card(Suit.SPADES, Rank.NINE)]
        hand = Hand(cards)
        bid = calculate_ai_bid(hand, hand_size=2, difficulty=AIDifficulty.EASY)
        assert 0 <= bid <= 2


class TestAICardPlay:
    """Tests for AI card selection logic."""

    def test_select_card_play_single_choice(self) -> None:
        """Test AI selects the only card when hand has 1 card."""
        c1 = Card(Suit.HEARTS, Rank.SEVEN)
        hand = Hand([c1])

        play = select_ai_card_play(
            hand=hand,
            lead_suit=Suit.HEARTS,
            current_trick=[],
            tricks_won=0,
            bid=1,
            hand_size=1,
        )
        assert play == c1

    def test_select_card_play_win_with_spade(self) -> None:
        """Test AI uses spade to trump when needing wins."""
        c_low = Card(Suit.CLUBS, Rank.THREE)
        c_spade = Card(Suit.SPADES, Rank.EIGHT)
        hand = Hand([c_low, c_spade])

        # Opponent led Hearts Ace
        current_trick = [("p1", Card(Suit.HEARTS, Rank.ACE))]

        play = select_ai_card_play(
            hand=hand,
            lead_suit=Suit.HEARTS,
            current_trick=current_trick,
            tricks_won=0,
            bid=1,
            hand_size=2,
            difficulty=AIDifficulty.MEDIUM,
        )
        # Void in Hearts -> Play Spade to win trick
        assert play == c_spade

    def test_select_card_play_avoid_winning(self) -> None:
        """Test AI plays low card to avoid winning when bid already met."""
        c_high = Card(Suit.HEARTS, Rank.KING)
        c_low = Card(Suit.HEARTS, Rank.FOUR)
        hand = Hand([c_high, c_low])

        # Opponent led Hearts Nine
        current_trick = [("p1", Card(Suit.HEARTS, Rank.NINE))]

        play = select_ai_card_play(
            hand=hand,
            lead_suit=Suit.HEARTS,
            current_trick=current_trick,
            tricks_won=1,
            bid=1,  # Already won target bid!
            hand_size=2,
            difficulty=AIDifficulty.MEDIUM,
        )
        # Play c_low (4) which loses to 9, instead of c_high (King)
        assert play == c_low

    def test_empty_hand_select_play(self) -> None:
        """Test selecting play from empty hand returns None gracefully."""
        empty_hand = Hand()
        assert (
            select_ai_card_play(empty_hand, None, [], 0, 0, 1, AIDifficulty.MEDIUM)
            is None
        )

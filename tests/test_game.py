"""Unit tests for game module in duck_engine."""

import pytest
from duck_engine.cards import Card, Hand, Rank, Suit
from duck_engine.game import DuckGameSession, PlayerState, TrickState


class TestPlayerState:
    """Tests for PlayerState class."""

    def test_player_state_initialization(self) -> None:
        """Test initialization and state dictionary export."""
        player = PlayerState("p1", "Alice", is_human=True)
        assert player.player_id == "p1"
        assert player.name == "Alice"
        assert player.is_human is True
        assert player.score == 0

        d = player.to_dict(reveal_hand=True)
        assert d["player_id"] == "p1"
        assert d["is_human"] is True


class TestTrickState:
    """Tests for TrickState class."""

    def test_trick_lead_suit_and_winner_non_spade(self) -> None:
        """Test lead suit assignment and winner evaluation without trump."""
        trick = TrickState("p1")
        c1 = Card(Suit.HEARTS, Rank.NINE)
        c2 = Card(Suit.HEARTS, Rank.KING)
        c3 = Card(Suit.HEARTS, Rank.FIVE)

        trick.add_play("p1", c1)
        assert trick.lead_suit == Suit.HEARTS

        trick.add_play("p2", c2)
        trick.add_play("p3", c3)

        winner = trick.evaluate_winner()
        assert winner == "p2"  # King of Hearts wins
        assert trick.is_complete is True

    def test_trick_winner_spade_trump(self) -> None:
        """Test Spade trump wins over higher lead suit card."""
        trick = TrickState("p1")
        c_lead = Card(Suit.DIAMONDS, Rank.ACE)
        c_trump = Card(Suit.SPADES, Rank.TWO)  # Low spade trumps Ace of Diamonds

        trick.add_play("p1", c_lead)
        trick.add_play("p2", c_trump)

        winner = trick.evaluate_winner()
        assert winner == "p2"

    def test_empty_trick_evaluation(self) -> None:
        """Test evaluating empty trick returns None safely."""
        trick = TrickState("p1")
        assert trick.evaluate_winner() is None


class TestDuckGameSession:
    """Tests for DuckGameSession round progression and scoring."""

    def test_invalid_player_count(self) -> None:
        """Test session creation fails if player count not between 3 and 7."""
        players = [PlayerState("p1", "P1"), PlayerState("p2", "P2")]
        with pytest.raises(ValueError, match="requires 3 to 7 players"):
            DuckGameSession(players)

    def test_session_initialization(self) -> None:
        """Test 4-player game session starts at Round 1 with 7 cards dealt."""
        p1 = PlayerState("p1", "Human", is_human=True)
        p2 = PlayerState("p2", "Bot1", is_human=False)
        p3 = PlayerState("p3", "Bot2", is_human=False)
        p4 = PlayerState("p4", "Bot3", is_human=False)

        session = DuckGameSession([p1, p2, p3, p4])

        assert session.current_round == 1
        assert session.hand_size == 7
        assert len(p1.hand.cards) == 7
        assert session.phase == "BIDDING"

    def test_human_submit_bid(self) -> None:
        """Test human submitting valid and invalid bids."""
        p1 = PlayerState("p1", "Human", is_human=True)
        p2 = PlayerState("p2", "Bot1", is_human=False)
        p3 = PlayerState("p3", "Bot2", is_human=False)
        session = DuckGameSession([p1, p2, p3])

        # Force bidding turn to p1
        session.bidding_turn_idx = 0

        # Out-of-bounds bid
        success, msg = session.submit_bid("p1", 10)
        assert success is False
        assert "between 0 and 7" in msg

        # Valid bid
        success, msg = session.submit_bid("p1", 3)
        assert success is True
        assert p1.current_bid == 3

    def test_step_single_ai_turn(self) -> None:
        """Test stepping AI turn plays a card for AI bot."""
        p1 = PlayerState("p1", "Human", is_human=True)
        p2 = PlayerState("p2", "Bot1", is_human=False)
        p3 = PlayerState("p3", "Bot2", is_human=False)
        session = DuckGameSession([p1, p2, p3])

        session.phase = "PLAYING"
        session.current_turn_idx = 1  # Bot1 turn
        session.current_trick = TrickState("p2")

        stepped = session.step_single_ai_turn()
        assert stepped is True
        assert len(session.current_trick.cards_played) == 1
        assert session.current_trick.cards_played[0][0] == "p2"

    def test_illegal_card_play(self) -> None:
        """Test play_card rejects out of turn or non-following-suit card plays."""
        p1 = PlayerState("p1", "Human", is_human=True)
        p2 = PlayerState("p2", "Bot1", is_human=False)
        p3 = PlayerState("p3", "Bot2", is_human=False)
        session = DuckGameSession([p1, p2, p3])

        session.phase = "PLAYING"
        session.current_turn_idx = 0
        session.current_trick = TrickState("p1")

        hearts_card = Card(Suit.HEARTS, Rank.ACE)
        spades_card = Card(Suit.SPADES, Rank.FIVE)
        p1.hand = Hand([hearts_card, spades_card])
        session.current_trick.lead_suit = Suit.HEARTS

        # Try playing Spades when holding Hearts
        success, msg = session.play_card("p1", spades_card)
        assert success is False
        assert "must follow suit" in msg

        # Playing Hearts should succeed
        success, msg = session.play_card("p1", hearts_card)
        assert success is True

    def test_exact_bid_scoring_bonus(self) -> None:
        """Test exact prediction bid awards +10 bonus points."""
        p1 = PlayerState("p1", "Human", is_human=True)
        p2 = PlayerState("p2", "Bot1", is_human=False)
        p3 = PlayerState("p3", "Bot2", is_human=False)
        session = DuckGameSession([p1, p2, p3])

        p1.current_bid = 2
        p1.tricks_won = 2  # Exact match!

        p2.current_bid = 1
        p2.tricks_won = 3  # Missed bid!

        session._finish_round()

        assert p1.score == 12  # 2 tricks + 10 bonus
        assert p2.score == 3  # 3 tricks + 0 bonus

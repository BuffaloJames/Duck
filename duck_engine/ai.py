"""AI Bot players for Duck card game.

Implements bidding prediction heuristic models and card play strategies across
Easy, Medium, and Hard difficulty levels.
"""

from enum import Enum
import random
from typing import Any, Dict, List, Optional, Tuple

from duck_engine.cards import Card, Hand, Rank, Suit


class AIDifficulty(str, Enum):
    """Bot difficulty settings."""

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


def calculate_ai_bid(
    hand: Hand, hand_size: int, difficulty: AIDifficulty = AIDifficulty.MEDIUM
) -> int:
    """Calculate predicted bid for an AI player.

    Args:
        hand: The player's Hand object.
        hand_size: Total cards in the current round.
        difficulty: AI difficulty strategy to apply.

    Returns:
        Integer bid prediction between 0 and hand_size inclusive.
    """
    if not hand or not hand.cards:
        return 0

    if difficulty == AIDifficulty.EASY:
        return random.randint(0, len(hand.cards))

    # Medium and Hard heuristic estimation
    estimated_tricks: float = 0.0

    for card in hand.cards:
        if card.suit == Suit.SPADES:
            if card.rank in (Rank.ACE, Rank.KING):
                estimated_tricks += 1.0
            elif card.rank in (Rank.QUEEN, Rank.JACK):
                estimated_tricks += 0.8
            elif card.rank in (Rank.TEN, Rank.NINE):
                estimated_tricks += 0.5
            else:
                estimated_tricks += 0.3
        else:
            if card.rank == Rank.ACE:
                estimated_tricks += 0.8
            elif card.rank == Rank.KING:
                estimated_tricks += 0.5
            elif card.rank == Rank.QUEEN:
                estimated_tricks += 0.3

    # Adjust based on small vs large hands
    if hand_size <= 3:
        estimated_tricks *= 0.9

    bid = round(estimated_tricks)
    return max(0, min(len(hand.cards), bid))


def select_ai_card_play(
    hand: Hand,
    lead_suit: Optional[Suit],
    current_trick: List[Tuple[str, Card]],
    tricks_won: int,
    bid: int,
    hand_size: int,
    difficulty: AIDifficulty = AIDifficulty.MEDIUM,
) -> Optional[Card]:
    """Select card to play for an AI player.

    Args:
        hand: Player's current Hand.
        lead_suit: Lead suit of the trick, or None if leading.
        current_trick: List of (player_id, Card) played so far.
        tricks_won: Tricks won by this player in the round.
        bid: Target bid prediction for this player.
        hand_size: Total cards dealt in the round.
        difficulty: AI difficulty setting.

    Returns:
        Chosen Card object, or None if hand empty.
    """
    legal_plays = hand.get_legal_plays(lead_suit)
    if not legal_plays:
        return None

    if difficulty == AIDifficulty.EASY or len(legal_plays) == 1:
        return random.choice(legal_plays)

    needs_win = tricks_won < bid

    # Determine winning card in current trick so far
    highest_trick_card: Optional[Card] = None
    if current_trick:
        spade_plays = [c for _, c in current_trick if c.suit == Suit.SPADES]
        if spade_plays:
            highest_trick_card = max(spade_plays, key=lambda c: c.value)
        elif lead_suit:
            lead_plays = [c for _, c in current_trick if c.suit == lead_suit]
            if lead_plays:
                highest_trick_card = max(lead_plays, key=lambda c: c.value)

    # Strategy: Leading trick
    if lead_suit is None:
        if needs_win:
            # Lead high non-spade Ace/King or high spade
            high_cards = sorted(legal_plays, key=lambda c: c.value, reverse=True)
            return high_cards[0]
        else:
            # Lead lowest non-spade card to avoid winning
            low_non_spades = [c for c in legal_plays if c.suit != Suit.SPADES]
            if low_non_spades:
                low_non_spades.sort(key=lambda c: c.value)
                return low_non_spades[0]
            legal_plays.sort(key=lambda c: c.value)
            return legal_plays[0]

    # Strategy: Following trick
    if needs_win:
        # Try to beat highest card played so far
        if highest_trick_card is None:
            legal_plays.sort(key=lambda c: c.value, reverse=True)
            return legal_plays[0]

        winners = []
        for c in legal_plays:
            if c.suit == Suit.SPADES:
                if (
                    highest_trick_card.suit != Suit.SPADES
                    or c.value > highest_trick_card.value
                ):
                    winners.append(c)
            elif (
                c.suit == lead_suit
                and highest_trick_card.suit == lead_suit
                and c.value > highest_trick_card.value
            ):
                winners.append(c)

        if winners:
            winners.sort(key=lambda c: c.value)
            return winners[0]  # Lowest winning card

        # Can't win, play lowest card
        legal_plays.sort(key=lambda c: c.value)
        return legal_plays[0]
    else:
        # Avoid winning trick
        if highest_trick_card is not None:
            losers = []
            for c in legal_plays:
                if c.suit == lead_suit and highest_trick_card.suit == lead_suit:
                    if c.value < highest_trick_card.value:
                        losers.append(c)
                elif c.suit != Suit.SPADES:
                    losers.append(c)

            if losers:
                losers.sort(key=lambda c: c.value, reverse=True)
                return losers[0]  # Throw highest losing card

        legal_plays.sort(key=lambda c: c.value)
        return legal_plays[0]

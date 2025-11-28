from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .cards import Card, Deck
from .scoring import HandResult, evaluate_hand


@dataclass
class SimpleGame:
    deck: Deck = field(default_factory=Deck)
    hand: List[Card] = field(default_factory=list)

    def start(self) -> None:
        """Reset the deck and draw a fresh set of cards."""
        # Reuse existing deck (handy for deterministic tests) but always reshuffle.
        self.deck.shuffle()
        self.hand = self.deck.draw(8)

    def play_cards(self, indices: List[int]) -> HandResult:
        if not self.hand:
            raise ValueError("Game has not been started. Call start() first.")

        if len(indices) != 5:
            raise ValueError("Exactly 5 card indices must be selected to score a hand.")

        if len(set(indices)) != 5:
            raise ValueError("Card indices must be unique.")

        try:
            cards = [self.hand[i] for i in indices]
        except IndexError as exc:  # pragma: no cover - safety net
            raise ValueError("Selected indices are out of range for the current hand.") from exc

        result = evaluate_hand(cards)

        # Remove played cards and replenish hand if possible.
        for index in sorted(indices, reverse=True):
            del self.hand[index]
        needed = max(0, 8 - len(self.hand))
        if needed:
            draw_count = min(needed, self.deck.remaining())
            if draw_count:
                self.hand.extend(self.deck.draw(draw_count))

        return result

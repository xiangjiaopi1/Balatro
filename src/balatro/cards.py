from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._cards: List[Card] = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self) -> None:
        self._rng.shuffle(self._cards)

    def draw(self, count: int) -> List[Card]:
        if count < 0:
            raise ValueError("count must be non-negative")
        if count > len(self._cards):
            raise ValueError("Not enough cards left in the deck")
        drawn, self._cards = self._cards[:count], self._cards[count:]
        return drawn

    def remaining(self) -> int:
        return len(self._cards)

    def take_back(self, cards: Iterable[Card]) -> None:
        # Put cards back on the bottom of the deck and reshuffle to simplify reuse.
        self._cards.extend(cards)
        self.shuffle()

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

from .cards import Card, RANKS

RANK_ORDER = {rank: index for index, rank in enumerate(RANKS)}


@dataclass(frozen=True)
class HandResult:
    name: str
    chips: int
    multiplier: int

    @property
    def total(self) -> int:
        return self.chips * self.multiplier


HAND_SCORES: list[tuple[str, int, int]] = [
    ("High Card", 10, 1),
    ("One Pair", 20, 2),
    ("Two Pair", 35, 2),
    ("Three of a Kind", 45, 3),
    ("Straight", 55, 4),
    ("Flush", 65, 4),
    ("Full House", 80, 4),
    ("Four of a Kind", 110, 7),
    ("Straight Flush", 140, 8),
]

HAND_LOOKUP = {name: HandResult(name, chips, mult) for name, chips, mult in HAND_SCORES}


def _is_flush(cards: Iterable[Card]) -> bool:
    suits = {card.suit for card in cards}
    return len(suits) == 1


def _is_straight(sorted_ranks: List[str]) -> bool:
    indices = [RANK_ORDER[r] for r in sorted_ranks]
    # Handle wheel straight (A-2-3-4-5)
    if indices == [0, 1, 2, 3, 12]:
        return True
    return all(b - a == 1 for a, b in zip(indices, indices[1:]))


def evaluate_hand(cards: List[Card]) -> HandResult:
    if len(cards) != 5:
        raise ValueError("A hand must contain exactly 5 cards to score.")

    ranks = sorted((card.rank for card in cards), key=lambda r: RANK_ORDER[r])
    flush = _is_flush(cards)
    straight = _is_straight(ranks)
    counts = Counter(ranks).most_common()

    if straight and flush:
        return HAND_LOOKUP["Straight Flush"]

    if counts[0][1] == 4:
        return HAND_LOOKUP["Four of a Kind"]

    if counts[0][1] == 3 and counts[1][1] == 2:
        return HAND_LOOKUP["Full House"]

    if flush:
        return HAND_LOOKUP["Flush"]

    if straight:
        return HAND_LOOKUP["Straight"]

    if counts[0][1] == 3:
        return HAND_LOOKUP["Three of a Kind"]

    if counts[0][1] == 2 and counts[1][1] == 2:
        return HAND_LOOKUP["Two Pair"]

    if counts[0][1] == 2:
        return HAND_LOOKUP["One Pair"]

    return HAND_LOOKUP["High Card"]

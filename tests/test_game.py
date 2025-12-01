import pytest

from balatro.cards import Card, Deck
from balatro.game import SimpleGame


class FixedDeck(Deck):
    def __init__(self, cards):
        self._cards = list(cards)

    def shuffle(self):
        pass


def make_cards(count: int):
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["♠", "♥", "♦", "♣"]
    cards = []
    while len(cards) < count:
        rank = ranks[len(cards) % len(ranks)]
        suit = suits[(len(cards) // len(ranks)) % len(suits)]
        cards.append(Card(rank, suit))
    return cards


def test_game_flow_draw_and_play():
    # Preload deck with deterministic cards
    starter_cards = [
        Card("2", "♠"),
        Card("3", "♠"),
        Card("4", "♠"),
        Card("5", "♠"),
        Card("6", "♠"),
        Card("7", "♥"),
        Card("8", "♦"),
        Card("9", "♣"),
        Card("10", "♣"),
    ]
    game = SimpleGame(deck=FixedDeck(starter_cards))
    game.start()

    assert len(game.hand) == 8

    result = game.play_cards([0, 1, 2, 3, 4])
    assert result.name == "Straight Flush"
    # After playing five cards, three remain and the last extra card is drawn (if available)
    assert len(game.hand) == 4


def test_discard_and_limits():
    game = SimpleGame(deck=FixedDeck(make_cards(20)))
    game.start()

    original_hand = list(game.hand)
    game.discard_cards([0, 1])

    assert len(game.hand) == 8
    assert game.discards_remaining == 4
    assert game.hand != original_hand

    for _ in range(4):
        game.discard_cards([0])

    assert game.discards_remaining == 0
    with pytest.raises(ValueError):
        game.discard_cards([0])


def test_play_limits_and_reset():
    game = SimpleGame(deck=FixedDeck(make_cards(60)))
    game.start()

    for _ in range(game.max_plays):
        game.play_cards([0, 1, 2, 3, 4])

    assert game.plays_remaining == 0
    with pytest.raises(ValueError):
        game.play_cards([0, 1, 2, 3, 4])

    game.start()
    assert game.plays_remaining == game.max_plays

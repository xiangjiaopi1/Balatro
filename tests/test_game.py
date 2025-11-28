from balatro.cards import Card, Deck
from balatro.game import SimpleGame


class FixedDeck(Deck):
    def __init__(self, cards):
        self._cards = list(cards)

    def shuffle(self):
        pass


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

import pytest

from balatro.cards import Card
from balatro.scoring import evaluate_hand


def make_hand(descriptors):
    return [Card(rank, suit) for rank, suit in descriptors]


def test_straight_flush():
    hand = make_hand([("9", "♠"), ("10", "♠"), ("J", "♠"), ("Q", "♠"), ("K", "♠")])
    result = evaluate_hand(hand)
    assert result.name == "Straight Flush"


def test_four_of_a_kind():
    hand = make_hand([("A", "♠"), ("A", "♥"), ("A", "♦"), ("A", "♣"), ("K", "♠")])
    result = evaluate_hand(hand)
    assert result.name == "Four of a Kind"


def test_full_house():
    hand = make_hand([("3", "♠"), ("3", "♥"), ("3", "♦"), ("8", "♣"), ("8", "♦")])
    assert evaluate_hand(hand).name == "Full House"


def test_flush():
    hand = make_hand([("2", "♠"), ("5", "♠"), ("8", "♠"), ("J", "♠"), ("K", "♠")])
    assert evaluate_hand(hand).name == "Flush"


def test_straight_with_wheel():
    hand = make_hand([("A", "♠"), ("2", "♥"), ("3", "♣"), ("4", "♦"), ("5", "♠")])
    assert evaluate_hand(hand).name == "Straight"


def test_three_of_a_kind():
    hand = make_hand([("Q", "♠"), ("Q", "♥"), ("Q", "♦"), ("6", "♣"), ("10", "♠")])
    assert evaluate_hand(hand).name == "Three of a Kind"


def test_two_pair():
    hand = make_hand([("5", "♠"), ("5", "♥"), ("K", "♣"), ("K", "♦"), ("7", "♣")])
    assert evaluate_hand(hand).name == "Two Pair"


def test_one_pair():
    hand = make_hand([("4", "♠"), ("4", "♥"), ("8", "♣"), ("9", "♦"), ("J", "♣")])
    assert evaluate_hand(hand).name == "One Pair"


def test_high_card():
    hand = make_hand([("2", "♠"), ("5", "♥"), ("9", "♣"), ("J", "♦"), ("K", "♣")])
    assert evaluate_hand(hand).name == "High Card"


def test_invalid_hand_size():
    with pytest.raises(ValueError):
        evaluate_hand(make_hand([("2", "♠"), ("5", "♥")]))

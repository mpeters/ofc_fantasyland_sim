"""Tests for parse_hand card-string parsing and validation."""

import pytest

from conftest import ofc


def test_parse_valid_13_card_hand():
    cards = ofc.parse_hand("Ac2c5c9cAd3d4dTdQd5s8sTsKs")
    assert len(cards) == 13
    # Each card is (rank_value, suit, display).
    assert cards[0] == (ofc.RANK_VALUE["A"], "c", "Ac")
    assert cards[1] == (ofc.RANK_VALUE["2"], "c", "2c")


def test_parse_is_case_insensitive_and_normalizes_display():
    cards = ofc.parse_hand("aC2C5C9CAD3D4DTDQD5S8STSKS")
    # Ranks upper, suits lower in the normalized display.
    assert cards[0][2] == "Ac"
    assert all(c[2][0] in "23456789TJQKA" and c[2][1] in "cdhs" for c in cards)


def test_parse_tolerates_whitespace():
    a = ofc.parse_hand("Ac 2c 5c 9c Ad 3d 4d Td Qd 5s 8s Ts Ks")
    b = ofc.parse_hand("Ac2c5c9cAd3d4dTdQd5s8sTsKs")
    assert a == b


def test_parse_accepts_14_15_16_cards():
    for n in (14, 15, 16):
        # Build n distinct cards from the deck.
        deck = ofc.full_deck()
        text = "".join(c[2] for c in deck[:n])
        parsed = ofc.parse_hand(text)
        assert len(parsed) == n


def test_parse_empty_raises():
    with pytest.raises(ofc.InputError, match="empty hand"):
        ofc.parse_hand("")


def test_parse_whitespace_only_is_empty():
    with pytest.raises(ofc.InputError, match="empty hand"):
        ofc.parse_hand("   \t\n ")


def test_parse_odd_length_raises():
    with pytest.raises(ofc.InputError, match="even number"):
        ofc.parse_hand("Ac2c5")


def test_parse_invalid_rank_raises():
    with pytest.raises(ofc.InputError, match="invalid rank"):
        ofc.parse_hand("1c2c5c9cAd3d4dTdQd5s8sTsKs")


def test_parse_invalid_suit_raises():
    with pytest.raises(ofc.InputError, match="invalid suit"):
        ofc.parse_hand("Ax2c5c9cAd3d4dTdQd5s8sTsKs")


def test_parse_duplicate_card_raises():
    with pytest.raises(ofc.InputError, match="duplicate card"):
        ofc.parse_hand("AcAc5c9cAd3d4dTdQd5s8sTsKs")


def test_parse_too_few_cards_raises():
    with pytest.raises(ofc.InputError, match="expected 13 to 16"):
        ofc.parse_hand("Ac2c5c9cAd3d4dTd")  # 8 cards


def test_parse_too_many_cards_raises():
    deck = ofc.full_deck()
    text = "".join(c[2] for c in deck[:17])
    with pytest.raises(ofc.InputError, match="expected 13 to 16"):
        ofc.parse_hand(text)

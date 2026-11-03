"""Tests for formatting/output helpers and the deck builder."""

from conftest import ofc, make_cards


def test_full_deck_has_52_unique_cards():
    deck = ofc.full_deck()
    assert len(deck) == 52
    assert len({c[2] for c in deck}) == 52
    # Every rank/suit combination present.
    assert {c[1] for c in deck} == set("cdhs")
    assert {c[2][0] for c in deck} == set("23456789TJQKA")


def test_format_cards():
    cards = make_cards(["Ac", "Kd", "9h"])
    assert ofc.format_cards(cards, [0, 2]) == "Ac 9h"
    assert ofc.format_cards(cards, []) == ""


def test_row_name_five_card_categories():
    straight = ofc.eval5(make_cards(["5c", "6d", "7h", "8s", "9c"]))
    assert ofc.row_name(straight, 5) == "Straight"
    flush = ofc.eval5(make_cards(["2c", "5c", "7c", "9c", "Jc"]))
    assert ofc.row_name(flush, 5) == "Flush"


def test_row_name_three_card_categories():
    pair = ofc.eval3(make_cards(["Ac", "Ad", "9h"]))
    assert ofc.row_name(pair, 3) == "Pair"
    trips = ofc.eval3(make_cards(["Ac", "Ad", "Ah"]))
    assert ofc.row_name(trips, 3) == "Three of a Kind"


def test_row_name_royal_flush_special_case():
    royal = ofc.eval5(make_cards(["Tc", "Jc", "Qc", "Kc", "Ac"]))
    assert ofc.row_name(royal, 5) == "Royal Flush"
    sf = ofc.eval5(make_cards(["5c", "6c", "7c", "8c", "9c"]))
    assert ofc.row_name(sf, 5) == "Straight Flush"


def test_three_map_ev_helper():
    cards = make_cards(["Ac", "Ad", "Ah", "2c", "3c"])
    assert ofc.three_map_ev(cards, (0, 1, 2)) == (3, ofc.RANK_VALUE["A"])


def test_format_duration_minutes_seconds():
    assert ofc.format_duration(0) == "0:00"
    assert ofc.format_duration(5) == "0:05"
    assert ofc.format_duration(65) == "1:05"
    assert ofc.format_duration(600) == "10:00"


def test_format_duration_hours():
    assert ofc.format_duration(3661) == "1:01:01"
    assert ofc.format_duration(7200) == "2:00:00"


def test_format_duration_rounds():
    assert ofc.format_duration(5.6) == "0:06"


def test_percentile_empty_is_zero():
    assert ofc.percentile([], 50) == 0


def test_percentile_basic():
    vals = [0, 10, 20, 30, 40]
    assert ofc.percentile(vals, 0) == 0
    assert ofc.percentile(vals, 100) == 40
    assert ofc.percentile(vals, 50) == 20


def test_percentile_interpolates():
    vals = [0, 10]
    # k = (2-1) * 0.25 = 0.25 -> between index 0 and 1
    assert ofc.percentile(vals, 25) == 2.5

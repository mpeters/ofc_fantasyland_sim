"""Tests for royalty scoring, Fantasyland-stay rule, and strength_value."""

import pytest

from conftest import ofc, make_cards

R = ofc.RANK_VALUE


def ev5(codes):
    return ofc.eval5(make_cards(codes))


def ev3(codes):
    return ofc.eval3(make_cards(codes))


# --------------------------------------------------------------------------- #
# top_royalty
# --------------------------------------------------------------------------- #

def test_top_royalty_high_card_zero():
    assert ofc.top_royalty(ev3(["Ac", "Kd", "9h"])) == 0


@pytest.mark.parametrize("pair_rank,expected", [
    ("2", 0), ("3", 0), ("4", 0), ("5", 0),  # below 66 => no royalty
    ("6", 1), ("7", 2), ("8", 3), ("9", 4), ("T", 5),
    ("J", 6), ("Q", 7), ("K", 8), ("A", 9),
])
def test_top_royalty_pairs(pair_rank, expected):
    ev = ev3([pair_rank + "c", pair_rank + "d", "3h" if pair_rank != "3" else "4h"])
    assert ofc.top_royalty(ev) == expected


@pytest.mark.parametrize("rank,expected", [
    ("2", 10), ("3", 11), ("A", 22),
])
def test_top_royalty_trips(rank, expected):
    ev = ev3([rank + "c", rank + "d", rank + "h"])
    assert ofc.top_royalty(ev) == expected


# --------------------------------------------------------------------------- #
# middle_royalty
# --------------------------------------------------------------------------- #

def test_middle_royalty_below_trips_zero():
    assert ofc.middle_royalty(ev5(["Ac", "Ad", "9h", "9s", "2c"])) == 0  # two pair


def test_middle_royalty_values():
    assert ofc.middle_royalty(ev5(["Ac", "Ad", "Ah", "9s", "2c"])) == 2   # trips
    assert ofc.middle_royalty(ev5(["5c", "6d", "7h", "8s", "9c"])) == 4   # straight
    assert ofc.middle_royalty(ev5(["2c", "5c", "7c", "9c", "Jc"])) == 8   # flush
    assert ofc.middle_royalty(ev5(["Ac", "Ad", "Ah", "9s", "9c"])) == 12  # boat
    assert ofc.middle_royalty(ev5(["Ac", "Ad", "Ah", "As", "9c"])) == 20  # quads


def test_middle_royalty_straight_flush_and_royal():
    assert ofc.middle_royalty(ev5(["5c", "6c", "7c", "8c", "9c"])) == 30  # SF
    assert ofc.middle_royalty(ev5(["Tc", "Jc", "Qc", "Kc", "Ac"])) == 50  # royal


# --------------------------------------------------------------------------- #
# bottom_royalty
# --------------------------------------------------------------------------- #

def test_bottom_royalty_below_straight_zero():
    assert ofc.bottom_royalty(ev5(["Ac", "Ad", "Ah", "9s", "2c"])) == 0  # trips


def test_bottom_royalty_values():
    assert ofc.bottom_royalty(ev5(["5c", "6d", "7h", "8s", "9c"])) == 2   # straight
    assert ofc.bottom_royalty(ev5(["2c", "5c", "7c", "9c", "Jc"])) == 4   # flush
    assert ofc.bottom_royalty(ev5(["Ac", "Ad", "Ah", "9s", "9c"])) == 6   # boat
    assert ofc.bottom_royalty(ev5(["Ac", "Ad", "Ah", "As", "9c"])) == 10  # quads


def test_bottom_royalty_straight_flush_and_royal():
    assert ofc.bottom_royalty(ev5(["5c", "6c", "7c", "8c", "9c"])) == 15  # SF
    assert ofc.bottom_royalty(ev5(["Tc", "Jc", "Qc", "Kc", "Ac"])) == 25  # royal


# --------------------------------------------------------------------------- #
# stays_in_fantasyland
# --------------------------------------------------------------------------- #

def test_stays_trips_on_top():
    top = ev3(["2c", "2d", "2h"])
    bottom = ev5(["Ac", "Kd", "9h", "7s", "2s"])  # nothing
    assert ofc.stays_in_fantasyland(top, bottom) is True


def test_stays_quads_on_bottom():
    top = ev3(["Ac", "Kd", "9h"])  # high card
    bottom = ev5(["2c", "2d", "2h", "2s", "7c"])  # quads
    assert ofc.stays_in_fantasyland(top, bottom) is True


def test_stays_straight_flush_on_bottom():
    top = ev3(["Ac", "Kd", "9h"])
    bottom = ev5(["5c", "6c", "7c", "8c", "9c"])
    assert ofc.stays_in_fantasyland(top, bottom) is True


def test_does_not_stay():
    top = ev3(["Ac", "Ad", "9h"])  # pair
    bottom = ev5(["Ac", "Ad", "Ah", "9s", "9c"])  # full house (<quads)
    assert ofc.stays_in_fantasyland(top, bottom) is False


# --------------------------------------------------------------------------- #
# strength_value
# --------------------------------------------------------------------------- #

def test_strength_value_monotonic_in_category():
    weak = ofc.strength_value(ev5(["Ac", "Kd", "9h", "7s", "2c"]), 5)
    strong = ofc.strength_value(ev5(["5c", "6c", "7c", "8c", "9c"]), 5)
    assert strong > weak


def test_strength_value_respects_tiebreakers():
    higher = ofc.strength_value(ev5(["Ac", "Ad", "Kh", "7s", "2c"]), 5)
    lower = ofc.strength_value(ev5(["Ac", "Ad", "Qh", "7s", "2c"]), 5)
    assert higher > lower


def test_strength_value_pads_to_slots():
    # A straight's ev is (4, high) -> only one tiebreaker, padded out to 5.
    v = ofc.strength_value((4, 9), 5)
    # Category dominates: 4 * 15^5 + 9 * 15^4
    assert v == 4 * 15 ** 5 + 9 * 15 ** 4

"""Tests for the 5-card and 3-card hand evaluators."""

from conftest import ofc, make_cards

R = ofc.RANK_VALUE


# --------------------------------------------------------------------------- #
# eval5 category detection
# --------------------------------------------------------------------------- #

def test_eval5_high_card():
    ev = ofc.eval5(make_cards(["Ac", "Kd", "9h", "7s", "2c"]))
    assert ev[0] == 0
    # Tiebreakers are ranks high to low.
    assert ev == (0, R["A"], R["K"], 9, 7, 2)


def test_eval5_pair():
    ev = ofc.eval5(make_cards(["Ac", "Ad", "9h", "7s", "2c"]))
    assert ev[0] == 1
    assert ev[1] == R["A"]  # the pair rank leads the tiebreakers


def test_eval5_two_pair():
    ev = ofc.eval5(make_cards(["Ac", "Ad", "9h", "9s", "2c"]))
    assert ev[0] == 2
    assert ev[1] == R["A"]
    assert ev[2] == 9


def test_eval5_three_of_a_kind():
    ev = ofc.eval5(make_cards(["Ac", "Ad", "Ah", "9s", "2c"]))
    assert ev[0] == 3
    assert ev[1] == R["A"]


def test_eval5_straight():
    ev = ofc.eval5(make_cards(["5c", "6d", "7h", "8s", "9c"]))
    assert ev == (4, 9)


def test_eval5_wheel_straight_is_five_high():
    ev = ofc.eval5(make_cards(["Ac", "2d", "3h", "4s", "5c"]))
    assert ev == (4, 5)


def test_eval5_broadway_straight():
    ev = ofc.eval5(make_cards(["Tc", "Jd", "Qh", "Ks", "Ac"]))
    assert ev == (4, R["A"])


def test_eval5_flush():
    ev = ofc.eval5(make_cards(["Ac", "Kc", "9c", "7c", "2c"]))
    assert ev[0] == 5
    assert ev[1:] == (R["A"], R["K"], 9, 7, 2)


def test_eval5_full_house():
    ev = ofc.eval5(make_cards(["Ac", "Ad", "Ah", "9s", "9c"]))
    assert ev[0] == 6
    assert ev[1] == R["A"]
    assert ev[2] == 9


def test_eval5_four_of_a_kind():
    ev = ofc.eval5(make_cards(["Ac", "Ad", "Ah", "As", "9c"]))
    assert ev[0] == 7
    assert ev[1] == R["A"]


def test_eval5_straight_flush():
    ev = ofc.eval5(make_cards(["5c", "6c", "7c", "8c", "9c"]))
    assert ev == (8, 9)


def test_eval5_steel_wheel_straight_flush():
    ev = ofc.eval5(make_cards(["Ac", "2c", "3c", "4c", "5c"]))
    assert ev == (8, 5)


def test_eval5_royal_flush():
    ev = ofc.eval5(make_cards(["Tc", "Jc", "Qc", "Kc", "Ac"]))
    assert ev == (8, R["A"])


def test_eval5_ordering_relations():
    hc = ofc.eval5(make_cards(["Ac", "Kd", "9h", "7s", "2c"]))
    pair = ofc.eval5(make_cards(["2c", "2d", "9h", "7s", "3c"]))
    twop = ofc.eval5(make_cards(["2c", "2d", "3h", "3s", "4c"]))
    trips = ofc.eval5(make_cards(["2c", "2d", "2h", "7s", "3c"]))
    straight = ofc.eval5(make_cards(["5c", "6d", "7h", "8s", "9c"]))
    flush = ofc.eval5(make_cards(["2c", "5c", "7c", "9c", "Jc"]))
    boat = ofc.eval5(make_cards(["2c", "2d", "2h", "7s", "7c"]))
    quads = ofc.eval5(make_cards(["2c", "2d", "2h", "2s", "7c"]))
    sf = ofc.eval5(make_cards(["5c", "6c", "7c", "8c", "9c"]))
    assert hc < pair < twop < trips < straight < flush < boat < quads < sf


def test_eval5_kicker_tiebreak():
    higher = ofc.eval5(make_cards(["Ac", "Ad", "Kh", "7s", "2c"]))
    lower = ofc.eval5(make_cards(["Ac", "Ad", "Qh", "7s", "2c"]))
    assert higher > lower


# --------------------------------------------------------------------------- #
# eval3
# --------------------------------------------------------------------------- #

def test_eval3_high_card():
    ev = ofc.eval3(make_cards(["Ac", "Kd", "9h"]))
    assert ev == (0, R["A"], R["K"], 9)


def test_eval3_pair():
    ev = ofc.eval3(make_cards(["Ac", "Ad", "9h"]))
    assert ev[0] == 1
    assert ev[1] == R["A"]
    assert ev[2] == 9  # kicker


def test_eval3_trips():
    ev = ofc.eval3(make_cards(["Ac", "Ad", "Ah"]))
    assert ev == (3, R["A"])


def test_eval3_ordering():
    hc = ofc.eval3(make_cards(["Ac", "Kd", "9h"]))
    pair = ofc.eval3(make_cards(["2c", "2d", "3h"]))
    trips = ofc.eval3(make_cards(["2c", "2d", "2h"]))
    assert hc < pair < trips

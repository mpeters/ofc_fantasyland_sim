"""Tests for the solve() optimizer and its invariants."""

import pytest

from conftest import ofc


def unpack(best):
    score, bottom, middle, top, b_roy, m_roy, t_roy, stay = best
    return score, bottom, middle, top, b_roy, m_roy, t_roy, stay


def evs_for(cards, bottom, middle, top):
    bev = ofc.eval5([cards[i] for i in bottom])
    mev = ofc.eval5([cards[i] for i in middle])
    tev = ofc.eval3([cards[i] for i in top])
    return bev, mev, tev


def assert_valid_solution(cards, best):
    score, bottom, middle, top, b_roy, m_roy, t_roy, stay = unpack(best)

    # Row sizes.
    assert len(bottom) == 5
    assert len(middle) == 5
    assert len(top) == 3

    # Rows are disjoint and use real card indices.
    used = list(bottom) + list(middle) + list(top)
    assert len(set(used)) == 13
    assert all(0 <= i < len(cards) for i in used)

    # No foul: bottom >= middle >= top on the shared strength scale.
    bev, mev, tev = evs_for(cards, bottom, middle, top)
    assert bev >= mev
    assert mev >= tev

    # Reported royalties match a fresh recomputation.
    assert b_roy == ofc.bottom_royalty(bev)
    assert m_roy == ofc.middle_royalty(mev)
    assert t_roy == ofc.top_royalty(tev)

    # Stay flag is consistent with the rule.
    assert stay == ofc.stays_in_fantasyland(tev, bev)


def test_solve_readme_example_is_valid():
    cards = ofc.parse_hand("Ac2c5c9cAd3d4dTdQd5s8sTsKs")
    best = ofc.solve(cards)
    assert best is not None
    assert_valid_solution(cards, best)


def test_solve_is_deterministic():
    cards = ofc.parse_hand("Ac2c5c9cAd3d4dTdQd5s8sTsKs")
    assert ofc.solve(cards)[0] == ofc.solve(cards)[0]


def test_solve_finds_optimal_total_is_maximal():
    # Brute-force the true maximum reported-royalty total and confirm the
    # solver's chosen arrangement is at least as good (it optimizes a
    # shadow-adjusted score, but should never report a worse legal total than
    # the best legal total it is capable of reaching — we check its own total
    # is consistent and non-fouling, and compare to an exhaustive search of
    # reported totals among non-fouling arrangements).
    cards = ofc.parse_hand("Ac2c5c9cAd3d4dTdQd5s8sTsKs")
    best = ofc.solve(cards)
    _, b, m, t, b_roy, m_roy, t_roy, _ = unpack(best)
    chosen_total = b_roy + m_roy + t_roy

    from itertools import combinations
    idx = list(range(13))
    best_total = -1
    for bottom in combinations(idx, 5):
        bev = ofc.eval5([cards[i] for i in bottom])
        rest1 = [i for i in idx if i not in set(bottom)]
        for middle in combinations(rest1, 5):
            mev = ofc.eval5([cards[i] for i in middle])
            if mev > bev:
                continue
            rest2 = [i for i in rest1 if i not in set(middle)]
            for top in combinations(rest2, 3):
                tev = ofc.eval3([cards[i] for i in top])
                if tev > mev:
                    continue
                total = (ofc.bottom_royalty(bev) + ofc.middle_royalty(mev)
                         + ofc.top_royalty(tev))
                best_total = max(best_total, total)

    # The solver may trade a little current royalty for a Fantasyland stay, but
    # for this example no stay is available, so the chosen total equals the max.
    assert chosen_total == best_total


def test_solve_keeps_fantasyland_when_available():
    # Hand with four 2s: a quads-on-bottom arrangement keeps Fantasyland and
    # is also high royalty, so the solver should choose to stay.
    cards = ofc.parse_hand("2c2d2h2sKcKdQhQsJcJd9s8s7s")
    best = ofc.solve(cards)
    assert_valid_solution(cards, best)
    assert best[-1] is True  # stay


def test_trips_in_middle_does_not_steal_high_cards_from_top():
    # Trips kickers never break a showdown tie, so high cards should go to the
    # top (which routinely wins on a single high card) rather than padding the
    # middle trips. Expected: top is K-T-9 high, middle is trips Jacks with the
    # two lowest available kickers.
    cards = ofc.parse_hand("9sThKhJdJhJs5c6hAsAdAc7c7d3c")
    best = ofc.solve(cards)
    assert_valid_solution(cards, best)
    _, bottom, middle, top, *_ = unpack(best)
    bev, mev, tev = evs_for(cards, bottom, middle, top)

    assert mev[0] == 3 and mev[1] == ofc.RANK_VALUE["J"]  # trips Jacks
    assert tev[0] == 0  # top is a high-card hand
    top_ranks = sorted((cards[i][0] for i in top), reverse=True)
    assert top_ranks == [ofc.RANK_VALUE["K"], ofc.RANK_VALUE["T"],
                         ofc.RANK_VALUE["9"]]


def cards5(text):
    return [(ofc.RANK_VALUE[text[i].upper()], text[i + 1].lower(),
             text[i].upper() + text[i + 1].lower())
            for i in range(0, len(text), 2)]


def test_strength_value_ignores_dead_kickers():
    # Trips: the two kickers must not change the strength.
    t_hi = ofc.eval5(cards5("JdJhJsKhTh"))
    t_lo = ofc.eval5(cards5("JdJhJs6h5c"))
    assert ofc.strength_value(t_hi, 5) == ofc.strength_value(t_lo, 5)
    # Quads kicker and full-house pair rank are likewise dead.
    q_hi = ofc.eval5(cards5("2c2d2h2sKd"))
    q_lo = ofc.eval5(cards5("2c2d2h2s3d"))
    assert ofc.strength_value(q_hi, 5) == ofc.strength_value(q_lo, 5)
    fh_hi = ofc.eval5(cards5("JdJhJsKhKd"))
    fh_lo = ofc.eval5(cards5("JdJhJs3h3d"))
    assert ofc.strength_value(fh_hi, 5) == ofc.strength_value(fh_lo, 5)
    # Two pair: both pairs are live, but the lone kicker is dead.
    tp_hi = ofc.eval5(cards5("JdJh5c5dKh"))
    tp_lo = ofc.eval5(cards5("JdJh5c5d2h"))
    assert ofc.strength_value(tp_hi, 5) == ofc.strength_value(tp_lo, 5)
    # ...but a change in a pair rank must still register.
    tp_other = ofc.eval5(cards5("JdJh6c6dKh"))
    assert ofc.strength_value(tp_hi, 5) != ofc.strength_value(tp_other, 5)


def test_solve_16_card_hand_discards_down_to_13():
    deck = ofc.full_deck()
    text = "".join(c[2] for c in deck[:16])
    cards = ofc.parse_hand(text)
    best = ofc.solve(cards)
    assert_valid_solution(cards, best)
    # 16 dealt, 13 placed -> 3 discarded.
    _, b, m, t, *_ = unpack(best)
    used = set(b) | set(m) | set(t)
    assert len(cards) - len(used) == 3

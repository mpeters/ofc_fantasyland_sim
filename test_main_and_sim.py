"""End-to-end tests for print_solution, main(), and simulation mode."""

import pytest

from conftest import ofc


# --------------------------------------------------------------------------- #
# print_solution
# --------------------------------------------------------------------------- #

def test_print_solution_none(capsys):
    ofc.print_solution([], None)
    out = capsys.readouterr().out
    assert "No valid" in out


def test_print_solution_renders_rows(capsys):
    cards = ofc.parse_hand("Ac2c5c9cAd3d4dTdQd5s8sTsKs")
    best = ofc.solve(cards)
    ofc.print_solution(cards, best)
    out = capsys.readouterr().out
    assert "Top" in out
    assert "Middle" in out
    assert "Bottom" in out
    assert "Total" in out
    assert "Stays in Fantasyland" in out


def test_print_solution_shows_discards_for_16_cards(capsys):
    deck = ofc.full_deck()
    cards = ofc.parse_hand("".join(c[2] for c in deck[:16]))
    best = ofc.solve(cards)
    ofc.print_solution(cards, best)
    out = capsys.readouterr().out
    assert "Discarded:" in out


# --------------------------------------------------------------------------- #
# main() - single hand mode
# --------------------------------------------------------------------------- #

def test_main_hand_success(capsys):
    rc = ofc.main(["--hand", "Ac2c5c9cAd3d4dTdQd5s8sTsKs"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Bottom" in out


def test_main_hand_invalid_returns_2(capsys):
    rc = ofc.main(["--hand", "garbage"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "error:" in err


def test_main_hand_wrong_count_returns_2(capsys):
    rc = ofc.main(["--hand", "Ac2c5c"])  # too few
    assert rc == 2
    assert "error:" in capsys.readouterr().err


def test_main_requires_a_mode():
    # The mutually exclusive group is required -> argparse exits with SystemExit.
    with pytest.raises(SystemExit):
        ofc.main([])


# --------------------------------------------------------------------------- #
# main() - simulation mode
# --------------------------------------------------------------------------- #

def test_main_sims_runs_and_reports(capsys):
    rc = ofc.main(["--sims", "3", "--seed", "42"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Simulated 3 random" in out
    assert "Average score" in out
    assert "Score distribution" in out


def test_main_sims_is_reproducible_with_seed(capsys):
    ofc.main(["--sims", "3", "--seed", "7"])
    first = capsys.readouterr().out
    ofc.main(["--sims", "3", "--seed", "7"])
    second = capsys.readouterr().out
    assert first == second


def test_main_sims_custom_card_count(capsys):
    rc = ofc.main(["--sims", "2", "--seed", "1", "--cards", "14"])
    assert rc == 0
    assert "14-card" in capsys.readouterr().out


def test_main_sims_non_positive_returns_2(capsys):
    rc = ofc.main(["--sims", "0"])
    assert rc == 2
    assert "positive integer" in capsys.readouterr().err


def test_main_sims_bad_card_count_returns_2(capsys):
    rc = ofc.main(["--sims", "1", "--cards", "20"])
    assert rc == 2
    assert "between 13 and 16" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# simulation report edge cases
# --------------------------------------------------------------------------- #

def test_print_simulation_report_single_score(capsys):
    # n == 1 exercises the pstdev=0.0 branch and single-bucket histogram.
    ofc.print_simulation_report([8], 1, {"top": 1, "middle": 3, "bottom": 4}, 13)
    out = capsys.readouterr().out
    assert "Simulated 1" in out
    assert "Std deviation:" in out


def test_run_simulations_direct(capsys):
    ofc.run_simulations(2, 13, seed=99)
    out = capsys.readouterr().out
    assert "Simulated 2 random 13-card" in out


def test_friendly_exit_exits_130(capsys):
    with pytest.raises(SystemExit) as exc:
        ofc._friendly_exit()
    assert exc.value.code == 130
    assert "Interrupted" in capsys.readouterr().err

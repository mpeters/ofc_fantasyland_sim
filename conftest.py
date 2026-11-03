"""Shared test fixtures / module loader.

The program under test is a single executable script named ``ofc_fl_sim``
with no ``.py`` extension, so it cannot be imported normally. We load it once
here via importlib and expose it (and a couple of card helpers) to the tests.
"""

import importlib.util
import os
from importlib.machinery import SourceFileLoader

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "ofc_fl_sim")

# The program under test has no ``.py`` extension, so importlib cannot infer a
# loader from the filename; supply a SourceFileLoader explicitly.
_loader = SourceFileLoader("ofc_fl_sim", _SRC)
_spec = importlib.util.spec_from_loader("ofc_fl_sim", _loader)
ofc = importlib.util.module_from_spec(_spec)
_loader.exec_module(ofc)


def make_card(code):
    """Build a single card tuple (rank_value, suit, display) from e.g. 'Ac'."""
    rc = code[0].upper()
    sc = code[1].lower()
    return (ofc.RANK_VALUE[rc], sc, rc + sc)


def make_cards(codes):
    """Build a list of card tuples from an iterable of 2-char codes."""
    return [make_card(c) for c in codes]


@pytest.fixture
def mod():
    return ofc


@pytest.fixture
def card():
    return make_card


@pytest.fixture
def cards():
    return make_cards

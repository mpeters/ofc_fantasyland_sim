# Makefile for ofc_fl_sim
#
#   make test   - create a local virtualenv, install dev dependencies, run the
#                 pytest suite with coverage.
#   make clean  - remove the virtualenv and all build/test artifacts.

PYTHON ?= python3
VENV   := .venv
BIN    := $(VENV)/bin
PYTEST := $(BIN)/pytest

.PHONY: test clean

# Marker file: lets Make skip reinstalling deps unless requirements change.
$(VENV)/.installed: requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r requirements-dev.txt
	touch $@

test: $(VENV)/.installed
	$(PYTEST) --cov=ofc_fl_sim --cov-report=term-missing

clean:
	rm -rf $(VENV) .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

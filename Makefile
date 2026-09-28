SHELL := /usr/bin/bash

VENV_DIR ?= .venv
PYTHON   := $(VENV_DIR)/bin/python
PIP      := $(VENV_DIR)/bin/pip

.PHONY: help setup venv deps run test lint format pre-commit clean

help:
	@echo "Targets:"
	@echo "  make setup        Bootstrap project (venv, deps, .env, pre-commit)"
	@echo "  make run          Run server (uses run.sh)"
	@echo "  make test         Run tests (pytest)"
	@echo "  make lint         Ruff check"
	@echo "  make format       Ruff format"
	@echo "  make pre-commit   Run pre-commit on all files"
	@echo "  make clean        Remove caches (keeps venv)"

setup:
	@./scripts/setup.sh

run:
	@./scripts/run.sh

test:
	@$(VENV_DIR)/bin/pytest -q

lint:
	@$(VENV_DIR)/bin/ruff check .

format:
	@$(VENV_DIR)/bin/ruff format .

pre-commit:
	@$(VENV_DIR)/bin/pre-commit run --all-files

clean:
	@rm -rf __pycache__ .pytest_cache .ruff_cache

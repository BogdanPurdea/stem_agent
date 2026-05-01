.PHONY: help install dev run test integration-tests lint format

help:
	@echo 'Targets:'
	@echo '  install             Sync runtime dependencies with uv'
	@echo '  dev                 Sync project + dev dependencies with uv'
	@echo '  run                 Start the local LangGraph dev server'
	@echo '  test                Run unit tests'
	@echo '  integration-tests   Run integration tests'
	@echo '  lint                Run Ruff checks'
	@echo '  format              Format with Ruff'
	@echo '  create-dataset      Create dataset for evaluation'
	@echo '  eval                Run STEM Agent evaluation'
	@echo '  eval-baseline       Run Baseline ReAct Agent evaluation'

install:
	uv sync --no-dev

dev:
	uv sync

run:
	uv run langgraph dev

test:
	uv run python -m pytest tests/unit_tests -q

integration-tests:
	uv run python -m pytest tests/integration_tests -q

lint:
	uv run python -m ruff check src tests

format:
	uv run python -m ruff format src tests

create-dataset:
	uv run python -m evals.create_dataset

eval:
	uv run python -m evals.run_eval

eval-baseline:
	uv run python -m evals.run_baseline_eval
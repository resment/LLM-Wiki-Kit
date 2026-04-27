# AGENTS.md

## Project

This repository implements llm-wiki-kit, a framework for building LLM-compiled Markdown knowledge bases.

## Commands

- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Format: `ruff format .`

## Rules

- Do not call external LLM APIs in tests.
- Do not mutate files under `raw/`.
- Keep generated templates deterministic.
- All new CLI commands require tests.
- Prefer small, composable modules.
- Keep Hermes integration optional.
- Keep examples anonymized.
- Keep templates and implementation separate.
- Do not hard-code business examples into core modules.
- Do not claim implemented automation in README before it exists.


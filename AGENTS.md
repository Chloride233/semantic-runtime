# Semantic Runtime project rules

## Purpose

Semantic Runtime is an open-source semantic infrastructure layer for AI
Agents: it provides semantic understanding, context resolution, evidence,
and safe execution between models and tools. It does not replace LLMs,
agent frameworks, databases, or MCP.

## Run and verify

- Install development dependencies: `python -m pip install -e '.[dev]'`.
- Run tests: `python -m pytest -q`.
- Run lint: `python -m ruff check src tests`.
- uv-managed alternative: `uv sync --extra dev` then `uv run pytest -q`.

## Stack and layout

- Python 3.12, `src/` layout; runtime code lives in `src/semantic_runtime/`.
- Design specifications live in `docs/` and are the source of truth;
  superseded v0.1 drafts are archived in `docs/archive/`.
- `Semantic Runtime.md` at the repository root is the Obsidian index (MOC);
  wikilinks resolve by filename, so notes moved into `docs/` stay intact.
- Unit tests live in `tests/unit/`; integration tests belong in
  `tests/integration/`.

## Current contract

- v0.1 is a package foundation: blueprint module packages exist, no runtime
  behavior is implemented yet.
- Data models, loaders, registry, graph engine, context resolver, MCP server,
  examples, and scripts are planned milestones from the Core Implementation
  Plan; do not claim them as shipped.
- Keep README, rules, and docs aligned with implemented behavior.

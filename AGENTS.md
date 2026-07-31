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

- Core Phases 1-5 are shipped: data models (Entity / Relation / Metric /
  Evidence / Policy), YAML model loader, registry, graph engine, deterministic
  context resolver, metric dependency resolution, policy-based operation
  validation, SQL guardrails, model integrity validation, MCP server
  (`python -m semantic_runtime.mcp <model.yaml>`, stdio and streamable HTTP),
  schema connectors (SQLite built-in; PostgreSQL/MySQL/Snowflake via optional
  extras), the e-commerce semantic pack (`semantic_runtime.packs`), the
  SafetyProvider extension point, benchmarks, and docker compose quick start.
- Not yet shipped: JoinLint adapter, plugin system, community packs,
  Snowflake-verified integration, and scripts tooling; do not claim them.
- New runtime behavior must come from the design documents in `docs/`;
  behavior is not invented in code. Docs are updated when implementation
  clarifies or extends them (e.g. new error codes).
- Keep README, rules, and docs aligned with implemented behavior.

# Semantic Runtime

[![CI](https://github.com/Chloride233/semantic-runtime/actions/workflows/ci.yml/badge.svg)](https://github.com/Chloride233/semantic-runtime/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg)](pyproject.toml)

Semantic infrastructure layer for AI Agents: semantic understanding,
context resolution, evidence, and safe execution between models and tools.

> Models provide intelligence. Tools provide capability. Semantic Runtime
> provides understanding.

## Status

- **Shipped:** repository architecture, package foundation, core data models
  (Entity / Relation / Metric / Evidence / Policy), and the YAML model loader
  (Steps 1-3 of the
  [Core Implementation Plan](docs/Semantic%20Runtime%20Core%20Implementation%20Plan.md)).
- **Planned:** registry, graph engine, context resolver, MCP server, and the
  e-commerce demo (Steps 4-7).

## Design Documents

Specifications live in [`docs/`](docs/); the Obsidian index is
[`Semantic Runtime.md`](Semantic%20Runtime.md).

- [PRD](docs/Semantic%20Runtime%20PRD.md) — positioning, problem, vision, scope
- [Protocol Specification](docs/Semantic%20Runtime%20Protocol%20Specification.md) — MCP tools, core objects, protocol principles
- [Reference Architecture](docs/Semantic%20Runtime%20Reference%20Architecture.md) — core modules and integrations
- [Data Model Specification](docs/Semantic%20Runtime%20Data%20Model%20Specification.md) — Entity / Relation / Metric / Evidence / Policy
- [API & MCP Specification](docs/Semantic%20Runtime%20API%20%26%20MCP%20Specification.md) — Python SDK, MCP tools, error model
- [Implementation Blueprint](docs/Semantic%20Runtime%20Implementation%20Blueprint.md) — repository layout, milestones
- [MVP Demo Design](docs/Semantic%20Runtime%20MVP%20Demo%20Design.md) — e-commerce revenue demo
- [Open Source Strategy](docs/Semantic%20Runtime%20Open%20Source%20Strategy.md) — adoption and ecosystem
- [Future Roadmap](docs/Semantic%20Runtime%20Future%20Roadmap.md) — Phase 1-5 roadmap

Superseded v0.1 drafts are archived in [`docs/archive/`](docs/archive/).

## Repository Layout

```
docs/                  design specifications (source of truth)
src/semantic_runtime/  core runtime packages
  core/  models/  loaders/  context/  safety/  evidence/  mcp/
tests/unit/            unit tests
tests/integration/     integration tests (planned with MCP server)
examples/              demo semantic models (planned, Step 3)
scripts/               development tooling (planned)
```

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests
```

The repository is uv-managed for reproducible environments:

```sh
uv sync --extra dev
uv run pytest -q
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for ground rules, setup, and how to
propose changes. All participants agree to the
[Code of Conduct](CODE_OF_CONDUCT.md). Report security issues privately per
[SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).


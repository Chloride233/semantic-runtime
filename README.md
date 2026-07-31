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
  (Entity / Relation / Metric / Evidence / Policy), YAML model loader,
  registry, graph engine, deterministic context resolver, metric dependency
  resolution, schema connectors (SQLite, PostgreSQL, MySQL, Snowflake), SQL
  guardrails, model integrity validation, policy-based operation validation,
  MCP server, and the e-commerce semantic pack (Phases 1-5 of the
  [Future Roadmap](docs/Semantic%20Runtime%20Future%20Roadmap.md)).
- **Planned:** JoinLint adapter integration, plugin system, and community
  packs (Phases 4-5 of the roadmap).

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
- [Post v0.1 Roadmap](docs/Semantic%20Runtime%20Post%20v0.1%20Roadmap.md) — Phase 6-10 execution plan, v0.2-v1.0 evolution
- [Validation and Adoption Plan](docs/Semantic%20Runtime%20Validation%20and%20Adoption%20Plan.md) — real-world validation framework, adoption stages

Superseded v0.1 drafts are archived in [`docs/archive/`](docs/archive/).

## Repository Layout

```
docs/                  design specifications (source of truth)
src/semantic_runtime/  core runtime packages
  core/  models/  loaders/  context/  safety/  evidence/  mcp/  connectors/
tests/unit/            unit tests
tests/integration/     integration tests (MCP server, connectors, benchmarks)
benchmarks/            Level 2 capability + Level 4 safety evaluations
examples/              demo semantic models (e-commerce demo included)
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

## MCP Server

Serve any semantic model to MCP clients over stdio:

```sh
python -m semantic_runtime.mcp                                   # e-commerce pack
python -m semantic_runtime.mcp path/to/semantic_model.yaml       # your model
```

Exposes five tools: `list_entities`, `describe_entity`, `get_metric`,
`resolve_context`, and `validate_operation`. Try it with any MCP client
(e.g. Claude Desktop) pointed at the command above, or connect with the SDK:

```python
from semantic_runtime.core import SemanticRuntime
from semantic_runtime.packs import load_pack

runtime = SemanticRuntime(load_pack("ecommerce"))
context = runtime.resolve_context("Why did revenue drop?")
print(context.matched_terms)  # ["revenue"]
```

## Benchmarks

Evaluation harnesses ship in `benchmarks/` (Phase 6 of the
[Post v0.1 Roadmap](docs/Semantic%20Runtime%20Post%20v0.1%20Roadmap.md)).
Each domain directory contains `model.yaml`, `questions.json`,
`expected_context.json`, and `evaluation.json`; questions are tagged
`semantic_understanding`, `relationship_reasoning`, or `business_analysis`:

```sh
python benchmarks/run_benchmark.py      # P/R/F1 per question and type, PASS/FAIL vs thresholds
python benchmarks/run_safety_eval.py    # Level 4: detection / false positive rate
```

## Docker

```sh
docker build -t semantic-runtime .
docker run --rm -i semantic-runtime            # MCP over stdio, e-commerce pack
```

## Safety

Deterministic safety checks run before any operation; nothing executes
side-effectful SQL. `validate` defaults to deny: policies must explicitly
allow an action, and SQL guardrails reject multi-statements and
`UPDATE`/`DELETE` without `WHERE`:

```python
runtime.validate("execute.query")                       # allow=True (policy)
runtime.validate("execute.query", sql="DELETE FROM orders")  # allow=False, UNSAFE_DELETE_NO_WHERE
runtime.validate_model()                                 # integrity: relations/metrics resolve
```

## Semantic Packs

Built-in domain semantic models ship with the package:

```python
from semantic_runtime.core import SemanticRuntime
from semantic_runtime.packs import load_pack

runtime = SemanticRuntime(load_pack("ecommerce"))  # ecommerce is available
```

Load a local pack directory with `load_pack("name", base_dir=path)`.

## Demo

```sh
python examples/ecommerce/demo.py          # prints the full pipeline
python examples/ecommerce/demo.py --mcp    # serves the same model over MCP
```

## Schema Connectors

Map database schemas into semantic models (tables become entities, foreign
keys become relations). SQLite works out of the box; PostgreSQL and MySQL
require their extras:

```python
from semantic_runtime.connectors import SQLiteConnector, map_schema
from semantic_runtime.core import SemanticRuntime

schema = SQLiteConnector("shop.db").load_schema()
runtime = SemanticRuntime(map_schema(schema))
```

```sh
pip install 'semantic-runtime[postgres]'   # or [mysql]
```

```python
from semantic_runtime.connectors import PostgresConnector, map_schema

schema = PostgresConnector("postgres://user:pass@localhost/shop").load_schema()
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for ground rules, setup, and how to
propose changes. All participants agree to the
[Code of Conduct](CODE_OF_CONDUCT.md). Report security issues privately per
[SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).


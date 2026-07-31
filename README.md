# Semantic Runtime

[![CI](https://github.com/Chloride233/semantic-runtime/actions/workflows/ci.yml/badge.svg)](https://github.com/Chloride233/semantic-runtime/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg)](pyproject.toml)

Semantic infrastructure layer for AI Agents: semantic understanding,
context resolution, evidence, and safe execution between models and tools.

> Models provide intelligence. Tools provide capability. Semantic Runtime
> provides understanding.

## Status

- **Shipped:** core data models (Entity / Relation / Metric / Evidence /
  Policy), YAML model loader, registry, graph engine, deterministic context
  resolver, metric dependency resolution, schema connectors (SQLite,
  PostgreSQL, MySQL, Snowflake), SQL guardrails, model integrity validation,
  policy-based operation validation, SafetyProvider extension point, MCP
  server (stdio + streamable HTTP), five built-in domain packs, the v0.2
  benchmark framework (six question types, SRB score), docker compose quick
  start, and the killer demo.
- **Planned:** JoinLint adapter integration, plugin system, third-party
  community packs, Snowflake-verified integration, Mode B agent evaluation,
  and scripts tooling.

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
- [Benchmark Plan v0.2](docs/Semantic%20Runtime%20Benchmark%20Plan%20v0.2.md) — six question types, SRB scoring, Mode A/B split
- [Validation and Adoption Plan](docs/Semantic%20Runtime%20Validation%20and%20Adoption%20Plan.md) — real-world validation framework, adoption stages

Superseded v0.1 drafts are archived in [`docs/archive/`](docs/archive/).

## Repository Layout

```
docs/                  design specifications (source of truth)
src/semantic_runtime/  core runtime packages
  core/  models/  loaders/  context/  safety/  evidence/  mcp/  connectors/
tests/unit/            unit tests
tests/integration/     integration tests (MCP server, connectors, benchmarks)
benchmarks/            v0.2 framework: runner, scorer, per-domain datasets
examples/              demo semantic models and scripts
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

The v0.2 framework (see the [Benchmark Plan](docs/Semantic%20Runtime%20Benchmark%20Plan%20v0.2.md))
evaluates runtime capability with six question types — semantic
understanding, entity discovery, relationship reasoning, metric dependency,
evidence grounding, and safety validation — and reports a weighted **SRB
score** with a hard safety gate:

```sh
python benchmarks/runner.py --domain ecommerce                 # full run
python benchmarks/runner.py --domain ecommerce --type metric_dependency
python benchmarks/runner.py --domain ecommerce --safety
python benchmarks/runner.py --domain ecommerce --output report.json
```

Legacy entry points remain available: `benchmarks/run_benchmark.py` and
`benchmarks/run_safety_eval.py`.

## Docker

```sh
docker compose up              # serves the e-commerce pack over streamable HTTP on :8000
```

```sh
docker build -t semantic-runtime .
docker run --rm -i semantic-runtime            # MCP over stdio, e-commerce pack
```

For an HTTP endpoint instead of stdio:

```sh
python -m semantic_runtime.mcp --http --port 8000
```

## Quick Start (five minutes)

1. Install: `pip install 'semantic-runtime[dev]'` (or `uv sync --extra dev`)
2. Run the MCP server: `python -m semantic_runtime.mcp` (stdio, e-commerce pack)
3. Wire it into Claude Desktop with
   [examples/claude_desktop_config.example.json](examples/claude_desktop_config.example.json)
   (copy the `mcpServers` block into your `claude_desktop_config.json`); Cursor
   users add the same block to `.cursor/mcp.json`
4. Ask: *"Why did revenue decrease last month?"*
5. Generate the demo database for connector experiments:

```sh
python examples/ecommerce/seed_db.py        # creates examples/ecommerce/shop.db
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

Operation safety runs through a `SafetyProvider` — inject your own to plug
in external engines (JoinLint adapters implement `check_operation`):

```python
from semantic_runtime.core import SemanticRuntime
from semantic_runtime.safety import SafetyReport

class MyProvider:
    def check_operation(self, action, sql):
        return SafetyReport()  # safe

runtime = SemanticRuntime.load("model.yaml", safety_provider=MyProvider())
```

## Semantic Packs

Built-in domain semantic models ship with the package:

```python
from semantic_runtime.core import SemanticRuntime
from semantic_runtime.packs import load_pack

runtime = SemanticRuntime(load_pack("ecommerce"))  # ecommerce, saas, finance, game, healthcare
```

Each pack provides entities, relations, metrics, evidence, and policies.
Load a local community pack directory with `load_pack("name", base_dir=path)`.

## Demo

```sh
python examples/ecommerce/demo.py                      # e-commerce
python examples/ecommerce/demo.py --pack saas          # any built-in pack
python examples/ecommerce/demo.py --pack finance --question "What is the portfolio value?"
python examples/ecommerce/demo.py --mcp                # serve over MCP instead
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


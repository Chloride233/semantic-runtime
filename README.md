# Semantic Runtime

Semantic infrastructure layer for AI Agents: semantic understanding,
context resolution, evidence, and safe execution between models and tools.

> Models provide intelligence. Tools provide capability. Semantic Runtime
> provides understanding.

## Design Documents

The specification set in this repository is the source of truth (v0.1, draft):

- [PRD](Semantic%20Runtime%20PRD.md) — positioning, problem, vision, scope
- [Protocol Specification](Semantic%20Runtime%20Protocol%20Specification.md) — MCP tools, core objects, protocol principles
- [Reference Architecture](Semantic%20Runtime%20Reference%20Architecture.md) — core modules and integrations
- [Data Model Specification](Semantic%20Runtime%20Data%20Model%20Specification.md) — Entity / Relation / Metric / Evidence / Policy
- [API & MCP Specification](Semantic%20Runtime%20API%20%26%20MCP%20Specification.md) — Python SDK, MCP tools, error model
- [Implementation Blueprint](Semantic%20Runtime%20Implementation%20Blueprint.md) — repository layout, milestones
- [Core Implementation Plan](Semantic%20Runtime%20Core%20Implementation%20Plan.md) — 7-step build order
- [MVP Demo Design](Semantic%20Runtime%20MVP%20Demo%20Design.md) — e-commerce revenue demo

## Repository Layout

```
src/semantic_runtime/
  core/       runtime core
  models/     Entity, Relation, Metric, Evidence, Policy
  loaders/    semantic model loading
  context/    context resolver
  safety/     policy engine and execution guardrails
  evidence/   evidence system
  mcp/        MCP server and tools
tests/        unit and integration tests
```

## Development

```sh
uv sync --extra dev
uv run pytest
```

Current status: repository initialized, package skeleton only. Step 2
(data models) is the next milestone.


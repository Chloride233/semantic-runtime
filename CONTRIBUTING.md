# Contributing to Semantic Runtime

Thanks for your interest in Semantic Runtime. The core runtime, MCP server,
domain packs, and v0.2 benchmark framework are shipped; integration
adapters (JoinLint) and the plugin system are not built yet. Contributions
that respect the design below are welcome.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By
participating, you agree to uphold its terms.

## Ground Rules

- **Docs are the source of truth.** All behavior is specified in
  [`docs/`](docs/); implementation must match the design, not the other way
  around. If the docs and code disagree, fix the code or update the docs with
  a design change, never silently.
- **Do not claim unshipped work.** Data models, loaders, registry, graph
  engine, context resolver, MCP server, examples, and scripts are planned
  milestones; do not mark them as shipped in README, docs, or changelogs.
- **No comments in code** unless they explain a non-obvious decision.
- **Keep scope small.** One logical change per PR.

## Development Setup

Requirements: Python 3.12.

```sh
# Install development dependencies
python -m pip install -e '.[dev]'

# Or, with uv (recommended for reproducibility)
uv sync --extra dev
```

## Running Checks

```sh
python -m pytest -q        # tests
python -m ruff check src tests   # lint
```

All tests must pass and lint must be clean before a PR is ready. CI runs the
same checks on every push and pull request.

## Where to Start

- Read the [Core Implementation Plan](docs/Semantic%20Runtime%20Core%20Implementation%20Plan.md)
  and the [Implementation Blueprint](docs/Semantic%20Runtime%20Implementation%20Blueprint.md).
- Check open issues labeled `good first issue`.
- Design documents: PRD, Protocol, Data Model, Reference Architecture under
  [`docs/`](docs/).

## Proposing Changes

1. Fork the repository and create a branch from `main`.
2. Make your change and add tests in `tests/unit/` (integration tests belong
   in `tests/integration/`).
3. Run the checks above.
4. Open a pull request using the [PR template](.github/pull_request_template.md).

## Issues

- **Bug reports:** use the bug report template and include reproduction steps.
- **Feature requests:** use the feature request template; describe the
  problem you are solving, not just a proposed solution.
- If you are not sure whether a feature fits, open an issue and ask before
  building — scope is deliberately narrow.

## Licensing

By contributing you agree that your contributions are licensed under the MIT
License (see [LICENSE](LICENSE)).

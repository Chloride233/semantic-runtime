"""CLI entry point: run the Semantic Runtime MCP server over stdio.

Usage: python -m semantic_runtime.mcp <model.yaml>
"""

from __future__ import annotations

import argparse
import sys

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.mcp.server import create_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="semantic-runtime-mcp",
        description="Serve a Semantic Runtime semantic model over MCP (stdio).",
    )
    parser.add_argument("model", help="path to the semantic model YAML file")
    args = parser.parse_args(argv)

    try:
        runtime = SemanticRuntime.load(args.model)
    except FileNotFoundError:
        print(f"error: model file not found: {args.model}", file=sys.stderr)
        return 1

    server = create_server(runtime)
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

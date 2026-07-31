"""CLI entry point: run the Semantic Runtime MCP server over stdio.

Usage:
    python -m semantic_runtime.mcp <model.yaml>   serve a model file
    python -m semantic_runtime.mcp                serve the e-commerce pack
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.mcp.server import create_server
from semantic_runtime.packs import pack_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="semantic-runtime-mcp",
        description="Serve a Semantic Runtime semantic model over MCP (stdio).",
    )
    parser.add_argument("model", nargs="?", help="path to the semantic model YAML file (defaults to e-commerce pack)")
    args = parser.parse_args(argv)

    model = Path(args.model) if args.model else pack_path("ecommerce")
    try:
        runtime = SemanticRuntime.load(model)
    except FileNotFoundError:
        print(f"error: model file not found: {model}", file=sys.stderr)
        return 1

    server = create_server(runtime)
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

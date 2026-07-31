"""CLI entry point: run the Semantic Runtime MCP server.

Usage:
    python -m semantic_runtime.mcp <model.yaml>        serve a model over stdio
    python -m semantic_runtime.mcp                     serve the e-commerce pack
    python -m semantic_runtime.mcp --http              serve over streamable HTTP
    python -m semantic_runtime.mcp --http --port 9000  custom port
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
        description="Serve a Semantic Runtime semantic model over MCP.",
    )
    parser.add_argument("model", nargs="?", help="path to the semantic model YAML file (defaults to e-commerce pack)")
    parser.add_argument("--http", action="store_true", help="serve over streamable HTTP instead of stdio")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (default: 8000)")
    args = parser.parse_args(argv)

    model = Path(args.model) if args.model else pack_path("ecommerce")
    try:
        runtime = SemanticRuntime.load(model)
    except FileNotFoundError:
        print(f"error: model file not found: {model}", file=sys.stderr)
        return 1

    server = create_server(runtime)
    if args.http:
        import uvicorn

        uvicorn.run(server.streamable_http_app(), host=args.host, port=args.port)
    else:
        server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

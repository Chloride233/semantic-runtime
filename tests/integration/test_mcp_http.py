"""Integration tests: MCP server over streamable HTTP transport."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from mcp.client.streamable_http import streamable_http_client

from semantic_runtime.packs import pack_path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV = {**os.environ.copy(), "PYTHONPATH": str(REPO_ROOT / "src")}


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_http_server(port: int) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "semantic_runtime.mcp",
            str(pack_path("ecommerce")),
            "--http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=ENV,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process


def wait_until_ready(port: int, timeout: float = 15.0) -> None:
    import urllib.error
    import urllib.request

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/mcp", timeout=1)
            return
        except urllib.error.HTTPError:
            return
        except Exception:
            time.sleep(0.2)
    raise TimeoutError("MCP HTTP server did not become ready")


async def test_mcp_http_transport_serves_tools():
    port = free_port()
    process = start_http_server(port)
    try:
        wait_until_ready(port)
        async with streamable_http_client(f"http://127.0.0.1:{port}/mcp") as (read, write, _):
            from mcp import ClientSession

            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert {t.name for t in tools.tools} == {
                    "list_entities",
                    "describe_entity",
                    "get_metric",
                    "resolve_context",
                    "validate_operation",
                }
                result = await session.call_tool("resolve_context", {"question": "Why did revenue drop?"})
                context = json.loads(result.content[0].text)
                assert context["matched_terms"] == ["revenue"]
    finally:
        process.terminate()
        process.wait(timeout=10)

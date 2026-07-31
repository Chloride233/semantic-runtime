"""Integration tests: MCP server interaction with a live runtime."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL_PATH = Path(__file__).resolve().parents[2] / "examples" / "ecommerce" / "semantic_model.yaml"
SRC_PATH = Path(__file__).resolve().parents[2] / "src"


def server_params() -> StdioServerParameters:
    env = {**os.environ.copy(), "PYTHONPATH": str(SRC_PATH)}
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "semantic_runtime.mcp", str(MODEL_PATH)],
        env=env,
    )


async def test_mcp_lists_five_tools():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert names == {
                "list_entities",
                "describe_entity",
                "get_metric",
                "resolve_context",
                "validate_operation",
            }


async def test_mcp_list_entities():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("list_entities", {})
            entities = _collect_items(result)
            assert {e["id"] for e in entities} == {"customer", "order", "product", "payment", "warehouse"}


async def test_mcp_describe_entity_with_relations():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("describe_entity", {"entity_id": "order"})
            payload = json.loads(result.content[0].text)
            assert payload["id"] == "order"
            assert {r["type"] for r in payload["relations"]} == {"places", "contains", "processes"}


async def test_mcp_describe_unknown_entity_returns_error():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("describe_entity", {"entity_id": "ghost"})
            assert result.isError
            assert "ENTITY_NOT_FOUND" in result.content[0].text


async def test_mcp_get_metric():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_metric", {"metric_id": "revenue"})
            metric = json.loads(result.content[0].text)
            assert metric["id"] == "revenue"
            assert metric["entity"] == "order"


async def test_mcp_resolve_context():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("resolve_context", {"question": "Why did revenue drop?"})
            context = json.loads(result.content[0].text)
            assert context["matched_terms"] == ["revenue"]
            assert context["entities"] == []
            assert context["metrics"][0]["id"] == "revenue"


async def test_mcp_validate_operation():
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            allowed = await session.call_tool("validate_operation", {"action": "runtime.query"})
            assert json.loads(allowed.content[0].text)["allow"] is True

            denied = await session.call_tool("validate_operation", {"action": "runtime.mutate"})
            assert json.loads(denied.content[0].text)["allow"] is False


def _collect_items(result) -> list[dict]:
    items: list[dict] = []
    for block in result.content:
        parsed = json.loads(block.text)
        if isinstance(parsed, list):
            items.extend(parsed)
        else:
            items.append(parsed)
    return items

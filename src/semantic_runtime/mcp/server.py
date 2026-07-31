"""MCP server exposing Semantic Runtime capabilities."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from semantic_runtime.core import SemanticRuntime, SemanticRuntimeError

TOOL_NAMES = (
    "list_entities",
    "describe_entity",
    "get_metric",
    "resolve_context",
    "validate_operation",
)


def create_server(runtime: SemanticRuntime, name: str = "Semantic Runtime") -> FastMCP:
    """Build an MCP server bound to a loaded runtime."""
    mcp = FastMCP(name)

    @mcp.tool()
    def list_entities() -> list[dict]:
        """Discover semantic objects (entities, metrics, policies)."""
        return [
            {"id": e.id, "type": e.type, "name": e.name}
            for e in runtime.entities()
        ]

    @mcp.tool()
    def describe_entity(entity_id: str) -> dict:
        """Retrieve entity meaning and its relationships."""
        entity = _safe(runtime.entity, entity_id)
        relations = [
            {
                "id": r.id,
                "type": r.type,
                "source": r.source,
                "target": r.target,
                "description": r.description,
            }
            for r in runtime.relations_for(entity.id)
        ]
        return {
            "id": entity.id,
            "type": entity.type,
            "name": entity.name,
            "description": entity.description,
            "properties": dict(entity.properties),
            "relations": relations,
        }

    @mcp.tool()
    def get_metric(metric_id: str) -> dict:
        """Retrieve a metric definition and its subject entity."""
        metric = _safe(runtime.metric, metric_id)
        return {
            "id": metric.id,
            "definition": metric.definition,
            "entity": metric.entity,
            "description": metric.description,
            "unit": metric.unit,
        }

    @mcp.tool()
    def resolve_context(question: str) -> dict:
        """Resolve a business question into semantic context."""
        context = runtime.resolve_context(question)
        return {
            "question": context.question,
            "matched_terms": context.matched_terms,
            "entities": [
                {"id": e.id, "type": e.type, "name": e.name} for e in context.entities
            ],
            "relations": [
                {"id": r.id, "type": r.type, "source": r.source, "target": r.target}
                for r in context.relations
            ],
            "metrics": [
                {"id": m.id, "definition": m.definition, "entity": m.entity}
                for m in context.metrics
            ],
            "evidences": [
                {"id": e.id, "statement": e.statement, "source": e.source, "status": e.status}
                for e in context.evidences
            ],
        }

    @mcp.tool()
    def validate_operation(action: str) -> dict:
        """Check whether an operation is allowed by policy (default deny)."""
        decision = runtime.validate(action)
        return {
            "allow": decision.allow,
            "action": decision.action,
            "policy_id": decision.policy_id,
            "reason": decision.reason,
        }

    return mcp


def _safe(lookup, model_id):
    try:
        return lookup(model_id)
    except SemanticRuntimeError as exc:
        raise ValueError(f"{exc.code}: {exc.message}") from exc

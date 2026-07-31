"""SemanticRuntime: the core runtime facade (load, access, resolve, validate)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from semantic_runtime.context.resolver import Context, ContextResolver
from semantic_runtime.core.errors import ModelNotLoadedError
from semantic_runtime.core.graph import GraphEngine
from semantic_runtime.core.registry import Registry
from semantic_runtime.loaders import load, loads
from semantic_runtime.loaders.yaml_loader import SemanticModel
from semantic_runtime.models import Entity, Evidence, Metric, Policy, Relation


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """Outcome of validating an operation against policies."""

    allow: bool
    action: str
    policy_id: str | None
    reason: str


class SemanticRuntime:
    """Facade over registry, graph engine, and context resolver."""

    def __init__(self, models: Iterable[SemanticModel] | None = None) -> None:
        self._models = list(models or [])
        self._registry = Registry(self._models)
        self._graph = GraphEngine(self._registry)
        self._resolver = ContextResolver(self._registry, self._graph)

    @classmethod
    def load(cls, path: str | Path) -> SemanticRuntime:
        """Load a semantic model from a YAML file."""
        return cls(load(path))

    @classmethod
    def from_yaml(cls, text: str) -> SemanticRuntime:
        """Build a runtime from YAML text."""
        return cls(loads(text))

    def entity(self, entity_id: str) -> Entity:
        return self._registry.entity(entity_id)

    def relation(self, relation_id: str) -> Relation:
        return self._registry.relation(relation_id)

    def metric(self, metric_id: str) -> Metric:
        return self._registry.metric(metric_id)

    def evidence(self, evidence_id: str) -> Evidence:
        return self._registry.evidence(evidence_id)

    def policy(self, policy_id: str) -> Policy:
        return self._registry.policy(policy_id)

    def entities(self) -> list[Entity]:
        return self._registry.entities()

    def relations(self) -> list[Relation]:
        return self._registry.relations()

    def relations_for(self, entity_id: str) -> list[Relation]:
        """Relations touching an entity, both outgoing and incoming."""
        return self._graph.relations_from(entity_id) + self._graph.relations_to(entity_id)

    def metrics(self) -> list[Metric]:
        return self._registry.metrics()

    def evidences(self) -> list[Evidence]:
        return self._registry.evidences()

    def policies(self) -> list[Policy]:
        return self._registry.policies()

    def resolve_context(self, question: str) -> Context:
        """Resolve a business question into semantic context."""
        return self._resolver.resolve(question)

    def metric_dependencies(self, metric_id: str) -> list[Metric]:
        """Metrics this metric transitively depends on, in compute order."""
        self.metric(metric_id)
        seen: set[str] = {metric_id}
        ordered: list[Metric] = []

        def visit(current_id: str) -> None:
            for dependency_id in self._registry.metric(current_id).depends_on:
                if dependency_id in seen:
                    continue
                seen.add(dependency_id)
                visit(dependency_id)
                ordered.append(self._registry.metric(dependency_id))

        visit(metric_id)
        return ordered

    def validate(self, action: str) -> PolicyDecision:
        """Check whether an operation is allowed by policy; default deny."""
        if len(self._registry) == 0:
            raise ModelNotLoadedError("no semantic model is loaded")
        matching = [p for p in self._registry.policies() if p.action == action]
        if not matching:
            return PolicyDecision(False, action, None, f"no policy matches action {action!r}; default deny")
        denied = [p for p in matching if p.effect == "deny"]
        if denied:
            return PolicyDecision(False, action, denied[0].id, f"denied by policy {denied[0].id!r}")
        allowed = matching[0]
        return PolicyDecision(True, action, allowed.id, f"allowed by policy {allowed.id!r}")

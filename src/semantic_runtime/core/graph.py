"""Graph engine: relation lookup, traversal, and dependency discovery."""

from __future__ import annotations

from collections import deque

from semantic_runtime.core.registry import Registry
from semantic_runtime.models import Relation


class GraphEngine:
    """Traverses semantic relations backed by a registry."""

    def __init__(self, registry: Registry) -> None:
        self._registry = registry
        self._outgoing: dict[str, list[Relation]] = {}
        self._incoming: dict[str, list[Relation]] = {}
        for relation in registry.relations():
            self._add(relation)

    def relations_from(self, entity_id: str) -> list[Relation]:
        self._require_entity(entity_id)
        return list(self._outgoing.get(entity_id, []))

    def relations_to(self, entity_id: str) -> list[Relation]:
        self._require_entity(entity_id)
        return list(self._incoming.get(entity_id, []))

    def neighbors(self, entity_id: str, direction: str = "outgoing") -> list[str]:
        self._require_entity(entity_id)
        relations: list[Relation] = []
        if direction in ("outgoing", "both"):
            relations.extend(self._outgoing.get(entity_id, []))
        if direction in ("incoming", "both"):
            relations.extend(self._incoming.get(entity_id, []))
        seen: list[str] = []
        for relation in relations:
            other = relation.target if relation.source == entity_id else relation.source
            if other not in seen:
                seen.append(other)
        return seen

    def traverse(self, entity_id: str, max_depth: int | None = None, direction: str = "outgoing") -> list[str]:
        """Breadth-first traversal returning entity ids in discovery order."""
        self._require_entity(entity_id)
        visited = {entity_id}
        queue: deque[tuple[str, int]] = deque([(entity_id, 0)])
        ordered: list[str] = []
        while queue:
            current, depth = queue.popleft()
            if max_depth is not None and depth >= max_depth:
                continue
            for neighbor in self.neighbors(current, direction):
                if neighbor not in visited:
                    visited.add(neighbor)
                    ordered.append(neighbor)
                    queue.append((neighbor, depth + 1))
        return ordered

    def dependencies(self, entity_id: str) -> list[str]:
        """Entities this entity relies on (transitive closure over incoming edges)."""
        self._require_entity(entity_id)
        return self.traverse(entity_id, direction="incoming")

    def dependents(self, entity_id: str) -> list[str]:
        """Entities that rely on this entity (transitive closure over outgoing edges)."""
        self._require_entity(entity_id)
        return self.traverse(entity_id, direction="outgoing")

    def _add(self, relation: Relation) -> None:
        self._outgoing.setdefault(relation.source, []).append(relation)
        self._incoming.setdefault(relation.target, []).append(relation)

    def _require_entity(self, entity_id: str) -> None:
        self._registry.entity(entity_id)

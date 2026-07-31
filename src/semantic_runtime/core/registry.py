"""Registry: stores and retrieves semantic models."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from semantic_runtime.core.errors import DuplicateModelError, EntityNotFoundError, RelationNotFoundError
from semantic_runtime.loaders.yaml_loader import SemanticModel
from semantic_runtime.models import Entity, Evidence, Metric, Policy, Relation


class Registry:
    """In-memory store of semantic models keyed by kind and id."""

    def __init__(self, models: Iterable[SemanticModel] | None = None) -> None:
        self._entities: dict[str, Entity] = {}
        self._relations: dict[str, Relation] = {}
        self._metrics: dict[str, Metric] = {}
        self._evidences: dict[str, Evidence] = {}
        self._policies: dict[str, Policy] = {}
        if models is not None:
            self.register_all(models)

    def register(self, model: SemanticModel) -> None:
        kind, store, model_id = self._kind_of(model)
        if model_id in store:
            raise DuplicateModelError(f"{kind} {model_id!r} is already registered")
        store[model_id] = model

    def register_all(self, models: Iterable[SemanticModel]) -> None:
        for model in models:
            self.register(model)

    def entity(self, entity_id: str) -> Entity:
        try:
            return self._entities[entity_id]
        except KeyError:
            raise EntityNotFoundError(f"entity {entity_id!r} not found") from None

    def relation(self, relation_id: str) -> Relation:
        try:
            return self._relations[relation_id]
        except KeyError:
            raise RelationNotFoundError(f"relation {relation_id!r} not found") from None

    def metric(self, metric_id: str) -> Metric:
        try:
            return self._metrics[metric_id]
        except KeyError:
            raise EntityNotFoundError(f"metric {metric_id!r} not found") from None

    def evidence(self, evidence_id: str) -> Evidence:
        try:
            return self._evidences[evidence_id]
        except KeyError:
            raise EntityNotFoundError(f"evidence {evidence_id!r} not found") from None

    def policy(self, policy_id: str) -> Policy:
        try:
            return self._policies[policy_id]
        except KeyError:
            raise EntityNotFoundError(f"policy {policy_id!r} not found") from None

    def entities(self) -> list[Entity]:
        return list(self._entities.values())

    def relations(self) -> list[Relation]:
        return list(self._relations.values())

    def metrics(self) -> list[Metric]:
        return list(self._metrics.values())

    def evidences(self) -> list[Evidence]:
        return list(self._evidences.values())

    def policies(self) -> list[Policy]:
        return list(self._policies.values())

    def __iter__(self) -> Iterator[SemanticModel]:
        yield from self._entities.values()
        yield from self._relations.values()
        yield from self._metrics.values()
        yield from self._evidences.values()
        yield from self._policies.values()

    def __len__(self) -> int:
        return sum(len(store) for store in self._stores())

    def _kind_of(self, model: SemanticModel) -> tuple[str, dict, str]:
        if isinstance(model, Entity):
            return "entity", self._entities, model.id
        if isinstance(model, Relation):
            return "relation", self._relations, model.id
        if isinstance(model, Metric):
            return "metric", self._metrics, model.id
        if isinstance(model, Evidence):
            return "evidence", self._evidences, model.id
        if isinstance(model, Policy):
            return "policy", self._policies, model.id
        raise TypeError(f"unsupported model type {type(model).__name__}")

    def _stores(self) -> tuple[dict, dict, dict, dict, dict]:
        return self._entities, self._relations, self._metrics, self._evidences, self._policies

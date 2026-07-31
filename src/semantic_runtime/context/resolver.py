"""Context resolver: deterministic semantic lookup for business questions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from semantic_runtime.models import Entity, Evidence, Metric, Relation

if TYPE_CHECKING:
    from semantic_runtime.core.graph import GraphEngine
    from semantic_runtime.core.registry import Registry

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)
_STOPWORDS = {
    "why", "what", "when", "where", "who", "how", "did", "does", "do", "is",
    "are", "was", "were", "the", "a", "an", "of", "for", "in", "on", "to",
    "and", "or", "with", "from", "by", "at", "it", "its", "this", "that",
}


@dataclass(frozen=True, slots=True)
class Context:
    """Semantic context resolved from a business question."""

    question: str
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    evidences: list[Evidence] = field(default_factory=list)
    matched_terms: list[str] = field(default_factory=list)


class ContextResolver:
    """Resolves questions by deterministic keyword matching; no LLM."""

    def __init__(self, registry: Registry, graph: GraphEngine) -> None:
        self._registry = registry
        self._graph = graph

    def resolve(self, question: str) -> Context:
        from semantic_runtime.core.errors import ModelNotLoadedError

        if len(self._registry) == 0:
            raise ModelNotLoadedError("no semantic model is loaded")

        terms = self._terms(question)
        matched_entities: list[Entity] = []
        matched_metrics: list[Metric] = []
        matched_evidences: list[Evidence] = []
        matched_terms: list[str] = []

        for entity in self._registry.entities():
            hits = self._score(entity.id, entity.name, entity.description, terms=terms)
            if hits:
                matched_entities.append(entity)
                matched_terms.extend(hits)

        for metric in self._registry.metrics():
            hits = self._score(metric.id, metric.definition, metric.description, terms=terms)
            if hits:
                matched_metrics.append(metric)
                matched_terms.extend(hits)

        for evidence in self._registry.evidences():
            hits = self._score(evidence.id, evidence.statement, evidence.source, terms=terms)
            if hits:
                matched_evidences.append(evidence)
                matched_terms.extend(hits)

        related: dict[str, Relation] = {}
        for entity in matched_entities:
            for relation in self._graph.relations_from(entity.id) + self._graph.relations_to(entity.id):
                related[relation.id] = relation

        return Context(
            question=question,
            entities=matched_entities,
            relations=list(related.values()),
            metrics=matched_metrics,
            evidences=matched_evidences,
            matched_terms=sorted(set(matched_terms)),
        )

    @staticmethod
    def _terms(question: str) -> set[str]:
        return {t for t in _TOKEN_RE.findall(question.lower()) if t not in _STOPWORDS}

    @staticmethod
    def _variants(term: str) -> list[str]:
        forms = [term]
        if len(term) > 3 and term.endswith("ies"):
            forms.append(term[:-3] + "y")
        elif len(term) > 2 and term.endswith("es"):
            forms.append(term[:-2])
        elif len(term) > 1 and term.endswith("s"):
            forms.append(term[:-1])
        return forms

    @staticmethod
    def _score(*fields: str | None, terms: set[str]) -> list[str]:
        haystack = " ".join(f for f in fields if f).lower()
        return [
            term
            for term in terms
            if any(re.search(rf"\b{re.escape(variant)}\b", haystack) for variant in ContextResolver._variants(term))
        ]

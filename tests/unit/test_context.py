"""Unit tests for the context resolver."""

import pytest

from semantic_runtime.context import ContextResolver
from semantic_runtime.core.errors import ModelNotLoadedError
from semantic_runtime.core.graph import GraphEngine
from semantic_runtime.core.registry import Registry
from semantic_runtime.models import Entity, Evidence, Metric, Relation

CUSTOMER = Entity(id="customer", type="business_object", description="A customer who places orders")
ORDER = Entity(id="order", type="business_object", description="A placed order")
CATEGORY = Entity(id="category", type="business_object", description="A product category")
REVENUE = Metric(id="revenue", definition="completed payment minus refunds", entity="order")
EVIDENCE = Evidence(id="ev-1", statement="Revenue dropped 12% in Q2", source="sql:revenue_report")
PLACES = Relation(source="customer", target="order", type="places")


def build_resolver():
    registry = Registry([CUSTOMER, ORDER, CATEGORY, REVENUE, EVIDENCE, PLACES])
    return ContextResolver(registry, GraphEngine(registry))


def test_resolve_matches_entity_and_metric():
    context = build_resolver().resolve("Why did revenue drop for the customer?")
    assert {e.id for e in context.entities} == {"customer"}
    assert {m.id for m in context.metrics} == {"revenue"}
    assert context.matched_terms == ["customer", "revenue"]


def test_resolve_includes_related_relations():
    context = build_resolver().resolve("What happens to customer orders?")
    assert {r.id for r in context.relations} == {"customer:places:order"}


def test_resolve_matches_evidence():
    context = build_resolver().resolve("Show evidence for the Q2 revenue drop")
    assert {e.id for e in context.evidences} == {"ev-1"}


def test_resolve_no_match_returns_empty_context():
    context = build_resolver().resolve("What about satellites?")
    assert context.entities == []
    assert context.metrics == []
    assert context.matched_terms == []


def test_resolve_stopwords_ignored():
    context = build_resolver().resolve("why is the revenue")
    assert context.matched_terms == ["revenue"]


def test_resolve_plural_terms_match_singular_fields():
    context = build_resolver().resolve("How are customers connected to payments?")
    assert {e.id for e in context.entities} == {"customer"}
    assert {m.id for m in context.metrics} == {"revenue"}
    assert {r.id for r in context.relations} == {"customer:places:order"}


def test_resolve_ies_plural_maps_to_y():
    context = build_resolver().resolve("Which categories exist?")
    assert {e.id for e in context.entities} == {"category"}


def test_resolve_without_model_raises():
    with pytest.raises(ModelNotLoadedError):
        ContextResolver(Registry(), GraphEngine(Registry())).resolve("revenue")

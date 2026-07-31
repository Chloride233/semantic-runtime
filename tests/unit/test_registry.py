"""Unit tests for the semantic model registry."""

import pytest

from semantic_runtime.core.errors import DuplicateModelError, EntityNotFoundError, RelationNotFoundError
from semantic_runtime.core.registry import Registry
from semantic_runtime.models import Entity, Evidence, Metric, Policy, Relation

CUSTOMER = Entity(id="customer", type="business_object", description="A customer who places orders")
ORDER = Entity(id="order", type="business_object", description="A placed order")
PLACES = Relation(source="customer", target="order", type="places", description="A customer places an order")
REVENUE = Metric(id="revenue", definition="completed payment minus refunds", entity="order")
EVIDENCE = Evidence(id="ev-1", statement="Revenue dropped 12%", source="sql:report", status="verified")
ALLOW_QUERY = Policy(id="p-query", action="execute.query", effect="allow")


def test_register_and_retrieve():
    registry = Registry([CUSTOMER, ORDER, PLACES, REVENUE, EVIDENCE, ALLOW_QUERY])
    assert len(registry) == 6
    assert registry.entity("customer") == CUSTOMER
    assert registry.relation("customer:places:order") == PLACES
    assert registry.metric("revenue") == REVENUE
    assert registry.evidence("ev-1") == EVIDENCE
    assert registry.policy("p-query") == ALLOW_QUERY


def test_register_empty():
    registry = Registry()
    assert len(registry) == 0


def test_duplicate_registration_raises():
    registry = Registry([CUSTOMER])
    with pytest.raises(DuplicateModelError):
        registry.register(Entity(id="customer", type="business_object"))


def test_entity_not_found():
    with pytest.raises(EntityNotFoundError) as exc:
        Registry().entity("missing")
    assert exc.value.code == "ENTITY_NOT_FOUND"


def test_relation_not_found():
    with pytest.raises(RelationNotFoundError) as exc:
        Registry([CUSTOMER]).relation("missing")
    assert exc.value.code == "RELATION_NOT_FOUND"


def test_unknown_metric_raises_entity_not_found():
    with pytest.raises(EntityNotFoundError):
        Registry().metric("nope")


def test_collections():
    registry = Registry([CUSTOMER, ORDER, PLACES])
    assert [e.id for e in registry.entities()] == ["customer", "order"]
    assert [r.id for r in registry.relations()] == ["customer:places:order"]


def test_iteration_yields_all_kinds():
    registry = Registry([CUSTOMER, PLACES, REVENUE])
    assert {type(m).__name__ for m in registry} == {"Entity", "Relation", "Metric"}

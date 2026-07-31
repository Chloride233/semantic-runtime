"""Unit tests for the graph engine."""

import pytest

from semantic_runtime.core.errors import EntityNotFoundError
from semantic_runtime.core.graph import GraphEngine
from semantic_runtime.core.registry import Registry
from semantic_runtime.models import Entity, Relation

CUSTOMER = Entity(id="customer", type="business_object")
ORDER = Entity(id="order", type="business_object")
PRODUCT = Entity(id="product", type="business_object")
WAREHOUSE = Entity(id="warehouse", type="business_object")
EMPLOYEE = Entity(id="employee", type="business_object")

CUSTOMER_PLACES_ORDER = Relation(source="customer", target="order", type="places")
ORDER_CONTAINS_PRODUCT = Relation(source="order", type="contains", target="product")
PRODUCT_STORED_IN = Relation(source="product", type="stored_in", target="warehouse")
EMPLOYEE_MANAGES_ORDER = Relation(source="employee", type="manages", target="order")


def build_graph(*relations: Relation) -> GraphEngine:
    registry = Registry(
        [CUSTOMER, ORDER, PRODUCT, WAREHOUSE, EMPLOYEE, *relations]
    )
    return GraphEngine(registry)


def test_relations_from():
    graph = build_graph(CUSTOMER_PLACES_ORDER, ORDER_CONTAINS_PRODUCT)
    assert [r.target for r in graph.relations_from("customer")] == ["order"]
    assert graph.relations_from("product") == []


def test_relations_to():
    graph = build_graph(CUSTOMER_PLACES_ORDER, ORDER_CONTAINS_PRODUCT)
    assert [r.source for r in graph.relations_to("order")] == ["customer"]


def test_neighbors_outgoing_and_incoming():
    graph = build_graph(CUSTOMER_PLACES_ORDER, EMPLOYEE_MANAGES_ORDER)
    assert graph.neighbors("order", "incoming") == ["customer", "employee"]
    assert graph.neighbors("order", "outgoing") == []
    assert graph.neighbors("order", "both") == ["customer", "employee"]


def test_traverse_breadth_first():
    graph = build_graph(CUSTOMER_PLACES_ORDER, ORDER_CONTAINS_PRODUCT, PRODUCT_STORED_IN)
    assert graph.traverse("customer") == ["order", "product", "warehouse"]


def test_traverse_max_depth():
    graph = build_graph(CUSTOMER_PLACES_ORDER, ORDER_CONTAINS_PRODUCT, PRODUCT_STORED_IN)
    assert graph.traverse("customer", max_depth=1) == ["order"]
    assert graph.traverse("customer", max_depth=2) == ["order", "product"]


def test_traverse_no_cycles_loop_forever():
    cyclic = Relation(source="a", target="b", type="linked")
    registry = Registry([Entity(id="a", type="x"), Entity(id="b", type="x"), cyclic])
    graph = GraphEngine(registry)
    assert graph.traverse("a", max_depth=5) == ["b"]


def test_dependencies():
    graph = build_graph(CUSTOMER_PLACES_ORDER, ORDER_CONTAINS_PRODUCT, PRODUCT_STORED_IN)
    assert graph.dependencies("product") == ["order", "customer"]
    assert graph.dependents("customer") == ["order", "product", "warehouse"]


def test_dependents_via_shared_target():
    graph = build_graph(EMPLOYEE_MANAGES_ORDER, CUSTOMER_PLACES_ORDER)
    assert graph.dependents("order") == []


def test_unknown_entity_raises():
    graph = build_graph(CUSTOMER_PLACES_ORDER)
    with pytest.raises(EntityNotFoundError):
        graph.traverse("ghost")
    with pytest.raises(EntityNotFoundError):
        graph.neighbors("ghost")

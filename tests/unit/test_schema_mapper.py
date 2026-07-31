"""Unit tests for schema mapping."""

from semantic_runtime.connectors.schema import (
    ColumnSchema,
    DatabaseSchema,
    ForeignKey,
    TableSchema,
)
from semantic_runtime.connectors.schema_mapper import map_schema
from semantic_runtime.models import Entity, Relation

ORDERS = TableSchema(
    name="orders",
    columns=(
        ColumnSchema(name="id", type="INTEGER", nullable=False, primary_key=True),
        ColumnSchema(name="customer_id", type="INTEGER", nullable=False, primary_key=False),
    ),
    foreign_keys=(ForeignKey(column="customer_id", referenced_table="customers", referenced_column="id"),),
)
CUSTOMERS = TableSchema(
    name="customers",
    columns=(ColumnSchema(name="id", type="INTEGER", nullable=False, primary_key=True),),
)


def test_map_schema_creates_entities_per_table():
    models = map_schema(DatabaseSchema(tables=(ORDERS, CUSTOMERS)))
    entities = [m for m in models if isinstance(m, Entity)]
    assert {e.id for e in entities} == {"orders", "customers"}
    orders = next(e for e in entities if e.id == "orders")
    assert orders.type == "table"
    assert orders.properties["primary_key"] == ["id"]
    assert orders.properties["columns"] == ["id", "customer_id"]


def test_map_schema_creates_relation_per_foreign_key():
    models = map_schema(DatabaseSchema(tables=(ORDERS, CUSTOMERS)))
    relations = [m for m in models if isinstance(m, Relation)]
    assert len(relations) == 1
    relation = relations[0]
    assert relation.source == "orders"
    assert relation.target == "customers"
    assert relation.type == "references"
    assert relation.properties["column"] == "customer_id"


def test_map_schema_no_foreign_keys():
    models = map_schema(DatabaseSchema(tables=(CUSTOMERS,)))
    assert all(isinstance(m, Entity) for m in models)

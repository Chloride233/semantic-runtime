"""Integration tests: SQLite connector with a live in-memory database."""

import sqlite3

from semantic_runtime.connectors import SQLiteConnector
from semantic_runtime.connectors.schema import ForeignKey, TableSchema
from semantic_runtime.connectors.schema_mapper import map_schema
from semantic_runtime.core import SemanticRuntime
from semantic_runtime.models import Entity, Relation


def build_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            total REAL NOT NULL
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
    )
    return connection


def test_sqlite_connector_discovers_schema():
    schema = SQLiteConnector(build_database()).load_schema()
    assert {t.name for t in schema.tables} == {"customers", "orders", "products"}

    orders = schema.table("orders")
    assert isinstance(orders, TableSchema)
    assert [c.name for c in orders.columns] == ["id", "customer_id", "total"]
    assert orders.foreign_keys == (
        ForeignKey(column="customer_id", referenced_table="customers", referenced_column="id"),
    )


def test_sqlite_connector_round_trip_into_runtime():
    schema = SQLiteConnector(build_database()).load_schema()
    models = map_schema(schema)
    runtime = SemanticRuntime(models)

    assert isinstance(runtime.entity("orders"), Entity)
    assert isinstance(runtime.entity("products"), Entity)
    relation = runtime.relation("orders:references:customers")
    assert isinstance(relation, Relation)
    assert relation.description == "orders.customer_id references customers.id"

    context = runtime.resolve_context("Which table references customers?")
    assert "customers" in {e.id for e in context.entities}
    assert {r.id for r in context.relations} == {"orders:references:customers"}


def test_sqlite_connector_from_file(tmp_path):
    path = tmp_path / "shop.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE items (id INTEGER PRIMARY KEY)")
    connection.close()

    schema = SQLiteConnector(path).load_schema()
    assert {t.name for t in schema.tables} == {"items"}

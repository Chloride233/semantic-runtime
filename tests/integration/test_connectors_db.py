"""Integration tests for PostgreSQL/MySQL connectors.

Skipped unless TEST_POSTGRES_URL / TEST_MYSQL_URL point at live databases.
"""

import os

import pytest

from semantic_runtime.connectors import MySQLConnector, PostgresConnector

pytestmark = pytest.mark.integration

POSTGRES_URL = os.environ.get("TEST_POSTGRES_URL")
MYSQL_URL = os.environ.get("TEST_MYSQL_URL")


def _require_env(name: str, value: str | None) -> str:
    if not value:
        pytest.skip(f"set {name} to enable this test")
    return value


@pytest.mark.skipif(not POSTGRES_URL, reason="TEST_POSTGRES_URL not set")
def test_postgres_connector_discovers_schema():
    import psycopg

    with psycopg.connect(_require_env("TEST_POSTGRES_URL", POSTGRES_URL)) as connection:
        connection.execute("DROP TABLE IF EXISTS orders")
        connection.execute("DROP TABLE IF EXISTS customers")
        connection.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        connection.execute(
            "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id))"
        )
        connection.commit()

    schema = PostgresConnector(_require_env("TEST_POSTGRES_URL", POSTGRES_URL)).load_schema()
    assert {t.name for t in schema.tables} == {"customers", "orders"}
    orders = schema.table("orders")
    assert len(orders.foreign_keys) == 1
    assert orders.foreign_keys[0].referenced_table == "customers"


@pytest.mark.skipif(not MYSQL_URL, reason="TEST_MYSQL_URL not set")
def test_mysql_connector_discovers_schema():
    dsn = _require_env("TEST_MYSQL_URL", MYSQL_URL)
    connector = MySQLConnector(dsn)
    import pymysql

    connection = pymysql.connect(
        host=connector._host,
        port=connector._port,
        user=connector._user,
        password=connector._password,
        database=connector._database,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS customers")
            cursor.execute("CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(50) NOT NULL)")
            cursor.execute(
                "CREATE TABLE orders (id INT PRIMARY KEY, customer_id INT, "
                "FOREIGN KEY (customer_id) REFERENCES customers(id))"
            )
        connection.commit()
    finally:
        connection.close()

    schema = connector.load_schema()
    assert {t.name for t in schema.tables} == {"customers", "orders"}
    orders = schema.table("orders")
    assert len(orders.foreign_keys) == 1
    assert orders.foreign_keys[0].referenced_table == "customers"

"""Unit tests for connector DSN parsing and driver guards."""

import pytest

from semantic_runtime.connectors.mysql import MySQLConnector
from semantic_runtime.connectors.postgres import PostgresConnector


def test_mysql_dsn_parsing():
    connector = MySQLConnector("mysql://alice:secret@db.example.com:3307/shop")
    assert connector._host == "db.example.com"
    assert connector._port == 3307
    assert connector._user == "alice"
    assert connector._password == "secret"
    assert connector._database == "shop"


def test_mysql_dsn_defaults():
    connector = MySQLConnector("mysql://root@localhost/shop")
    assert connector._host == "localhost"
    assert connector._port == 3306
    assert connector._user == "root"
    assert connector._database == "shop"


def test_mysql_dsn_rejects_other_schemes():
    with pytest.raises(ValueError, match="mysql://"):
        MySQLConnector("postgres://user@host/db")


def test_postgres_requires_driver():
    connector = PostgresConnector("postgres://user:pass@localhost/db")
    with pytest.raises(ImportError, match="postgres"):
        connector.load_schema()


def test_mysql_requires_driver():
    connector = MySQLConnector("mysql://root@localhost/shop")
    with pytest.raises(ImportError, match="mysql"):
        connector.load_schema()

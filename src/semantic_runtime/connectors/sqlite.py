"""SQLite schema connector (stdlib only)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from semantic_runtime.connectors.schema import (
    ColumnSchema,
    DatabaseSchema,
    ForeignKey,
    TableSchema,
)


class SQLiteConnector:
    """Discovers the schema of a SQLite database."""

    def __init__(self, database: str | Path | sqlite3.Connection) -> None:
        self._connection: sqlite3.Connection | None = None
        if isinstance(database, sqlite3.Connection):
            self._connection = database
        self._database = str(database) if not isinstance(database, sqlite3.Connection) else None

    def load_schema(self) -> DatabaseSchema:
        connection = self._connection or sqlite3.connect(self._database)
        try:
            tables = tuple(self._load_table(connection, row[0]) for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            ))
        finally:
            if self._connection is None:
                connection.close()
        return DatabaseSchema(tables=tables)

    def _load_table(self, connection: sqlite3.Connection, name: str) -> TableSchema:
        columns = tuple(
            ColumnSchema(
                name=row[1],
                type=row[2],
                nullable=not bool(row[3]),
                primary_key=bool(row[5]),
            )
            for row in connection.execute(f"PRAGMA table_info({_quote(name)})")
        )
        foreign_keys = tuple(
            ForeignKey(
                column=row[3],
                referenced_table=row[2],
                referenced_column=row[4],
            )
            for row in connection.execute(f"PRAGMA foreign_key_list({_quote(name)})")
        )
        return TableSchema(name=name, columns=columns, foreign_keys=foreign_keys)


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'

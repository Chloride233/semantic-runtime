"""PostgreSQL schema connector (requires the 'postgres' extra)."""

from __future__ import annotations

from semantic_runtime.connectors.schema import (
    ColumnSchema,
    DatabaseSchema,
    ForeignKey,
    TableSchema,
)

_SCHEMA_SQL = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name
"""

_COLUMNS_SQL = """
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = %s
ORDER BY ordinal_position
"""

_PRIMARY_KEY_SQL = """
SELECT kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
WHERE tc.table_schema = 'public' AND tc.table_name = %s
  AND tc.constraint_type = 'PRIMARY KEY'
ORDER BY kcu.ordinal_position
"""

_FOREIGN_KEYS_SQL = """
SELECT kcu.column_name, ccu.table_name, ccu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name
 AND ccu.table_schema = tc.table_schema
WHERE tc.table_schema = 'public' AND tc.table_name = %s
  AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY kcu.ordinal_position
"""


class PostgresConnector:
    """Discovers the schema of a PostgreSQL database."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def load_schema(self) -> DatabaseSchema:
        try:
            import psycopg
        except ImportError as exc:
            raise ImportError(
                "PostgresConnector requires the 'postgres' extra: "
                "install 'semantic-runtime[postgres]'"
            ) from exc

        with psycopg.connect(self._dsn) as connection:
            tables = tuple(
                TableSchema(
                    name=row[0],
                    columns=self._columns(connection, row[0]),
                    foreign_keys=self._foreign_keys(connection, row[0]),
                )
                for row in connection.execute(_SCHEMA_SQL)
            )
        return DatabaseSchema(tables=tables)

    def _columns(self, connection, table: str) -> tuple[ColumnSchema, ...]:
        primary_keys = {row[0] for row in connection.execute(_PRIMARY_KEY_SQL, (table,))}
        return tuple(
            ColumnSchema(
                name=row[0],
                type=row[1],
                nullable=row[2] == "YES",
                primary_key=row[0] in primary_keys,
            )
            for row in connection.execute(_COLUMNS_SQL, (table,))
        )

    def _foreign_keys(self, connection, table: str) -> tuple[ForeignKey, ...]:
        return tuple(
            ForeignKey(column=row[0], referenced_table=row[1], referenced_column=row[2])
            for row in connection.execute(_FOREIGN_KEYS_SQL, (table,))
        )

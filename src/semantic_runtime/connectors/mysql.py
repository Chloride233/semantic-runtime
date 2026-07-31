"""MySQL schema connector (requires the 'mysql' extra)."""

from __future__ import annotations

from urllib.parse import urlparse

from semantic_runtime.connectors.schema import (
    ColumnSchema,
    DatabaseSchema,
    ForeignKey,
    TableSchema,
)

_SCHEMA_SQL = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s AND table_type = 'BASE TABLE'
ORDER BY table_name
"""

_COLUMNS_SQL = """
SELECT column_name, column_type, is_nullable, column_key
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
ORDER BY ordinal_position
"""

_FOREIGN_KEYS_SQL = """
SELECT kcu.column_name, kcu.referenced_table_name, kcu.referenced_column_name
FROM information_schema.key_column_usage kcu
WHERE kcu.table_schema = %s AND kcu.table_name = %s
  AND kcu.referenced_table_name IS NOT NULL
ORDER BY kcu.ordinal_position
"""


class MySQLConnector:
    """Discovers the schema of a MySQL database from a DSN."""

    def __init__(self, dsn: str) -> None:
        parsed = urlparse(dsn)
        if parsed.scheme != "mysql":
            raise ValueError(f"expected a mysql:// DSN, got {parsed.scheme!r}")
        self._host = parsed.hostname or "localhost"
        self._port = parsed.port or 3306
        self._user = parsed.username or ""
        self._password = parsed.password or ""
        self._database = parsed.path.lstrip("/")

    def load_schema(self) -> DatabaseSchema:
        try:
            import pymysql
        except ImportError as exc:
            raise ImportError(
                "MySQLConnector requires the 'mysql' extra: "
                "install 'semantic-runtime[mysql]'"
            ) from exc

        connection = pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(_SCHEMA_SQL, (self._database,))
                tables = tuple(
                    TableSchema(
                        name=row[0],
                        columns=self._columns(cursor, row[0]),
                        foreign_keys=self._foreign_keys(cursor, row[0]),
                    )
                    for row in cursor.fetchall()
                )
        finally:
            connection.close()
        return DatabaseSchema(tables=tables)

    def _columns(self, cursor, table: str) -> tuple[ColumnSchema, ...]:
        cursor.execute(_COLUMNS_SQL, (self._database, table))
        return tuple(
            ColumnSchema(
                name=row[0],
                type=row[1],
                nullable=row[2] == "YES",
                primary_key=row[3] == "PRI",
            )
            for row in cursor.fetchall()
        )

    def _foreign_keys(self, cursor, table: str) -> tuple[ForeignKey, ...]:
        cursor.execute(_FOREIGN_KEYS_SQL, (self._database, table))
        return tuple(
            ForeignKey(column=row[0], referenced_table=row[1], referenced_column=row[2])
            for row in cursor.fetchall()
        )

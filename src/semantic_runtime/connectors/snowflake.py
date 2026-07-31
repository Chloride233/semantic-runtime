"""Snowflake schema connector (requires the 'snowflake' extra).

Snowflake does not enforce foreign keys, so only tables and columns are
introspected; relationships must be declared in the semantic model.
"""

from __future__ import annotations

from semantic_runtime.connectors.schema import (
    ColumnSchema,
    DatabaseSchema,
    TableSchema,
)

_TABLES_SQL = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s AND table_type = 'BASE TABLE'
ORDER BY table_name
"""

_COLUMNS_SQL = """
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
ORDER BY ordinal_position
"""


class SnowflakeConnector:
    """Discovers the schema of a Snowflake database."""

    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        database: str,
        schema: str = "PUBLIC",
    ) -> None:
        self._account = account
        self._user = user
        self._password = password
        self._database = database
        self._schema = schema

    def load_schema(self) -> DatabaseSchema:
        try:
            import snowflake.connector
        except ImportError as exc:
            raise ImportError(
                "SnowflakeConnector requires the 'snowflake' extra: "
                "install 'semantic-runtime[snowflake]'"
            ) from exc

        connection = snowflake.connector.connect(
            account=self._account,
            user=self._user,
            password=self._password,
            database=self._database,
            schema=self._schema,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(_TABLES_SQL, (self._schema,))
                tables = tuple(
                    TableSchema(name=row[0], columns=self._columns(cursor, row[0]))
                    for row in cursor.fetchall()
                )
        finally:
            connection.close()
        return DatabaseSchema(tables=tables)

    def _columns(self, cursor, table: str) -> tuple[ColumnSchema, ...]:
        cursor.execute(_COLUMNS_SQL, (self._schema, table))
        return tuple(
            ColumnSchema(name=row[0], type=row[1], nullable=row[2] == "YES", primary_key=False)
            for row in cursor.fetchall()
        )

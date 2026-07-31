"""Connector protocol: schema discovery for database systems."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from semantic_runtime.connectors.schema import DatabaseSchema


@runtime_checkable
class SchemaConnector(Protocol):
    """Discovers a database schema without executing user queries."""

    def load_schema(self) -> DatabaseSchema:
        """Return the database schema as semantic structures."""
        ...

"""Schema mapping: database schemas into semantic models."""

from __future__ import annotations

from semantic_runtime.connectors.schema import DatabaseSchema
from semantic_runtime.loaders.yaml_loader import SemanticModel
from semantic_runtime.models import Entity, Relation


def map_schema(
    schema: DatabaseSchema,
    entity_type: str = "table",
    relation_type: str = "references",
) -> list[SemanticModel]:
    """Map a database schema to entities and reference relations."""
    models: list[SemanticModel] = []
    for table in schema.tables:
        models.append(
            Entity(
                id=table.name,
                type=entity_type,
                description=f"Database table {table.name!r}",
                properties={
                    "columns": [column.name for column in table.columns],
                    "primary_key": [column.name for column in table.columns if column.primary_key],
                },
            )
        )
    for table in schema.tables:
        for foreign_key in table.foreign_keys:
            models.append(
                Relation(
                    source=table.name,
                    target=foreign_key.referenced_table,
                    type=relation_type,
                    description=(
                        f"{table.name}.{foreign_key.column} references "
                        f"{foreign_key.referenced_table}.{foreign_key.referenced_column}"
                    ),
                    properties={
                        "column": foreign_key.column,
                        "referenced_column": foreign_key.referenced_column,
                    },
                )
            )
    return models

"""Schema model: a database schema as immutable structures."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ColumnSchema:
    """A column of a database table."""

    name: str
    type: str
    nullable: bool
    primary_key: bool


@dataclass(frozen=True, slots=True)
class ForeignKey:
    """A foreign key constraint from one table to another."""

    column: str
    referenced_table: str
    referenced_column: str


@dataclass(frozen=True, slots=True)
class TableSchema:
    """A database table with its columns and foreign keys."""

    name: str
    columns: tuple[ColumnSchema, ...] = ()
    foreign_keys: tuple[ForeignKey, ...] = ()


@dataclass(frozen=True, slots=True)
class DatabaseSchema:
    """A full database schema."""

    tables: tuple[TableSchema, ...] = field(default_factory=tuple)

    def table(self, name: str) -> TableSchema:
        for table in self.tables:
            if table.name == name:
                return table
        raise KeyError(f"table {name!r} not found in schema")

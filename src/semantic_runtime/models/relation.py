"""Relation model: describes how entities connect."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from semantic_runtime.models.entity import _validate_id
from semantic_runtime.models.exceptions import ModelValidationError


@dataclass(frozen=True, slots=True)
class Relation:
    """A typed connection between two entities."""

    source: str
    target: str
    type: str = "related_to"
    id: str | None = None
    description: str | None = None
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id("Relation", self.source)
        _validate_id("Relation", self.target)
        if not self.type or not self.type.strip():
            raise ModelValidationError("Relation", "type", "type must be a non-empty string")
        if self.id is None:
            object.__setattr__(self, "id", f"{self.source}:{self.type}:{self.target}")

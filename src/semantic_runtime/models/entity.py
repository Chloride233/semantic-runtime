"""Entity model: describes what exists in the business world."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from semantic_runtime.models.exceptions import ModelValidationError


def _validate_id(model: str, value: str) -> None:
    if not value or not value.strip():
        raise ModelValidationError(model, "id", "id must be a non-empty string")


@dataclass(frozen=True, slots=True)
class Entity:
    """A meaningful real-world business object."""

    id: str
    type: str
    name: str | None = None
    description: str | None = None
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id("Entity", self.id)
        if not self.type or not self.type.strip():
            raise ModelValidationError("Entity", "type", "type must be a non-empty string")

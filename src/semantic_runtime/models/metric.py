"""Metric model: describes business meaning of data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from semantic_runtime.models.entity import _validate_id
from semantic_runtime.models.exceptions import ModelValidationError


@dataclass(frozen=True, slots=True)
class Metric:
    """A business-level definition of a measurable concept."""

    id: str
    definition: str
    entity: str | None = None
    description: str | None = None
    unit: str | None = None
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id("Metric", self.id)
        if not self.definition or not self.definition.strip():
            raise ModelValidationError("Metric", "definition", "definition must be a non-empty string")
        if self.entity is not None:
            _validate_id("Metric", self.entity)

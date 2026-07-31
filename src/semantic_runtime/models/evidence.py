"""Evidence model: describes verification sources for conclusions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from semantic_runtime.models.entity import _validate_id
from semantic_runtime.models.exceptions import ModelValidationError

VALID_STATUSES = ("verified", "unverified", "expired")


@dataclass(frozen=True, slots=True)
class Evidence:
    """A traceable source that supports a conclusion."""

    id: str
    statement: str
    source: str
    status: str = "unverified"
    collected_at: datetime | None = None
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id("Evidence", self.id)
        if not self.statement or not self.statement.strip():
            raise ModelValidationError("Evidence", "statement", "statement must be a non-empty string")
        if not self.source or not self.source.strip():
            raise ModelValidationError("Evidence", "source", "source must be a non-empty string")
        if self.status not in VALID_STATUSES:
            raise ModelValidationError("Evidence", "status", f"status must be one of {VALID_STATUSES}")

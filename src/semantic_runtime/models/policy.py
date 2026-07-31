"""Policy model: describes rules that control access and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping

from semantic_runtime.models.entity import _validate_id
from semantic_runtime.models.exceptions import ModelValidationError

VALID_EFFECTS = ("allow", "deny")


@dataclass(frozen=True, slots=True)
class Policy:
    """A runtime rule governing an action."""

    id: str
    action: str
    effect: Literal["allow", "deny"] = "deny"
    rule: str | None = None
    description: str | None = None
    properties: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id("Policy", self.id)
        if not self.action or not self.action.strip():
            raise ModelValidationError("Policy", "action", "action must be a non-empty string")
        if self.effect not in VALID_EFFECTS:
            raise ModelValidationError("Policy", "effect", f"effect must be one of {VALID_EFFECTS}")

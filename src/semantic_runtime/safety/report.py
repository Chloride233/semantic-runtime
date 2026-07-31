"""Safety report structures for validation results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SafetyViolation:
    """A single safety violation with a stable code."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class SafetyReport:
    """Aggregated result of a safety check."""

    violations: list[SafetyViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations

    def __bool__(self) -> bool:
        return self.ok

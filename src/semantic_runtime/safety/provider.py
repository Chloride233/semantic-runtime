"""Safety provider interface: extension point for external safety engines.

Semantic Runtime checks operation safety through a SafetyProvider. The
built-in GuardrailSafetyProvider applies deterministic SQL guardrails;
external engines (e.g. a JoinLint adapter) implement the protocol to add
join validation, relationship safety, and execution guardrails.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from semantic_runtime.safety.report import SafetyReport
from semantic_runtime.safety.sql_guard import check_sql


@runtime_checkable
class SafetyProvider(Protocol):
    """Checks whether an operation is safe before execution."""

    def check_operation(self, action: str, sql: str | None) -> SafetyReport:
        """Return violations found for the operation; empty means safe."""
        ...


class GuardrailSafetyProvider:
    """Built-in provider: deterministic SQL guardrails."""

    def check_operation(self, action: str, sql: str | None) -> SafetyReport:
        if sql is None:
            return SafetyReport()
        return check_sql(sql)

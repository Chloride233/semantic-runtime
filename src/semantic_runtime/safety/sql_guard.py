"""SQL guardrails: deterministic checks without executing statements."""

from __future__ import annotations

import re

from semantic_runtime.safety.report import SafetyReport, SafetyViolation

_STATEMENT_SPLIT = re.compile(r";")
_STATEMENT_END = re.compile(r";\s*$")
_UPDATE_PATTERN = re.compile(r"^\s*update\s+[^\s;]+\s", re.IGNORECASE)
_DELETE_PATTERN = re.compile(r"^\s*delete\s+from\s+[^\s;]+", re.IGNORECASE)
_HAS_WHERE = re.compile(r"\bwhere\b", re.IGNORECASE)
_COMMENT_PATTERN = re.compile(r"(--.*$)|(/\*.*?\*/)", re.IGNORECASE | re.DOTALL | re.MULTILINE)


def check_sql(statement: str) -> SafetyReport:
    """Inspect a SQL statement for unsafe patterns. Never executes SQL."""
    violations: list[SafetyViolation] = []
    stripped = _COMMENT_PATTERN.sub("", statement)

    if not stripped.strip():
        return SafetyReport()

    body = _STATEMENT_END.sub("", stripped.strip())
    if _STATEMENT_SPLIT.search(body):
        violations.append(
            SafetyViolation("UNSAFE_MULTI_STATEMENT", "multiple SQL statements are not allowed")
        )
        body = _STATEMENT_SPLIT.split(body, maxsplit=1)[0]

    if _UPDATE_PATTERN.match(body) and not _HAS_WHERE.search(body):
        violations.append(
            SafetyViolation("UNSAFE_UPDATE_NO_WHERE", "UPDATE without a WHERE clause is not allowed")
        )

    if _DELETE_PATTERN.match(body) and not _HAS_WHERE.search(body):
        violations.append(
            SafetyViolation("UNSAFE_DELETE_NO_WHERE", "DELETE without a WHERE clause is not allowed")
        )

    return SafetyReport(violations=violations)

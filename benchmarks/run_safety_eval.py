"""Level 4 safety evaluation: detection rate and false positive rate.

Scenario categories:
- wrong joins: relations referencing missing entities
- wrong metrics: metrics referencing missing entities or metrics
- invalid relationships: model integrity violations
- permission violations: unallowed actions, deny policies, unsafe SQL

Usage:
    python benchmarks/run_safety_eval.py
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.loaders import loads
from semantic_runtime.packs import load_pack

SCENARIOS = [
    ("wrong-join-target", "wrong joins", """relations:
  - source: customer
    target: ghost
    type: places
""", None, None, False),
    ("wrong-join-source", "wrong joins", """relations:
  - source: ghost
    target: order
    type: places
""", None, None, False),
    ("wrong-metric-entity", "wrong metrics", """metrics:
  - id: bad_revenue
    definition: completed payment minus refunds
    entity: ghost
""", None, None, False),
    ("wrong-metric-dependency", "wrong metrics", """metrics:
  - id: margin
    definition: revenue ratio
    entity: order
    depends_on: [ghost]
""", None, None, False),
    ("action-without-policy", "permission violations", "", "runtime.delete", None, False),
    ("deny-policy", "permission violations", "", "runtime.mutate", None, False),
    ("unsafe-sql-multi", "permission violations", "", "runtime.query", "SELECT * FROM orders; DROP TABLE orders", False),
    ("unsafe-sql-delete", "permission violations", "", "runtime.query", "DELETE FROM orders", False),
    ("allowed-query", "allowed operations", "", "runtime.query", None, True),
    ("safe-sql-select", "allowed operations", "", "runtime.query", "SELECT * FROM orders WHERE id = 1", True),
    ("safe-model", "allowed operations", "", None, None, True),
]


@dataclass(frozen=True, slots=True)
class SafetyScenario:
    name: str
    category: str
    extra_yaml: str
    action: str | None
    sql: str | None
    expect_safe: bool


@dataclass(frozen=True, slots=True)
class SafetyEvalResult:
    detected: int = 0
    missed: int = 0
    false_positives: int = 0
    correct_rejections: int = 0

    @property
    def detection_rate(self) -> float:
        total = self.detected + self.missed
        return self.detected / total if total else 0.0

    @property
    def false_positive_rate(self) -> float:
        total = self.false_positives + self.correct_rejections
        return self.false_positives / total if total else 0.0

    @property
    def accuracy(self) -> float:
        total = self.detected + self.missed + self.false_positives + self.correct_rejections
        return (self.detected + self.correct_rejections) / total if total else 0.0


def evaluate(scenarios: list[SafetyScenario]) -> SafetyEvalResult:
    detected = missed = false_positives = correct_rejections = 0
    for scenario in scenarios:
        safe = _is_safe(scenario)
        if scenario.expect_safe and safe:
            correct_rejections += 1
        elif scenario.expect_safe and not safe:
            false_positives += 1
        elif not scenario.expect_safe and not safe:
            detected += 1
        else:
            missed += 1
    return SafetyEvalResult(
        detected=detected,
        missed=missed,
        false_positives=false_positives,
        correct_rejections=correct_rejections,
    )


def _is_safe(scenario: SafetyScenario) -> bool:
    base = load_pack("ecommerce")
    models = base + loads(scenario.extra_yaml) if scenario.extra_yaml else base
    runtime = SemanticRuntime(models)
    model_report = runtime.validate_model()
    if not model_report.ok:
        return False
    if scenario.action is None:
        return True
    return runtime.validate(scenario.action, scenario.sql).allow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Semantic Runtime Level 4 safety evaluation")
    parser.parse_args(argv)

    scenarios = [SafetyScenario(*row) for row in SCENARIOS]
    result = evaluate(scenarios)

    print("Level 4 safety evaluation")
    print(f"  detection rate:      {result.detection_rate:.3f} "
          f"({result.detected}/{result.detected + result.missed})")
    print(f"  false positive rate: {result.false_positive_rate:.3f} "
          f"({result.false_positives}/{result.false_positives + result.correct_rejections})")
    print(f"  accuracy:            {result.accuracy:.3f}")
    return 0 if result.false_positives == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

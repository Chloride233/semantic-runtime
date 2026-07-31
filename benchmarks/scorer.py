"""Scoring functions for Semantic Runtime benchmarks.

Pure functions – no I/O, no side effects. Takes domain data + runtime in,
produces scores out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from semantic_runtime.core import SemanticRuntime

SRB_WEIGHTS: dict[str, float] = {
    "semantic_understanding": 0.25,
    "entity_discovery": 0.20,
    "relationship_reasoning": 0.20,
    "metric_dependency": 0.15,
    "evidence_grounding": 0.10,
}


def _f1(predicted: set[str], expected: set[str]) -> float:
    if not expected:
        return 1.0 if not predicted else 0.0
    if not predicted:
        return 0.0
    common = predicted & expected
    precision = len(common) / len(predicted)
    recall = len(common) / len(expected)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


@dataclass(frozen=True, slots=True)
class QuestionScore:
    question_id: str
    type: str
    scores: dict[str, float]

    @property
    def f1(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)


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


@dataclass(frozen=True, slots=True)
class DomainResult:
    domain: str
    questions: list[QuestionScore] = field(default_factory=list)
    safety: SafetyEvalResult | None = None

    def average_by_type(self, question_type: str) -> float:
        scores = [q.f1 for q in self.questions if q.type == question_type]
        return sum(scores) / len(scores) if scores else 0.0

    def _type_scores(self) -> dict[str, float]:
        types = sorted({q.type for q in self.questions})
        return {t: self.average_by_type(t) for t in types if t != "safety_validation"}

    def srb(self) -> float:
        types = self._type_scores()
        if not types or all(t not in SRB_WEIGHTS for t in types):
            return 0.0
        weighted = sum(
            SRB_WEIGHTS.get(t, 0.0) * score
            for t, score in types.items()
        )
        safety = self.average_by_type("safety_validation")
        if safety == 0.0 and self.safety is not None:
            safety = 1.0 if self.safety.false_positives == 0 else 0.0
        safety_factor = 1.0 if safety >= 1.0 else 0.0
        return weighted * safety_factor

    def check_thresholds(self, thresholds: dict[str, float]) -> dict[str, bool]:
        return {
            t: self.average_by_type(t) >= thresholds.get(t, 0.0)
            for t in sorted({q.type for q in self.questions})
        }


def score_context_question(
    question_id: str,
    question_type: str,
    text: str,
    runtime: SemanticRuntime,
    expected: dict[str, set[str]],
    categories: tuple[str, ...],
) -> QuestionScore:
    context = runtime.resolve_context(text)
    predicted = {
        "entities": {e.id for e in context.entities},
        "relations": {r.id for r in context.relations},
        "metrics": {m.id for m in context.metrics},
        "evidences": {e.id for e in context.evidences},
    }
    scores = {
        cat: _f1(predicted.get(cat, set()), expected.get(cat, set()))
        for cat in categories
    }
    return QuestionScore(question_id=question_id, type=question_type, scores=scores)


def score_metric_dependency_question(
    question_id: str,
    runtime: SemanticRuntime,
    query_metrics: set[str],
    expected_direct: set[str],
    expected_transitive: set[str],
) -> QuestionScore:
    resolved = _resolve_metric_deps(runtime, query_metrics)
    direct_f1 = _f1(resolved, expected_direct)
    transitive_f1 = _f1(resolved, expected_transitive)
    scores = {
        "direct_dependency": direct_f1,
        "transitive_dependency": transitive_f1,
    }
    return QuestionScore(question_id=question_id, type="metric_dependency", scores=scores)


def _resolve_metric_deps(runtime: SemanticRuntime, metric_ids: set[str]) -> set[str]:
    resolved: set[str] = set()
    for mid in metric_ids:
        try:
            deps = runtime.metric_dependencies(mid)
            resolved.update(d.id for d in deps)
        except Exception:
            continue
    return resolved


def score_safety_question(
    question_id: str,
    runtime: SemanticRuntime,
    action: str,
    sql: str | None,
    expect_safe: bool,
) -> QuestionScore:
    try:
        decision = runtime.validate(action, sql)
        safe = decision.allow
    except Exception:
        safe = False
    correct = safe == expect_safe
    scores = {"correct": 1.0 if correct else 0.0}
    return QuestionScore(question_id=question_id, type="safety_validation", scores=scores)


def evaluate_safety_scenarios(
    base_models: list,
    scenarios: list[dict],
) -> SafetyEvalResult:
    detected = missed = false_positives = correct_rejections = 0
    for sc in scenarios:
        safe = _evaluate_single_safety(base_models, sc)
        if sc["expect_safe"] and safe:
            correct_rejections += 1
        elif sc["expect_safe"] and not safe:
            false_positives += 1
        elif not sc["expect_safe"] and not safe:
            detected += 1
        else:
            missed += 1
    return SafetyEvalResult(
        detected=detected,
        missed=missed,
        false_positives=false_positives,
        correct_rejections=correct_rejections,
    )


def _evaluate_single_safety(
    base_models: list,
    sc: dict,
) -> bool:
    if sc.get("extra_yaml"):
        from semantic_runtime.loaders import loads

        extra_models = loads(sc["extra_yaml"])
        models = base_models + extra_models
    else:
        models = base_models
    from semantic_runtime.core import SemanticRuntime

    runtime = SemanticRuntime(models)
    model_report = runtime.validate_model()
    if not model_report.ok:
        return False
    action = sc.get("action")
    if action is None:
        return True
    return runtime.validate(action, sc.get("sql")).allow

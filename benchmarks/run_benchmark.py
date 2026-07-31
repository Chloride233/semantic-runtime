"""Phase 6 benchmark: semantic capability evaluation per domain.

Each benchmark domain directory contains:
- model.yaml           the semantic model under evaluation
- questions.json       questions with type tags
- expected_context.json expected entities/relations/metrics/evidences per question
- evaluation.json      categories, metrics, and per-type thresholds

Question types (from the post-v0.1 roadmap):
- semantic_understanding
- relationship_reasoning
- business_analysis

Usage:
    python benchmarks/run_benchmark.py [--domain ecommerce]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.loaders import load

BENCHMARKS = Path(__file__).resolve().parent

QUESTION_TYPES = ("semantic_understanding", "relationship_reasoning", "business_analysis")


@dataclass(frozen=True, slots=True)
class QuestionScore:
    question_id: str
    type: str
    scores: dict[str, float]

    @property
    def f1(self) -> float:
        return self.scores["f1"]


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    questions: list[QuestionScore] = field(default_factory=list)

    def average_by_type(self, question_type: str) -> float:
        f1s = [q.f1 for q in self.questions if q.type == question_type]
        return sum(f1s) / len(f1s) if f1s else 0.0

    def overall(self) -> float:
        f1s = [q.f1 for q in self.questions]
        return sum(f1s) / len(f1s) if f1s else 0.0


def run_domain(domain: str) -> tuple[BenchmarkResult, dict]:
    domain_dir = BENCHMARKS / domain
    questions_doc = json.loads((domain_dir / "questions.json").read_text(encoding="utf-8"))
    expected_doc = json.loads((domain_dir / "expected_context.json").read_text(encoding="utf-8"))
    evaluation = json.loads((domain_dir / "evaluation.json").read_text(encoding="utf-8"))
    categories = tuple(evaluation["categories"])

    runtime = SemanticRuntime(load(domain_dir / "model.yaml"))

    questions: list[QuestionScore] = []
    for entry in questions_doc["questions"]:
        question_id = entry["id"]
        context = runtime.resolve_context(entry["text"])
        predicted = {
            "entities": {e.id for e in context.entities},
            "relations": {r.id for r in context.relations},
            "metrics": {m.id for m in context.metrics},
            "evidences": {e.id for e in context.evidences},
        }
        expected = {category: set(expected_doc[question_id].get(category, [])) for category in categories}
        scores = {category: _f1(predicted[category], expected[category]) for category in categories}
        scores["f1"] = scores["entities"] + scores["relations"] + scores["metrics"] + scores["evidences"]
        scores["f1"] /= 4
        questions.append(QuestionScore(question_id=question_id, type=entry["type"], scores=scores))

    return BenchmarkResult(questions=questions), evaluation


def _f1(predicted: set[str], expected: set[str]) -> float:
    if not expected:
        return 1.0 if not predicted else 0.0
    if not predicted:
        return 0.0
    true_positive = len(predicted & expected)
    precision = true_positive / len(predicted)
    recall = true_positive / len(expected)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Semantic Runtime Phase 6 benchmark")
    parser.add_argument("--domain", default="ecommerce")
    args = parser.parse_args(argv)

    result, evaluation = run_domain(args.domain)
    print(f"Phase 6 benchmark: {args.domain}")
    for question in result.questions:
        print(f"  [{question.type}] {question.question_id}: f1={question.f1:.3f}")

    print("by type:")
    passed = True
    for question_type in QUESTION_TYPES:
        average = result.average_by_type(question_type)
        threshold = evaluation["thresholds"].get(question_type, 0.0)
        status = "PASS" if average >= threshold else "FAIL"
        if status == "FAIL":
            passed = False
        print(f"  {question_type}: {average:.3f} (threshold {threshold}) {status}")

    overall = result.overall()
    print(f"overall f1: {overall:.3f}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

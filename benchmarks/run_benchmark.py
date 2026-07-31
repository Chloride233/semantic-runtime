"""Level 2 benchmark: semantic capability evaluation against gold sets.

Evaluates entity retrieval, relation retrieval, and metric understanding
with precision / recall / F1 per question and per category.

Usage:
    python benchmarks/run_benchmark.py [--domain ecommerce]
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.packs import load_pack

BENCHMARKS = Path(__file__).resolve().parent

CATEGORIES = ("entities", "relations", "metrics", "evidences")


@dataclass(frozen=True, slots=True)
class QuestionScore:
    question: str
    scores: dict[str, float]

    def __str__(self) -> str:
        parts = "  ".join(f"{k}: {v:.3f}" for k, v in self.scores.items())
        return f"  {self.question}\n    {parts}"


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    questions: list[QuestionScore] = field(default_factory=list)

    def average(self, category: str) -> float:
        values = [q.scores[category] for q in self.questions]
        return sum(values) / len(values) if values else 0.0


def run_domain(domain: str) -> BenchmarkResult:
    gold_path = BENCHMARKS / domain / "gold.yaml"
    if not gold_path.is_file():
        raise FileNotFoundError(f"no gold set found at {gold_path}")

    document = yaml.safe_load(gold_path.read_text(encoding="utf-8"))
    runtime = SemanticRuntime(load_pack(domain))

    questions: list[QuestionScore] = []
    for entry in document["questions"]:
        context = runtime.resolve_context(entry["question"])
        predicted = {
            "entities": {e.id for e in context.entities},
            "relations": {r.id for r in context.relations},
            "metrics": {m.id for m in context.metrics},
            "evidences": {e.id for e in context.evidences},
        }
        expected = {
            category: set(entry.get(category, [])) for category in CATEGORIES
        }
        questions.append(
            QuestionScore(
                question=entry["question"],
                scores={
                    category: _f1(predicted[category], expected[category])
                    for category in CATEGORIES
                },
            )
        )
    return BenchmarkResult(questions=questions)


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
    parser = argparse.ArgumentParser(description="Semantic Runtime Level 2 benchmark")
    parser.add_argument("--domain", default="ecommerce")
    args = parser.parse_args(argv)

    result = run_domain(args.domain)
    print(f"Level 2 benchmark: {args.domain}")
    for question in result.questions:
        print(question)
    print("averages:")
    for category in CATEGORIES:
        print(f"  {category}: {result.average(category):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

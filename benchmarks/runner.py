"""Unified benchmark runner (v0.2).

Usage:
    python benchmarks/runner.py --domain ecommerce
    python benchmarks/runner.py --domain ecommerce --type metric_dependency
    python benchmarks/runner.py --domain ecommerce --safety
    python benchmarks/runner.py --domain ecommerce --output report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_SRC = str(_REPO_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from benchmarks.report import render_report, write_json_report  # noqa: E402
from benchmarks.scorer import (  # noqa: E402
    DomainResult,
    SafetyEvalResult,
    evaluate_safety_scenarios,
    score_context_question,
    score_metric_dependency_question,
    score_safety_question,
)
from semantic_runtime.core import SemanticRuntime  # noqa: E402
from semantic_runtime.loaders import load  # noqa: E402
from semantic_runtime.packs import load_pack  # noqa: E402

BENCHMARKS = Path(__file__).resolve().parent
CATEGORIES = ("entities", "relations", "metrics", "evidences")

CONTEXT_TYPES = frozenset(
    {
        "semantic_understanding",
        "entity_discovery",
        "relationship_reasoning",
        "evidence_grounding",
    }
)


def load_json_or_empty(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def run_domain(
    domain: str,
    types: set[str] | None = None,
    with_safety: bool = True,
) -> DomainResult:
    domain_dir = BENCHMARKS / domain

    questions_doc = load_json_or_empty(domain_dir / "questions.json")
    expected_context = load_json_or_empty(domain_dir / "expected_context.json")
    expected_metrics = load_json_or_empty(domain_dir / "expected_metrics.json")
    safety_doc = load_json_or_empty(domain_dir / "safety_scenarios.json")

    model_path = domain_dir / "model.yaml"
    models = load(model_path) if model_path.is_file() else load_pack(domain)
    runtime = SemanticRuntime(models)

    scored = []
    for entry in questions_doc.get("questions", []):
        question_type = entry["type"]
        if types is not None and question_type not in types:
            continue

        question_id = entry["id"]

        if question_type in CONTEXT_TYPES:
            expected = {
                cat: set(expected_context.get(question_id, {}).get(cat, []))
                for cat in CATEGORIES
            }
            scored.append(
                score_context_question(
                    question_id,
                    question_type,
                    entry["text"],
                    runtime,
                    expected,
                    CATEGORIES,
                )
            )
        elif question_type == "metric_dependency":
            em = expected_metrics.get(question_id, {})
            scored.append(
                score_metric_dependency_question(
                    question_id,
                    runtime,
                    query_metrics={em.get("metric_id", "")} - {""},
                    expected_direct=set(em.get("direct_dependencies", [])),
                    expected_transitive=set(em.get("transitive_dependencies", [])),
                )
            )
        elif question_type == "safety_validation":
            val = entry.get("validate", {})
            scored.append(
                score_safety_question(
                    question_id,
                    runtime,
                    action=val.get("action", ""),
                    sql=val.get("sql"),
                    expect_safe=val.get("expect_safe", True),
                )
            )

    safety: SafetyEvalResult | None = None
    if with_safety:
        scenarios = safety_doc.get("scenarios", [])
        if scenarios:
            safety = evaluate_safety_scenarios(models, scenarios)

    return DomainResult(domain=domain, questions=scored, safety=safety)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Semantic Runtime benchmark runner (v0.2)")
    parser.add_argument("--domain", default="ecommerce", help="benchmark domain directory")
    parser.add_argument("--type", help="run only one question type (e.g. metric_dependency)")
    parser.add_argument("--safety", action="store_true", help="run only safety evaluation")
    parser.add_argument("--output", help="write JSON report to this path")
    args = parser.parse_args(argv)

    domain_dir = BENCHMARKS / args.domain
    if not domain_dir.is_dir():
        print(f"error: domain directory not found: {domain_dir}", file=sys.stderr)
        return 2

    evaluation = load_json_or_empty(domain_dir / "evaluation.json")
    thresholds = evaluation.get("thresholds", {})

    if args.safety:
        filter_types: set[str] | None = {"safety_validation"}
        run_safety = True
    else:
        filter_types = {args.type} if args.type else None
        run_safety = args.type is None

    result = run_domain(args.domain, types=filter_types, with_safety=run_safety)

    report = render_report(result, thresholds)
    print(report)

    if args.output:
        write_json_report(result, args.output)
        print(f"\nwrote {args.output}")

    if result.safety is not None and result.safety.false_positives > 0:
        return 1
    checks = result.check_thresholds(thresholds)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

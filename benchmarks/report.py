"""Benchmark reporting: human-readable summary and JSON reports."""

from __future__ import annotations

import json
from pathlib import Path

from benchmarks.scorer import DomainResult, SafetyEvalResult

TYPE_LABELS = {
    "semantic_understanding": "Semantic Understanding",
    "entity_discovery": "Entity Discovery",
    "relationship_reasoning": "Relationship Reasoning",
    "metric_dependency": "Metric Dependency",
    "evidence_grounding": "Evidence Grounding",
    "safety_validation": "Safety Validation",
}


def render_report(domain_result: DomainResult, thresholds: dict[str, float]) -> str:
    lines = [f"Benchmark report: {domain_result.domain}", ""]
    for question in domain_result.questions:
        label = TYPE_LABELS.get(question.type, question.type)
        lines.append(f"  [{label}] {question.question_id}: f1={question.f1:.3f}")

    lines.append("")
    lines.append("by type:")
    passed = True
    for question_type in sorted({q.type for q in domain_result.questions}):
        average = domain_result.average_by_type(question_type)
        threshold = thresholds.get(question_type, 0.0)
        status = "PASS" if average >= threshold else "FAIL"
        passed = passed and status == "PASS"
        lines.append(
            f"  {TYPE_LABELS.get(question_type, question_type)}: "
            f"{average:.3f} (threshold {threshold}) {status}"
        )

    safety = domain_result.safety
    if safety is not None:
        lines.append("")
        lines.append(
            f"safety: detection={safety.detection_rate:.3f} "
            f"false_positive={safety.false_positive_rate:.3f} "
            f"accuracy={safety.accuracy:.3f}"
        )

    lines.append("")
    lines.append(f"SRB score: {domain_result.srb():.3f}")
    lines.append(f"result: {'PASS' if passed else 'FAIL'}")
    return "\n".join(lines)


def write_json_report(domain_result: DomainResult, path: str | Path) -> None:
    payload = {
        "domain": domain_result.domain,
        "questions": [
            {
                "id": q.question_id,
                "type": q.type,
                "scores": q.scores,
                "f1": q.f1,
            }
            for q in domain_result.questions
        ],
        "by_type": {
            question_type: domain_result.average_by_type(question_type)
            for question_type in sorted({q.type for q in domain_result.questions})
        },
        "srb": domain_result.srb(),
    }
    if domain_result.safety is not None:
        safety: SafetyEvalResult = domain_result.safety
        payload["safety"] = {
            "detection_rate": safety.detection_rate,
            "false_positive_rate": safety.false_positive_rate,
            "accuracy": safety.accuracy,
        }
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

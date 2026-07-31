"""Model integrity validation: relationships must resolve."""

from __future__ import annotations

from collections.abc import Iterable

from semantic_runtime.loaders.yaml_loader import SemanticModel
from semantic_runtime.models import Entity, Metric, Relation
from semantic_runtime.safety.report import SafetyReport, SafetyViolation


def validate_model(models: Iterable[SemanticModel]) -> SafetyReport:
    """Check that every relation and metric reference an existing entity."""
    violations: list[SafetyViolation] = []
    entities = {model.id for model in models if isinstance(model, Entity)}
    metrics = {model.id for model in models if isinstance(model, Metric)}
    relations = [model for model in models if isinstance(model, Relation)]

    for relation in relations:
        if relation.source not in entities:
            violations.append(
                SafetyViolation(
                    "RELATION_SOURCE_MISSING",
                    f"relation {relation.id!r} references missing source entity {relation.source!r}",
                )
            )
        if relation.target not in entities:
            violations.append(
                SafetyViolation(
                    "RELATION_TARGET_MISSING",
                    f"relation {relation.id!r} references missing target entity {relation.target!r}",
                )
            )

    for metric in metrics:
        metric_model = next(m for m in models if isinstance(m, Metric) and m.id == metric)
        if metric_model.entity is not None and metric_model.entity not in entities:
            violations.append(
                SafetyViolation(
                    "METRIC_ENTITY_MISSING",
                    f"metric {metric!r} references missing entity {metric_model.entity!r}",
                )
            )
        for dependency in metric_model.depends_on:
            if dependency not in metrics:
                violations.append(
                    SafetyViolation(
                        "METRIC_DEPENDENCY_MISSING",
                        f"metric {metric!r} depends on missing metric {dependency!r}",
                    )
                )

    return SafetyReport(violations=violations)

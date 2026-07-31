"""YAML semantic model loading, validation, and runtime object creation."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import yaml

from semantic_runtime.models import (
    Entity,
    Evidence,
    Metric,
    ModelError,
    Policy,
    Relation,
)
from semantic_runtime.models.exceptions import ModelValidationError

SemanticModel = Union[Entity, Relation, Metric, Evidence, Policy]

KIND_TO_MODEL = {
    "entity": Entity,
    "relation": Relation,
    "metric": Metric,
    "evidence": Evidence,
    "policy": Policy,
}

PLURAL_TO_KIND = {
    "entities": "entity",
    "relations": "relation",
    "metrics": "metric",
    "evidences": "evidence",
    "policies": "policy",
}

VALID_KINDS = sorted(KIND_TO_MODEL)


class ModelLoadError(ModelError):
    """Raised when a semantic model document cannot be loaded."""


def loads(text: str) -> list[SemanticModel]:
    """Parse YAML text into validated semantic model objects."""
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ModelLoadError(f"invalid YAML: {exc}") from exc

    if document is None:
        return []

    if not isinstance(document, dict):
        raise ModelLoadError(f"expected a mapping at the top level, got {type(document).__name__}")

    models: list[SemanticModel] = []
    for key, payload in document.items():
        kind = PLURAL_TO_KIND.get(key)
        if kind is None and key not in KIND_TO_MODEL:
            raise ModelLoadError(f"unknown model kind {key!r}; expected one of {VALID_KINDS}")
        if kind is None:
            kind = key

        entries = payload if isinstance(payload, list) else [payload]
        for entry in entries:
            if not isinstance(entry, dict):
                raise ModelLoadError(f"{key}: expected a mapping per model, got {type(entry).__name__}")
            models.append(_build(kind, entry))
    return models


def load(path: str | Path) -> list[SemanticModel]:
    """Load semantic models from a YAML file."""
    return loads(Path(path).read_text(encoding="utf-8"))


def _build(kind: str, data: dict) -> SemanticModel:
    model_cls = KIND_TO_MODEL[kind]
    try:
        return model_cls(**data)
    except TypeError as exc:
        raise ModelLoadError(f"{kind}: unexpected field or missing required field: {exc}") from exc
    except ModelValidationError as exc:
        raise ModelLoadError(str(exc)) from exc

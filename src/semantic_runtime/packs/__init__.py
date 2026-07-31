"""Semantic packs: built-in domain semantic models."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from semantic_runtime.loaders import load
from semantic_runtime.loaders.yaml_loader import SemanticModel

PACKS = ("ecommerce", "saas", "finance", "game", "healthcare")


class PackNotFoundError(ValueError):
    """Raised when a requested semantic pack does not exist."""


def load_pack(name: str, base_dir: str | Path | None = None) -> list[SemanticModel]:
    """Load a semantic pack from package data or a local directory."""
    if base_dir is not None:
        return _load_from(base_dir, name)

    if name not in PACKS:
        raise PackNotFoundError(
            f"unknown semantic pack {name!r}; available packs: {', '.join(PACKS)}"
        )
    path = resources.files("semantic_runtime.packs").joinpath(name, "semantic_model.yaml")
    return load(path)


def pack_path(name: str) -> Path:
    """Absolute path of a built-in pack's semantic model file."""
    if name not in PACKS:
        raise PackNotFoundError(
            f"unknown semantic pack {name!r}; available packs: {', '.join(PACKS)}"
        )
    return Path(resources.files("semantic_runtime.packs").joinpath(name, "semantic_model.yaml"))


def _load_from(base_dir: str | Path, name: str) -> list[SemanticModel]:
    base = Path(base_dir)
    candidates = [base / f"{name}.yaml", base / name / "semantic_model.yaml"]
    for candidate in candidates:
        if candidate.is_file():
            return load(candidate)
    raise PackNotFoundError(f"no semantic pack {name!r} found under {base}")
